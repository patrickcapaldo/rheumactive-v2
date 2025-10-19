#!/bin/bash

# --- Configuration Variables ---

# The full command that successfully launches the pose detection application.
# We are using the ABSOLUTE path for the configuration file to ensure portability.
# Your working path: /usr/share/rpi-camera-assets/hailo_yolov8_pose.json
CONFIG_FILE="/usr/share/rpi-camera-assets/hailo_yolov8_pose.json"

# --- Pre-flight Checks ---

echo "Starting Real-Time Pose Estimation from rheumactive-v2 repo..."

# 1. Check if the required configuration file exists on the system.
if [ ! -f "$CONFIG_FILE" ]; then
    echo " "
    echo "--- FATAL ERROR ---"
    echo "Required pose detection configuration file not found at: $CONFIG_FILE"
    echo "Please ensure the Raspberry Pi Camera assets and Hailo packages are correctly installed."
    echo "Exiting the script."
    echo "-------------------"
    exit 1
fi

# 2. Check if the main executable is in the system PATH.
if ! command -v rpicam-hello &> /dev/null
then
    echo " "
    echo "--- FATAL ERROR ---"
    echo "The 'rpicam-hello' command was not found in the system PATH."
    echo "Please ensure the official Raspberry Pi Camera application package is installed."
    echo "Exiting the script."
    echo "-------------------"
    exit 1
fi

echo "All dependencies and configuration confirmed. Launching application..."
echo " "

# --- Main Application Execution ---

# Run the command that you confirmed works, using the -t 0 (timeout 0, run indefinitely)
# and the absolute path to the configuration file.
rpicam-hello -t 0 --post-process-file "$CONFIG_FILE"
```eof

### How to Finalise

1.  **Replace the script:** Save this new content into your `run_pose_detection.sh` file inside your `rheumactive-v2` repo.
2.  **Test:** You should now be able to run it successfully from the root of your `rheumactive-v2` repo:
    ```bash
    patrick@rpi5:~/rheumactive-v2 $ ./scripts/run_pose_detection.sh
    ```
