#!/bin/bash

# ===================================================================
# RheumActive v2 - Pose Detection Runner
#
# This script runs the standard rpicam-hello application with the
# Hailo YOLOv8 pose estimation post-processing configuration.
# ===================================================================

echo "Starting Real-Time Pose Estimation..."

# If the DISPLAY variable isn't set (e.g., in an SSH session),
# set it to :0.0 to output to the primary monitor.
if [ -z "$DISPLAY" ]; then
  echo "DISPLAY variable not set. Setting to ':0.0'."
  export DISPLAY=:0.0
fi

# Path to the post-processing configuration file
# This file was installed system-wide by the 'hailo-all' package
POST_PROCESS_FILE="/usr/share/hailo/postprocesses/rpicam_apps/hailo_yolov8_pose.json"

# Check if the config file exists
if [ ! -f "$POST_PROCESS_FILE" ]; then
  echo "Error: Pose detection config file not found at $POST_PROCESS_FILE"
  echo "Please ensure the Hailo software stack is installed correctly (see setup/02-software-install.md)."
  exit 1
fi

# Run the camera application with the Hailo post-processing
# -t 0: Run indefinitely (until Ctrl+C)
rpicam-hello -t 0 --post-process-file "$POST_PROCESS_FILE"

echo "Pose estimation stopped."
