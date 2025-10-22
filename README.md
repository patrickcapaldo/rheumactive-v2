# RheumActive v2

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
- [Common Questions](#common-questions)
- [Success Indicators](#success-indicators)
- [Installation Time Estimate](#installation-time-estimate)
- [Getting Help](#getting-help)

## Quick Start

This section provides tailored instructions for different user types to get RheumActive v2 up and running.

### First Time Developer

This guide is for developers setting up the project from scratch, including hardware and software installation.

### First Time Developer

This guide is for developers setting up the project from scratch, including hardware and software installation.

#### 1. Hardware Setup

This section guides you through the physical assembly and initial configuration of your Raspberry Pi 5 with the Hailo AI HAT+ and Camera Module.

##### 1.1. Get Required Hardware

Here is a list of all the hardware required for implementing this project.

**Core Components:**
- **Coordinator:** [Raspberry Pi 5 4GB](https://thepihut.com/products/raspberry-pi-5?variant=42531604922563)
- **Compute:** [Raspberry Pi Hailo AI HAT+ 13 TOPS](https://thepihut.com/products/raspberry-pi-ai-hat-plus?variant=53621840118145)
- **Visual Sensor:** [Raspberry Pi Camera Module 3](https://thepihut.com/products/raspberry-pi-camera-module-3?variant=42305752039619)
- **Camera/Pi Connection:** [Camera Adapter Cable for Raspberry Pi 5 300mm](https://thepihut.com/products/camera-adapter-cable-for-raspberry-pi-5?variant=42531560816835)
- **Base Memory:** [SanDisk MicroSD Card 32GB](https://www.amazon.co.uk/dp/B08GY9NYRM/?coliid=I60G1GWDIL00Y&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- **Power:** [Raspberry Pi 27W USB-C Power Supply](https://thepihut.com/products/raspberry-pi-27w-usb-c-power-supply?variant=42531604070595)
- **Cooling:** [Active Cooler for Raspberry Pi 5](https://thepihut.com/products/active-cooler-for-raspberry-pi-5)

**Camera Mounting (Recommended for Stability):**
- **Camera Housing:** [Tripod Mount for Raspberry Pi Camera Modules](https://thepihut.com/products/tripod-mount-for-raspberry-pi-camera-modules)
- **Camera Stability:** [Small Tripod for Raspberry Pi HQ Camera](https://thepihut.com/products/small-tripod-for-raspberry-pi-hq-camera)
- **Camera Pointing:** [Heavy-duty Tripod Swivel Ball Adapter](https://thepihut.com/products/heavy-duty-tripod-swivel-ball-adapter)

**Essential Peripherals (You may already own these):**
- Keyboard
- Mouse
- Monitor (with HDMI port)
- Another computer (to flash SD card)
- [Micro HDMI Cable 1m](https://thepihut.com/products/hdmi-to-micro-hdmi-cable-2m-gold-plated?variant=40818117050563) (for Pi/Monitor Connection)
- [SD Card Reader](https://www.amazon.co.uk/Beikell-High-speed-Adapter-Supports-MMC-Compatible-Windows/dp/B07L9VT8YY/ref/sr_1_4?sr=8-4) (for Flashing RPi OS)

**Optional (Recommended for Long-Term Use):**
- **Extra Storage:** [NVMe PCIe 4.0 Internal SSD 500GB M.2 2280](https://www.amazon.co.uk/dp/B0DBR9RZLV/?coliid=I1AGFURUH066UI&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- **Pi/Extra Storage Connection:** [NVMe SSD Enclosure USB-C](https://www.amazon.co.uk/UGREEN-Enclosure-External-Drive-Cables/dp/B09T97Z7DM/ref/sr_1_1?sr=8-1)

##### 1.2. Base Raspberry Pi Setup (OS Installation)

Before connecting specialized hardware, we'll set up the Raspberry Pi's operating system.

**<span style="color: orange;">&#x1F40D; Warning:</span> Do NOT connect the AI HAT+ during initial OS setup – it can prevent the Pi from booting properly.**

1.  On a separate computer, download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2.  Insert the micro SD card into an SD card reader and plug it into your computer.
3.  Launch the Raspberry Pi Imager:
    *   Select your Raspberry Pi model: **Raspberry Pi 5**
    *   Click "Choose OS" → "Raspberry Pi OS (other)" → **"Raspberry Pi OS (Legacy, 64-bit) Full"**
    *   **<span style="color: orange;">&#x1F40D; Critical:</span> You MUST choose the Legacy version with Debian Bookworm. Do NOT use Trixie – the Hailo software is not compatible with it yet.**
    *   Select your SD card as the storage device.
4.  Before writing, click the settings gear icon (or press `Ctrl+Shift+X`):
    *   Set hostname (e.g., `rpi5`)
    *   Enable SSH
    *   Set username and password
    *   Configure WiFi credentials (optional but recommended)
5.  Flash the operating system to the SD card and wait for completion.
6.  Safely eject the SD card from the reader.
7.  Insert the SD card into the Raspberry Pi 5 (bottom of the board).
8.  **Do NOT connect the AI HAT+ yet**. Connect only:
    *   Power supply (USB-C)
    *   Micro HDMI cable to the **left port** (port closest to USB-C power)
    *   Monitor via HDMI
    *   Keyboard and mouse (USB)
9.  Power on the Pi and wait for it to boot.
10. You should see the Raspberry Pi desktop appear on your monitor. If you see a solid green light or consistent blinking (about twice per second), the SD card may be faulty or incorrectly flashed – try reflashing or a different SD card.
11. Connect to the internet via WiFi or Ethernet.
12. Verify the OS version by running:
    ```bash
    cat /etc/os-release
    ```
    You should see `VERSION_CODENAME=bookworm`. If it says `trixie`, you've flashed the wrong version.

##### 1.3. Specialized Hardware Assembly

Now that the Pi has successfully booted and been verified, we can connect the specialized hardware.

###### AI HAT+ Installation

1.  Shut down the Pi completely:
    ```bash
    sudo poweroff
    ```
2.  Wait for the green light to stop completely, then unplug the power supply.
3.  Disconnect the micro HDMI cable (makes the next steps easier).
4.  Install the Active Cooler first:
    *   Follow the instructions included in the box.
    *   Align the cooler correctly.
    *   Push in the stabilizing pins into the Pi board.
    *   Connect the cable with the yellow wire closest to the edge of the Pi.
5.  Prepare the AI HAT+:
    *   Attach plastic spacers to the AI HAT+ mounting holes.
    *   Attach the GPIO extension headers to the Pi board.
6.  Install the AI HAT+:
    *   Carefully lower the HAT onto the GPIO pins (keep the PCIe ribbon cable out of the way).
    *   Push down gently until the GPIO pins are fully seated.
    *   Connect the PCIe ribbon cable:
        *   One end goes to the AI HAT+.
        *   The other end goes to the Pi's PCIe port.
        *   Push the ribbon into the connector evenly, then press the clamp down.
    *   Tighten the spacer screws to secure the HAT.

###### Camera Installation

7.  Thread the camera adapter cable through the camera housing slit.
8.  Connect the adapter ribbon to the camera module:
    *   The wide end goes into the camera.
    *   The side with visible circuit traces faces the same direction as the lens.
    *   Push the ribbon in evenly, then close the clamp.
9.  Connect the other end to the Pi:
    *   Insert into the camera port (between the two USB 3.0 ports).
    *   The side with visible traces should face the USB ports.
    *   Push in evenly and close the clamp.
10. Attach the camera housing to the swivel ball mount adapter.
11. Attach the swivel ball adapter to the tripod.
12. Reconnect the micro HDMI cable and power supply.
13. Power on the Pi – it should now boot normally with all hardware attached.
14. **<span style="color: #007bff;">&#x1F428; Note:</span>** You can now put your Pi in a case of your choice. However, note that with the extra height from the AI Hat and ribbon cables, some cases will likely not fit. For example, I’ve found that this one worked for me: 52Pi Metal Case for Raspberry Pi 5, with Raspberry Pi Active Cooler for Raspberry Pi 5 4GB/8GB, Support X1000/X1001 PCIe Peripheral Board

2.  **Prerequisites**: Ensure all [Prerequisites](#prerequisites) are met.
3.  **Download required files** from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) to `~/Downloads/`:
    -   `hailort_4.23.0_arm64.deb`
    -   `hailort-pcie-driver_4.23.0_all.deb`

3.  **Run the pre-reboot hardware installation** (this will check your system and install HailoRT and the PCIe driver):
    ```bash
    cd ~/rheumactive-v2
    make full-install
    ```
    **What You'll See**:
    The installation will show progress like this:
    ```
    === System Requirements Check ===
    Checking OS version... ✓ Bookworm detected
    Checking architecture... ✓ ARM64 detected
    Checking hardware model... ✓ Raspberry Pi 5 detected
    ...

    === Installing HailoRT Runtime ===
    Installing: hailort_4.23.0_arm64.deb
    ✓ HailoRT 4.23.0 installed successfully
    ...
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
    You should see:
    ```
    === Verifying Hailo Installation ===
    Checking HailoRT package... ✓ Installed (version: 4.23.0)
    Checking PCIe driver package... ✓ Installed (version: 4.23.0)
    Checking kernel module... ✓ Loaded
    ...
    === ✓ Installation verified successfully ===
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

#### Next Steps for Developers

After successful installation and initial setup:

1.  **Explore the application**:
    *   Camera feed should show pose keypoints in real-time
    *   Try different poses and movements

2.  **Review documentation**:
    *   Full setup guide: `docs/01-initial-setup.md`
    *   Setup scripts: `scripts/setup/README.md`

3.  **Start developing**:
    *   Application code will go in `src/`
    *   See project roadmap for features

[Back to Top](#table-of-contents)

### First Time User

This guide is for users who want to get the application running with minimal interaction, assuming a fresh system.

### First Time User

This guide is for users who want to get the application running with minimal interaction, assuming a fresh system.

#### 1. Hardware Setup

This section guides you through the physical assembly and initial configuration of your Raspberry Pi 5 with the Hailo AI HAT+ and Camera Module.

##### 1.1. Get Required Hardware

Here is a list of all the hardware required for implementing this project.

**Core Components:**
- **Coordinator:** [Raspberry Pi 5 4GB](https://thepihut.com/products/raspberry-pi-5?variant=42531604922563)
- **Compute:** [Raspberry Pi Hailo AI HAT+ 13 TOPS](https://thepihut.com/products/raspberry-pi-ai-hat-plus?variant=53621840118145)
- **Visual Sensor:** [Raspberry Pi Camera Module 3](https://thepihut.com/products/raspberry-pi-camera-module-3?variant=42305752039619)
- **Camera/Pi Connection:** [Camera Adapter Cable for Raspberry Pi 5 300mm](https://thepihut.com/products/camera-adapter-cable-for-raspberry-pi-5?variant=42531560816835)
- **Base Memory:** [SanDisk MicroSD Card 32GB](https://www.amazon.co.uk/dp/B08GY9NYRM/?coliid=I60G1GWDIL00Y&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- **Power:** [Raspberry Pi 27W USB-C Power Supply](https://thepihut.com/products/raspberry-pi-27w-usb-c-power-supply?variant=42531604070595)
- **Cooling:** [Active Cooler for Raspberry Pi 5](https://thepihut.com/products/active-cooler-for-raspberry-pi-5)

**Camera Mounting (Recommended for Stability):**
- **Camera Housing:** [Tripod Mount for Raspberry Pi Camera Modules](https://thepihut.com/products/tripod-mount-for-raspberry-pi-camera-modules)
- **Camera Stability:** [Small Tripod for Raspberry Pi HQ Camera](https://thepihut.com/products/small-tripod-for-raspberry-pi-hq-camera)
- **Camera Pointing:** [Heavy-duty Tripod Swivel Ball Adapter](https://thepihut.com/products/heavy-duty-tripod-swivel-ball-adapter)

**Essential Peripherals (You may already own these):**
- Keyboard
- Mouse
- Monitor (with HDMI port)
- Another computer (to flash SD card)
- [Micro HDMI Cable 1m](https://thepihut.com/products/hdmi-to-micro-hdmi-cable-2m-gold-plated?variant=40818117050563) (for Pi/Monitor Connection)
- [SD Card Reader](https://www.amazon.co.uk/Beikell-High-speed-Adapter-Supports-MMC-Compatible-Windows/dp/B07L9VT8YY/ref/sr_1_4?sr=8-4) (for Flashing RPi OS)

**Optional (Recommended for Long-Term Use):**
- **Extra Storage:** [NVMe PCIe 4.0 Internal SSD 500GB M.2 2280](https://www.amazon.co.uk/dp/B0DBR9RZLV/?coliid=I1AGFURUH066UI&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- **Pi/Extra Storage Connection:** [NVMe SSD Enclosure USB-C](https://www.amazon.co.uk/UGREEN-Enclosure-External-Drive-Cables/dp/B09T97Z7DM/ref/sr_1_1?sr=8-1)

##### 1.2. Base Raspberry Pi Setup (OS Installation)

Before connecting specialized hardware, we'll set up the Raspberry Pi's operating system.

**<span style="color: orange;">&#x1F40D; Warning:</span> Do NOT connect the AI HAT+ during initial OS setup – it can prevent the Pi from booting properly.**

1.  On a separate computer, download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2.  Insert the micro SD card into an SD card reader and plug it into your computer.
3.  Launch the Raspberry Pi Imager:
    *   Select your Raspberry Pi model: **Raspberry Pi 5**
    *   Click "Choose OS" → "Raspberry Pi OS (other)" → **"Raspberry Pi OS (Legacy, 64-bit) Full"**
    *   **<span style="color: orange;">&#x1F40D; Critical:</span> You MUST choose the Legacy version with Debian Bookworm. Do NOT use Trixie – the Hailo software is not compatible with it yet.**
    *   Select your SD card as the storage device.
4.  Before writing, click the settings gear icon (or press `Ctrl+Shift+X`):
    *   Set hostname (e.g., `rpi5`)
    *   Enable SSH
    *   Set username and password
    *   Configure WiFi credentials (optional but recommended)
5.  Flash the operating system to the SD card and wait for completion.
6.  Safely eject the SD card from the reader.
7.  Insert the SD card into the Raspberry Pi 5 (bottom of the board).
8.  **Do NOT connect the AI HAT+ yet**. Connect only:
    *   Power supply (USB-C)
    *   Micro HDMI cable to the **left port** (port closest to USB-C power)
    *   Monitor via HDMI
    *   Keyboard and mouse (USB)
9.  Power on the Pi and wait for it to boot.
10. You should see the Raspberry Pi desktop appear on your monitor. If you see a solid green light or consistent blinking (about twice per second), the SD card may be faulty or incorrectly flashed – try reflashing or a different SD card.
11. Connect to the internet via WiFi or Ethernet.
12. Verify the OS version by running:
    ```bash
    cat /etc/os-release
    ```
    You should see `VERSION_CODENAME=bookworm`. If it says `trixie`, you've flashed the wrong version.

##### 1.3. Specialized Hardware Assembly

Now that the Pi has successfully booted and been verified, we can connect the specialized hardware.

###### AI HAT+ Installation

1.  Shut down the Pi completely:
    ```bash
    sudo poweroff
    ```
2.  Wait for the green light to stop completely, then unplug the power supply.
3.  Disconnect the micro HDMI cable (makes the next steps easier).
4.  Install the Active Cooler first:
    *   Follow the instructions included in the box.
    *   Align the cooler correctly.
    *   Push in the stabilizing pins into the Pi board.
    *   Connect the cable with the yellow wire closest to the edge of the Pi.
5.  Prepare the AI HAT+:
    *   Attach plastic spacers to the AI HAT+ mounting holes.
    *   Attach the GPIO extension headers to the Pi board.
6.  Install the AI HAT+:
    *   Carefully lower the HAT onto the GPIO pins (keep the PCIe ribbon cable out of the way).
    *   Push down gently until the GPIO pins are fully seated.
    *   Connect the PCIe ribbon cable:
        *   One end goes to the AI HAT+.
        *   The other end goes to the Pi's PCIe port.
        *   Push the ribbon into the connector evenly, then press the clamp down.
    *   Tighten the spacer screws to secure the HAT.

###### Camera Installation

7.  Thread the camera adapter cable through the camera housing slit.
8.  Connect the adapter ribbon to the camera module:
    *   The wide end goes into the camera.
    *   The side with visible circuit traces faces the same direction as the lens.
    *   Push the ribbon in evenly, then close the clamp.
9.  Connect the other end to the Pi:
    *   Insert into the camera port (between the two USB 3.0 ports).
    *   The side with visible traces should face the USB ports.
    *   Push in evenly and close the clamp.
10. Attach the camera housing to the swivel ball mount adapter.
11. Attach the swivel ball adapter to the tripod.
12. Reconnect the micro HDMI cable and power supply.
13. Power on the Pi – it should now boot normally with all hardware attached.
14. **<span style="color: #007bff;">&#x1F428; Note:</span>** You can now put your Pi in a case of your choice. However, note that with the extra height from the AI Hat and ribbon cables, some cases will likely not fit. For example, I’ve found that this one worked for me: 52Pi Metal Case for Raspberry Pi 5, with Raspberry Pi Active Cooler for Raspberry Pi 5 4GB/8GB, Support X1000/X1001 PCIe Peripheral Board

2.  **Prerequisites**: Ensure all [Prerequisites](#prerequisites) are met.
3.  **Download required files** from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) to `~/Downloads/`:
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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)
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

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)

## Prerequisites

Before starting, ensure you have:

- [ ] Raspberry Pi 5 (4GB or 8GB)
- [ ] Hailo AI HAT+ 13 TOPS installed
- [ ] Raspberry Pi Camera Module 3 connected
- [ ] Raspberry Pi OS (Legacy, 64-bit) **Bookworm** installed
- [ ] Active Cooler installed
- [ ] PCIe Gen3 enabled (via `sudo raspi-config`)
- [ ] System updated (`sudo apt update && sudo apt full-upgrade -y`)
- [ ] Internet connection active
- [ ] Monitor, keyboard, mouse connected

[Back to Top](#table-of-contents)

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

[Back to Top](#table-of-contents)
```

## Installation Time Estimate

| Step | Duration |
|------|----------|
| Download .deb files | 2-3 min |
| Clone repository | < 1 min |
| Run full-install | 5-10 min |
| Reboot | 1-2 min |
| Verify + permissions | 1 min |
| **Total** | **10-15 minutes** |

[Back to Top](#table-of-contents)

## Success Indicators

You know it's working when:
- ✓ `make verify-install` shows all green checkmarks
- ✓ `hailortcli scan` shows `[-] Device: 0001:01:00.0`
- ✓ `./scripts/run_pose_detection.sh` shows camera feed with pose overlays
- ✓ No red error messages

[Back to Top](#table-of-contents)

## Common Questions

**Q: Do I need to download anything else?**  
A: No, just the two `.deb` files. Everything else is handled by apt.

**Q: Can I use Raspberry Pi OS Trixie?**  
A: No, Hailo software requires Bookworm. Use the Legacy version.

**Q: How long does installation take?**  
A: 5-10 minutes for installation, plus a reboot.

**Q: What if I already installed hailo-all via apt?**  
A: Run `make clean` and start fresh. The manual `.deb` approach is more reliable.

**Q: Can I re-run installation?**  
A: Yes! `make clean` removes markers and lets you start over.

**Q: Why do I need to reboot?**  
A: The PCIe driver is a kernel module that requires a reboot to load.

[Back to Top](#table-of-contents)

## Getting Help

- Check `make help` for available commands
- Review script output for specific error messages
- See main documentation: `docs/01-initial-setup.md`
- Ensure all prerequisites are met before starting

[Back to Top](#table-of-contents)
