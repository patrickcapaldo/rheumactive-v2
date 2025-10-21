#!/usr/bin/env python3

"""
Standalone test script for verifying camera access and pose detection logic.

This script captures a single frame from the Pi Camera, simulates Hailo AI inference,
calculates an angle, and saves a debug image.

Usage:
1. Install dependencies: pip install opencv-python picamera2 numpy
2. Run the script: python3 camera_test.py
3. Check for the 'output.jpg' file and the angle printed to the console.
"""

import cv2
import numpy as np
import time
from picamera2 import Picamera2

# --- Configuration ---

# The resolution for camera capture. It should match what the AI model expects.
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# For this example, we will calculate the left elbow angle.
# These are the standard indices for keypoints from models like YOLOv8-Pose.
LEFT_SHOULDER_INDEX = 5
LEFT_ELBOW_INDEX = 7
LEFT_WRIST_INDEX = 9

# --- Helper Functions ---

def get_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Calculate the angle between three points (p2 is the vertex)."""
    v1 = p1 - p2
    v2 = p3 - p2
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)
    
    # Avoid division by zero
    if norm_product == 0:
        return 0.0
        
    cosine_angle = dot_product / norm_product
    # Clip the value to handle potential floating point inaccuracies
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

def draw_pose(frame: np.ndarray, keypoints: np.ndarray, confidence_threshold=0.5):
    """Draw keypoints and connections on the frame."""
    for i, point in enumerate(keypoints):
        x, y, confidence = int(point[0]), int(point[1]), point[2]
        if confidence > confidence_threshold:
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(frame, str(i), (x + 5, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    # Define connections (e.g., left arm)
    connections = [(LEFT_SHOULDER_INDEX, LEFT_ELBOW_INDEX), (LEFT_ELBOW_INDEX, LEFT_WRIST_INDEX)]
    for start_idx, end_idx in connections:
        start_point = keypoints[start_idx]
        end_point = keypoints[end_idx]
        if start_point[2] > confidence_threshold and end_point[2] > confidence_threshold:
            cv2.line(frame, (int(start_point[0]), int(start_point[1])), (int(end_point[0]), int(end_point[1])), (0, 255, 255), 2)

# --- Main Execution Logic ---

def run_hailo_inference(frame: np.ndarray) -> np.ndarray:
    """
    *** THIS IS A PLACEHOLDER FUNCTION ***
    
    In a real implementation, this function would:
    1. Pre-process the frame (resize, normalize) to match the Hailo model's input.
    2. Run inference using the `hailort` Python library.
    3. Post-process the model's output tensors to get keypoints.
    
    For now, it returns a static, mock array of keypoints for a bent arm.
    The format is (17 keypoints, each with [x, y, confidence]).
    """
    print("\n[SIMULATION] Running mock Hailo inference...")
    
    # Create a mock pose (a bent left arm)
    mock_keypoints = np.zeros((17, 3), dtype=np.float32)
    
    # Left Shoulder
    mock_keypoints[LEFT_SHOULDER_INDEX] = [CAMERA_WIDTH * 0.3, CAMERA_HEIGHT * 0.4, 0.95]
    # Left Elbow
    mock_keypoints[LEFT_ELBOW_INDEX] = [CAMERA_WIDTH * 0.5, CAMERA_HEIGHT * 0.5, 0.95]
    # Left Wrist
    mock_keypoints[LEFT_WRIST_INDEX] = [CAMERA_WIDTH * 0.4, CAMERA_HEIGHT * 0.7, 0.95]
    
    return mock_keypoints

def main():
    """Main function to run the test."""
    picam2 = None
    try:
        # 1. Initialize the camera
        print("--- Initializing Camera ---")
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (CAMERA_WIDTH, CAMERA_HEIGHT)})
        picam2.configure(config)
        picam2.start()
        time.sleep(2)  # Allow camera to warm up
        print("Camera initialized successfully.")

        # 2. Capture a single frame
        print("\n--- Capturing Frame ---")
        frame = picam2.capture_array()
        # Convert from RGB to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        print(f"Frame captured with shape: {frame.shape}")

        # 3. Run pose detection (simulated)
        keypoints = run_hailo_inference(frame)

        # 4. Calculate the angle
        print("\n--- Calculating Angle ---")
        p1 = keypoints[LEFT_SHOULDER_INDEX, :2] # Left Shoulder
        p2 = keypoints[LEFT_ELBOW_INDEX, :2]   # Left Elbow (Vertex)
        p3 = keypoints[LEFT_WRIST_INDEX, :2]   # Left Wrist
        
        angle = get_angle(p1, p2, p3)
        print(f"[SUCCESS] Calculated Left Elbow Angle: {angle:.2f} degrees")

        # 5. Draw the pose and save the output image
        print("\n--- Saving Debug Image ---")
        draw_pose(frame, keypoints)
        cv2.putText(frame, f"Angle: {angle:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imwrite("output.jpg", frame)
        print("[SUCCESS] Saved debug image to 'output.jpg' in the current directory.")

    except ImportError as e:
        print("\n--- DEPENDENCY ERROR ---")
        print(f"Failed to import a required library: {e}")
        print("Please install the required dependencies by running:")
        print("pip install opencv-python picamera2 numpy")
        
    except Exception as e:
        print(f"\n--- An unexpected error occurred ---")
        print(e)
        if "camera" in str(e).lower():
            print("\nTroubleshooting: Please ensure the camera is enabled in 'raspi-config' and not in use by another process.")

    finally:
        if picam2:
            picam2.stop()
            print("\nCamera stopped.")

if __name__ == "__main__":
    main()
