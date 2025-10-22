# RheumActive v2 - Automated Setup Scripts

This directory contains automated installation scripts for setting up the Hailo AI software stack on Raspberry Pi 5.
It also includes the RheumActive web application, built with Flask, for real-time pose estimation.

## Table of Contents
- [Quick Start](#quick-start)
  - [First Time Developer](#first-time-developer)
  - [First Time User](#first-time-user)
  - [Returning Developer](#returning-developer)
  - [Returning User](#returning-user)
- [Project Architecture (Web Application)](#project-architecture-web-application)
- [Running the Web Application](#running-the-web-application)
- [Available Make Targets](#available-make-targets)
- [Individual Scripts](#individual-scripts)
- [Installation Workflow](#installation-workflow)
- [Marker Files](#marker-files)
- [Troubleshooting](#troubleshooting)
- [Prerequisites](#prerequisites)
- [Manual Installation](#manual-installation)
- [Getting Help](#getting-help)

## Quick Start

This section provides tailored instructions for different user types to get RheumActive v2 up and running.

### First Time Developer

This guide is for developers setting up the project from scratch, including hardware and software installation.

1.  **Prerequisites**: Ensure all [Prerequisites](#prerequisites) are met.
2.  **Download required files** from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) to `~/Downloads/`:
    -   `hailort_4.23.0_arm64.deb`
    -   `hailort-pcie-driver_4.23.0_all.deb`

3.  **Run the pre-reboot hardware installation** (this will check your system and install HailoRT and the PCIe driver):
    ```bash
    cd ~/rheumactive-v2
    make full-install
    ```

4.  **Reboot your system**:
    ```bash
    sudo reboot
    ```

5.  **After reboot, run the post-reboot installation steps** (this will verify the installation and set up device permissions):
    ```bash
    cd ~/rheumactive-v2
    make post-reboot-install
    ```

6.  **Set up the Web Application environment**:
    ```bash
    cd ~/rheumactive-v2/app
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
    *(Ensure `libcap-dev` is installed on your system: `sudo apt-get install libcap-dev`)*

7.  **Run the Web Application**:
    Follow the instructions in the [Running the Web Application](#running-the-web-application) section below.

### First Time User

This guide is for users who want to get the application running with minimal interaction, assuming a fresh system.

1.  **Prerequisites**: Ensure all [Prerequisites](#prerequisites) are met.
2.  **Download required files** from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) to `~/Downloads/`:
    -   `hailort_4.23.0_arm64.deb`
    -   `hailort-pcie-driver_4.23.0_all.deb`

3.  **Run the pre-reboot hardware installation**:
    ```bash
    cd ~/rheumactive-v2
    make full-install
    ```

4.  **Reboot your system**:
    ```bash
    sudo reboot
    ```

5.  **After reboot, run the post-reboot installation steps**:
    ```bash
    cd ~/rheumactive-v2
    make post-reboot-install
    ```

6.  **Set up the Web Application environment**:
    ```bash
    cd ~/rheumactive-v2/app
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
    *(Ensure `libcap-dev` is installed on your system: `sudo apt-get install libcap-dev`)*

7.  **Run the Web Application**:
    Follow the instructions in the [Running the Web Application](#running-the-web-application) section below.

### Returning Developer

This guide is for developers who have previously set up the project and want to quickly get back to development.

1.  **Navigate to the project directory**:
    ```bash
    cd ~/rheumactive-v2
    ```

2.  **Ensure installation markers are cleared (if you want to re-run any installation steps)**:
    ```bash
    make clean
    ```
    *(Only run `make clean` if you intend to re-run installation steps. Otherwise, skip this.)*

3.  **If you need to re-run hardware installation (e.g., after OS update or driver issues)**:
    *   Run `make full-install`
    *   `sudo reboot`
    *   `make post-reboot-install`

4.  **Set up and activate the Web Application environment**:
    ```bash
    cd ~/rheumactive-v2/app
    source .venv/bin/activate
    ```

5.  **Run the Web Application**:
    Follow the instructions in the [Running the Web Application](#running-the-web-application) section below.

### Returning User

This guide is for users who have previously set up the application and just want to run it again.

1.  **Navigate to the web application directory**:
    ```bash
    cd ~/rheumactive-v2/app
    ```

2.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

3.  **Run the Web Application**:
    Follow the instructions in the [Running the Web Application](#running-the-web-application) section below.

## Project Architecture (Web Application)

To overcome compatibility issues with hardware-specific libraries (`picamera2`) and Python virtual environments, the web application uses a two-process architecture:

1.  **Flask Backend (`app.py`):**
    *   Runs in an **isolated Python virtual environment**.
    *   Manages the web server, serves HTML, and provides API endpoints for angle data and video streams.
    *   Communicates with the `camera_streamer.py` process via a TCP socket.

2.  **Camera Streamer (`camera_streamer.py`):**
    *   Runs using the **system's Python interpreter** (where `picamera2` and `opencv-python` are typically installed and configured for hardware access).
    *   Initializes `picamera2` to capture frames from the Raspberry Pi Camera.
    *   Performs mock pose detection (this is where Hailo inference would be integrated).
    *   Encodes frames to MJPEG and sends them, along with angle data, over a TCP socket to the Flask backend.

This separation ensures that the hardware-dependent code runs in its native environment while the web application remains isolated and manageable.

## Running the Web Application

To run the RheumActive web application, you need to start two separate Python processes in two different terminal windows:

#### **Terminal Window 1: Start the Flask Backend**

1.  **Navigate to the `app` directory**:
    ```bash
    cd ~/rheumactive-v2/app
    ```

2.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

3.  **Run the Flask application**:
    ```bash
    python3 app.py
    ```
    *(You should see Flask starting up and a message like "Flask app listening for camera streamer on 127.0.0.1:5001".)*

#### **Terminal Window 2: Start the Camera Streamer**

1.  **Navigate to the `app` directory**:
    ```bash
    cd ~/rheumactive-v2/app
    ```

2.  **Run the camera streamer using your system's Python**:
    *(Do NOT activate the virtual environment in this terminal, as `picamera2` is installed globally.)*
    ```bash
    python3 camera_streamer.py
    ```
    *(You should see messages about the camera initializing and "Connected to Flask app.".)*

Once both processes are running, open your web browser and navigate to **http://localhost:5000**.

---

## Available Make Targets

| Target | Description |
|--------|-------------|
| `make help` | Show all available commands |
| `make check-system` | Verify system requirements (OS, hardware) |
| `make install-hailo` | Install Hailo software packages |
| `make verify-install` | Verify installation and firmware communication |
| `make setup-permissions` | Configure device permissions |
| `make test-camera` | Run a quick 5-second camera test |
| `make full-install` | Run pre-reboot installation steps (check + install Hailo) |
| `make post-reboot-install` | Run post-reboot installation steps (verify + permissions) |
| `make clean` | Remove installation markers (to re-run steps) |
| `make mark-reboot-done` | Clear reboot marker after rebooting |

## Individual Scripts

The Makefile orchestrates these scripts in the correct order:

### 01_check_system.sh
- Verifies OS version (must be Bookworm)
- Checks architecture (ARM64)
- Confirms Raspberry Pi 5 hardware
- Verifies PCIe Gen3 configuration
- Checks for Hailo device on PCIe bus
- Validates firmware version
- Ensures required packages are installed

### 02_install_hailort.sh
- Installs HailoRT runtime from `.deb` package
- Fixes dependencies
- Enables and starts hailort.service
- Verifies installation

**Usage**: Called automatically by Makefile, or manually:
```bash
./setup/02_install_hailort.sh ~/Downloads/hailort_4.23.0_arm64.deb
```

### 03_install_driver.sh
- Installs PCIe driver from `.deb` package
- Configures DKMS if available
- Marks system as requiring reboot
- Verifies installation

**Usage**: Called automatically by Makefile, or manually:
```bash
./setup/03_install_driver.sh ~/Downloads/hailort-pcie-driver_4.23.0_all.deb
```

**Note**: You MUST reboot after this step.

### 04_verify_install.sh
- Checks all installed packages
- Verifies kernel module is loaded
- Tests hailort.service status
- Confirms device visibility on PCIe
- Tests `hailortcli` communication
- Verifies firmware identification
- Checks for pose detection configuration file

**Usage**:
```bash
./setup/04_verify_install.sh
```

### 05_setup_permissions.sh
- Creates `hailo` group
- Adds current user to hailo group
- Sets device ownership to `root:hailo`
- Sets device permissions to `660`
- Creates persistent udev rule
- Reloads udev rules

**Usage**:
```bash
bash
./setup/05_setup_permissions.sh
```

**Note**: You may need to log out and back in after running this script.

## Installation Workflow

The Makefile orchestrates these scripts in the correct order:

### Pre-Reboot Installation Flow
```
check-system
    ↓
install-hailo
```

### Post-Reboot Installation Flow
```
verify-install
    ↓
setup-permissions
    ↓
Ready to run pose detection
```

### Marker Files

- `.install_markers/01_system_check` - System requirements verified
- `.install_markers/02_hailo_install` - HailoRT runtime installed
- `.install_markers/03_driver_install` - PCIe driver installed
- `.install_markers/04_permissions` - Permissions configured
- `.install_markers/05_needs_reboot` - Reboot required (removed after reboot)

To force re-running a step, delete its marker:
```bash
rm .install_markers/02_hailo_install
make install-hailo
```

Or remove all markers:
```bash
make clean
```

## Troubleshooting

### "Driver version mismatch" error
This occurs when the kernel module version doesn\'t match the library version.
```bash
# Check versions
cat /sys/module/hailo_pci/version
hailortcli --version

# If different, ensure both .deb files are installed and reboot
sudo reboot
```

### "Permission denied" when running hailortcli
```bash
# Check group membership
groups

# Should show 'hailo' in the list
# If not, run:
newgrp hailo

# Or log out and back in
```

### Device not detected on PCIe
```bash
# Check physical connection
lspci | grep Hailo

# If not shown:
# 1. Power off completely
# 2. Reseat AI HAT+ and PCIe ribbon
# 3. Power on and check again
```

### Installation marker stuck
If installation gets stuck or you need to re-run a step:
```bash
# Remove specific marker
rm .install_markers/03_driver_install

# Or remove all markers
make clean
```

### Reboot required but can't verify
After rebooting, if verification still fails:
```bash
# Manually clear the reboot marker
make mark-reboot-done

# Then try verification again
make post-reboot-install
```

## Prerequisites

Before running any installation:
1. Raspberry Pi OS (Legacy, 64-bit) Bookworm installed
2. AI HAT+ properly connected
3. System updated: `sudo apt update && sudo apt full-upgrade -y`
4. PCIe Gen3 enabled: `sudo raspi-config` → Advanced Options → PCIe Speed
5. Downloaded `.deb` files in `~/Downloads/`

## Manual Installation

If you prefer not to use the Makefile, you can run scripts individually in order:
```bash
# 1. Check system
./setup/01_check_system.sh

# 2. Install HailoRT
./setup/02_install_hailort.sh ~/Downloads/hailort_4.23.0_arm64.deb

# 3. Install driver
./setup/03_install_driver.sh ~/Downloads/hailort-pcie-driver_4.23.0_all.deb

# 4. REBOOT
sudo reboot

# 5. Verify (after reboot)
./setup/04_verify_install.sh

# 6. Setup permissions
./setup/05_setup_permissions.sh

# 7. Log out and back in (or run 'newgrp hailo')
```

## Getting Help

- Check `make help` for available commands
- Review script output for specific error messages
- See main documentation: `docs/01-initial-setup.md`
- Ensure all prerequisites are met before starting
