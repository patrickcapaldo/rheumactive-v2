#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import socket
import json
import base64
from pathlib import Path

from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.pose_estimation.pose_estimation_pipeline import GStreamerPoseEstimationApp

# --- Configuration ---
TCP_IP = '127.0.0.1'
TCP_PORT = 5001
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# --- Globals ---
sock = None

# --- COCO Keypoints and Skeleton ---
KEYPOINTS = {
    'nose': 0, 'left_eye': 1, 'right_eye': 2, 'left_ear': 3, 'right_ear': 4,
    'left_shoulder': 5, 'right_shoulder': 6, 'left_elbow': 7, 'right_elbow': 8,
    'left_wrist': 9, 'right_wrist': 10, 'left_hip': 11, 'right_hip': 12,
    'left_knee': 13, 'right_knee': 14, 'left_ankle': 15, 'right_ankle': 16,
}

SKELETON = [
    (KEYPOINTS['left_shoulder'], KEYPOINTS['right_shoulder']),
    (KEYPOINTS['left_hip'], KEYPOINTS['right_hip']),
    (KEYPOINTS['left_shoulder'], KEYPOINTS['left_hip']),
    (KEYPOINTS['right_shoulder'], KEYPOINTS['right_hip']),
    (KEYPOINTS['left_shoulder'], KEYPOINTS['left_elbow']),
    (KEYPOINTS['right_shoulder'], KEYPOINTS['right_elbow']),
    (KEYPOINTS['left_elbow'], KEYPOINTS['left_wrist']),
    (KEYPOINTS['right_elbow'], KEYPOINTS['right_wrist']),
    (KEYPOINTS['left_hip'], KEYPOINTS['left_knee']),
    (KEYPOINTS['right_hip'], KEYPOINTS['right_knee']),
    (KEYPOINTS['left_knee'], KEYPOINTS['left_ankle']),
    (KEYPOINTS['right_knee'], KEYPOINTS['right_ankle']),
]

# --- User-defined Callback Class ---
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()

# --- Helper Functions ---
def get_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_product == 0: return 0.0
    cosine_angle = np.clip(dot_product / norm_product, -1.0, 1.0)
    return np.degrees(np.arccos(cosine_angle))

def draw_pose(frame, keypoints_with_scores, confidence_threshold=0.5):
    # Draw keypoints
    for i, point in enumerate(keypoints_with_scores):
        if point[2] > confidence_threshold:
            cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

    # Draw skeleton
    for p1_idx, p2_idx in SKELETON:
        if keypoints_with_scores[p1_idx][2] > confidence_threshold and keypoints_with_scores[p2_idx][2] > confidence_threshold:
            p1 = (int(keypoints_with_scores[p1_idx][0]), int(keypoints_with_scores[p1_idx][1]))
            p2 = (int(keypoints_with_scores[p2_idx][0]), int(keypoints_with_scores[p2_idx][1]))
            cv2.line(frame, p1, p2, (255, 0, 0), 2)

import sys
from hailo_apps.hailo_app_python.core.common.core import get_default_parser

