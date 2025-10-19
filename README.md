# RheumActive v2

This is the second version of RheumActive, a system that helps people with rheumatoid arthritis to monitor and improve their mobility.

## Project Structure

* `/setup`: A step-by-step tutorial for setting up the hardware and base software from a fresh Raspberry Pi OS image.
* `/scripts`: Contains the main application scripts for running inference.

## Quick Start

1.  **Setup Hardware & Software:** Follow the tutorial in the `/setup` directory, starting with `01-hardware-setup.md`.
2.  **Run the App:** Once setup is complete, run the main pose detection script:
    ```bash
    ./scripts/run_pose_detection.sh
    ```
