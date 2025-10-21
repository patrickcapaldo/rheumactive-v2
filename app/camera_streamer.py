#!/usr/bin/env python3

import cv2
import numpy as np
import time
import json
import base64
import socket
from picamera2 import Picamera2

# --- Configuration ---
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
TCP_IP = '127.0.0.1'  # Loopback address for local communication
TCP_PORT = 5001       # Port for the camera streamer

# Keypoint indices for left elbow angle (YOLOv8-Pose)
LEFT_SHOULDER_INDEX = 5
LEFT_ELBOW_INDEX = 7
LEFT_WRIST_INDEX = 9

# --- Helper Functions ---
def get_angle(p1, p2, p3):
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    if norm_product == 0: return 0.0
    cosine_angle = np.clip(dot_product / norm_product, -1.0, 1.0)
    return np.degrees(np.arccos(cosine_angle))

def draw_pose(frame, keypoints, confidence_threshold=0.5):
    for i, point in enumerate(keypoints):
        if point[2] > confidence_threshold:
            cv2.circle(frame, (int(point[0]), int(point[1])), 5, (0, 255, 0), -1)

def _process_frame_and_get_data(frame: np.ndarray):
    # MOCK HAIlo INFERENCE
    mock_keypoints = np.zeros((17, 3), dtype=np.float32)
    mock_keypoints[LEFT_SHOULDER_INDEX] = [CAMERA_WIDTH * 0.3, CAMERA_HEIGHT * 0.4, 0.95]
    mock_keypoints[LEFT_ELBOW_INDEX] = [CAMERA_WIDTH * 0.5, CAMERA_HEIGHT * 0.5, 0.95]
    mock_keypoints[LEFT_WRIST_INDEX] = [CAMERA_WIDTH * 0.4, CAMERA_HEIGHT * 0.7, 0.95]

    p1, p2, p3 = mock_keypoints[LEFT_SHOULDER_INDEX, :2], mock_keypoints[LEFT_ELBOW_INDEX, :2], mock_keypoints[LEFT_WRIST_INDEX, :2]
    current_angle = get_angle(p1, p2, p3)

    draw_pose(frame, mock_keypoints)
    cv2.putText(frame, f"Angle: {current_angle:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    _, buffer = cv2.imencode('.jpg', frame)
    encoded_frame = base64.b64encode(buffer).decode('utf-8')

    return {
        "image": encoded_frame,
        "angle": round(current_angle, 1)
    }

# --- Main Streamer Logic ---
def main():
    print(f"Camera Streamer starting. Connecting to {TCP_IP}:{TCP_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((TCP_IP, TCP_PORT))
        print("Connected to Flask app.")

        print("--- Initializing Camera ---")
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)  # Allow camera to warm up
        print("Camera initialized successfully.")

        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Convert for OpenCV
            
            data = _process_frame_and_get_data(frame)
            json_data = json.dumps(data)
            
            # Send length of message first, then message itself
            message_length = len(json_data.encode('utf-8'))
            sock.sendall(message_length.to_bytes(4, 'big')) # 4 bytes for length
            sock.sendall(json_data.encode('utf-8'))
            
            time.sleep(0.05) # ~20 FPS

    except ConnectionRefusedError:
        print(f"ERROR: Connection to Flask app refused. Is Flask app running and listening on {TCP_IP}:{TCP_PORT}?")
    except Exception as e:
        print(f"An error occurred in camera streamer: {e}")
    finally:
        if 'picam2' in locals() and picam2:
            picam2.stop()
            print("Camera stopped.")
        sock.close()
        print("Streamer socket closed.")

if __name__ == '__main__':
    main()