# --- GStreamer Callback ---
def app_callback(pad, info, user_data):
    global sock
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    format, width, height = get_caps_from_pad(pad)
    print(f"app_callback: format={format}, width={width}, height={height}") # DEBUG
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        frame = get_numpy_from_buffer(buffer, format, width, height)
        print(f"app_callback: Frame captured, frame is None: {frame is None}") # DEBUG
    else:
        print("app_callback: user_data.use_frame is false or format/width/height is None") # DEBUG

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    current_angle = 0.0
    all_keypoints = np.zeros((17, 3), dtype=np.float32)

    for detection in detections:
        if detection.get_label() == "person":
            landmarks = detection.get_objects_typed(hailo.HAILO_LANDMARKS)
            if len(landmarks) != 0:
                points = landmarks[0].get_points()
                bbox = detection.get_bbox()
                for i in range(len(points)):
                    x = int((points[i].x() * bbox.width() + bbox.xmin()) * width)
                    y = int((points[i].y() * bbox.height() + bbox.ymin()) * height)
                    # Assuming the model provides confidence, if not, we default to 1.0
                    confidence = points[i].confidence() if hasattr(points[i], 'confidence') else 1.0
                    all_keypoints[i] = [x, y, confidence]

                # Calculate angle (example: left elbow)
                p1 = all_keypoints[KEYPOINTS['left_shoulder'], :2]
                p2 = all_keypoints[KEYPOINTS['left_elbow'], :2]
                p3 = all_keypoints[KEYPOINTS['left_wrist'], :2]
                current_angle = get_angle(p1, p2, p3)

                if frame is not None:
                    draw_pose(frame, all_keypoints)
                    cv2.putText(frame, f"Angle: {current_angle:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    if frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.jpg', frame)
        encoded_frame = base64.b64encode(buffer).decode('utf-8')

        data = {
            "image": encoded_frame,
            "angle": round(current_angle, 1)
        }
        json_data = json.dumps(data)
        
        try:
            message_length = len(json_data.encode('utf-8'))
            sock.sendall(message_length.to_bytes(4, 'big'))
            sock.sendall(json_data.encode('utf-8'))
            print("Sent frame to Flask app") # DEBUG
        except Exception as e:
            print(f"Error sending data: {e}")
            return Gst.PadProbeReturn.DROP # Stop pipeline if socket fails

    else:
        print("app_callback: Frame is None, not sending to Flask app") # DEBUG

    return Gst.PadProbeReturn.OK

from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_helper_pipelines import (
    SOURCE_PIPELINE, 
    INFERENCE_PIPELINE, 
    INFERENCE_PIPELINE_WRAPPER, 
    TRACKER_PIPELINE, 
    USER_CALLBACK_PIPELINE
)

# --- Headless GStreamer App ---
class HeadlessGStreamerPoseEstimationApp(GStreamerPoseEstimationApp):
    def get_pipeline_string(self):
        source_pipeline = SOURCE_PIPELINE(video_source=self.video_source,
                                          video_width=self.video_width, video_height=self.video_height,
                                          frame_rate=self.frame_rate, sync=self.sync)
        infer_pipeline = INFERENCE_PIPELINE(
            hef_path=self.hef_path,
            post_process_so=self.post_process_so,
            post_function_name=self.post_process_function,
            batch_size=self.batch_size
        )
        infer_pipeline_wrapper = INFERENCE_PIPELINE_WRAPPER(infer_pipeline)
        tracker_pipeline = TRACKER_PIPELINE(class_id=0)
        user_callback_pipeline = USER_CALLBACK_PIPELINE()

        pipeline_string = (
            f'{source_pipeline} !'
            f'{infer_pipeline_wrapper} ! '
            f'{tracker_pipeline} ! '
            f'{user_callback_pipeline} ! '
            f'fakesink'
        )
        print(pipeline_string)
        return pipeline_string

# --- Main Streamer Logic ---
def main():
    global sock
    print(f"Camera Streamer starting. Connecting to {TCP_IP}:{TCP_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((TCP_IP, TCP_PORT))
        print("Connected to Flask app.")

        project_root = Path(__file__).resolve().parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            os.environ["HAILO_ENV_FILE"] = str(env_file)
            print(f"Using environment file: {env_file}")
        else:
            print("Warning: .env file not found. Hailo App might not run correctly.")

        user_data = user_app_callback_class()
        user_data.use_frame = True # We need the frame for drawing

        # Get default parser and set input to rpi
        parser = get_default_parser()
        sys.argv.extend(['--input', 'rpi'])

        app = HeadlessGStreamerPoseEstimationApp(app_callback, user_data, parser=parser)
        app.run()

    except ConnectionRefusedError:
        print(f"ERROR: Connection to Flask app refused. Is Flask app running and listening on {TCP_IP}:{TCP_PORT}?")
    except Exception as e:
        print(f"An error occurred in camera streamer: {e}")
    finally:
        if sock:
            sock.close()
            print("Streamer socket closed.")

if __name__ == '__main__':
    main()