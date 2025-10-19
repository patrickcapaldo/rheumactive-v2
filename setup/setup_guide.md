# Initial Setup

This will guide you, from start to finish, to setup the RheumActive pose detection system.

# 1. Get Hardware

This is a list of all the hardware required for implementing this project.

- Coordinator: [Raspberry Pi 5 4GB](https://thepihut.com/products/raspberry-pi-5?variant=42531604922563)
- Compute: [Raspberry Pi Hailo AI HAT+ 13 TOPS](https://thepihut.com/products/raspberry-pi-ai-hat-plus?variant=53621840118145)
- Visual Sensor: [Raspberry Pi Camera Module 3](https://thepihut.com/products/raspberry-pi-camera-module-3?variant=42305752039619)
- Camera/Pi Connection: [Camera Adapter Cable for Raspberry Pi 5 300mm](https://thepihut.com/products/camera-adapter-cable-for-raspberry-pi-5?variant=42531560816835)
- Camera Housing: [Tripod Mount for Raspberry Pi Camera Modules](https://thepihut.com/products/tripod-mount-for-raspberry-pi-camera-modules)
- Camera Stability: [Small Tripod for Raspberry Pi HQ Camera](https://thepihut.com/products/small-tripod-for-raspberry-pi-hq-camera)
- Camera Pointing: [Heavy-duty Tripod Swivel Ball Adapter](https://thepihut.com/products/heavy-duty-tripod-swivel-ball-adapter)
- Base Memory: [SanDisk MicroSD Card 32GB](https://www.amazon.co.uk/dp/B08GY9NYRM/?coliid=I60G1GWDIL00Y&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- Power: [Raspberry Pi 27W USB-C Power Supply](https://thepihut.com/products/raspberry-pi-27w-usb-c-power-supply?variant=42531604070595)
- Cooling: [Active Cooler for Raspberry Pi 5](https://thepihut.com/products/active-cooler-for-raspberry-pi-5)
- Pi/Monitor Connection: [Micro HDMI Cable 1m](https://thepihut.com/products/hdmi-to-micro-hdmi-cable-2m-gold-plated?variant=40818117050563)
- Flashing RPi OS: [SD Card Reader](https://www.amazon.co.uk/Beikell-High-speed-Adapter-Supports-MMC-Compatible-Windows/dp/B07L9VT8YY/ref=sr_1_4?sr=8-4)

The following aren't absolutely necessary, but are recommended for long-term use:
- Extra Storage: [NVMe PCIe 4.0 Internal SSD 500GB M.2 2280](https://www.amazon.co.uk/dp/B0DBR9RZLV/?coliid=I1AGFURUH066UI&colid=1O4CX6QKF4BPD&ref_=list_c_wl_lv_ov_lig_dp_it)
- Pi/Extra Storage Connection: [NVMe SSD Enclosure USB-C](https://www.amazon.co.uk/UGREEN-Enclosure-External-Drive-Cables/dp/B09T97Z7DM/ref=sr_1_1?sr=8-1)

You may already have the following but definitely find some if you don't have them:
- Keyboard
- Mouse
- Monitor (with HDMI port)
- Another computer (to flash)

# 2. Base Raspberry Pi Setup

Before we do anything with the more specialised hardware (e.g., AI Hat and Camera Module), we first need to get the Raspberry Pi working on its own.

**CRITICAL**: Do NOT connect the AI HAT+ during initial setup - it will prevent the Pi from booting properly.

1. On a separate computer, download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Once downloaded, take the micro SD card and insert it into the SD card reader.
3. Plug the SD card reader into your separate computer.
4. Launch the Raspberry Pi imager:
   - Select your Raspberry Pi model: **Raspberry Pi 5**
   - Click "Choose OS" → "Raspberry Pi OS (other)" → **"Raspberry Pi OS (Legacy, 64-bit) Full"**
   - **CRITICAL**: You MUST choose the Legacy version with Debian Bookworm. Do NOT use Trixie - the Hailo software is not compatible with it yet.
   - Select your SD card as the storage device
5. Before writing, click the settings gear icon (or press Ctrl+Shift+X):
   - Set hostname (e.g., `rpi5`)
   - Enable SSH
   - Set username and password
   - Configure WiFi credentials (optional but recommended)
6. Flash the operating system to the SD card and wait until it is completed.
7. Once flashed, safely eject the SD card from the reader.
8. Insert the SD card into the Raspberry Pi 5 (bottom of the board).
9. **Do NOT connect the AI HAT+ yet** - connect only:
   - Power supply (USB-C)
   - Micro HDMI cable to the **left port** (port closest to USB-C power)
   - Monitor via HDMI
   - Keyboard and mouse (USB)
10. Power on the Pi and wait for it to boot.
11. You should see the Raspberry Pi desktop appear on your monitor. If you see a solid green light or consistent blinking (about twice per second), the SD card may be faulty or incorrectly flashed - try reflashing or use a different SD card.
12. Connect to the internet via WiFi or Ethernet.
13. Verify the OS version by running:

```bash
cat /etc/os-release
```

You should see `VERSION_CODENAME=bookworm`. If it says `trixie`, you've flashed the wrong version.

# 3. Specialised Hardware Setup

Now that the Pi has been successfully booted and verified, we can connect the specialised hardware.

**AI Hat Installation**

1. Shut down the Pi completely:
```bash
sudo poweroff
```

2. Wait for the green light to stop completely, then unplug the power supply.

3. Disconnect the micro HDMI cable (makes the next steps easier).

4. Install the Active Cooler first:
   - Follow the instructions included in the box
   - Align the cooler correctly
   - Push in the stabilising pins into the Pi board
   - Connect the cable with yellow wire closest to the edge of the Pi

5. Prepare the AI HAT+:
   - Attach plastic spacers to the AI HAT+ mounting holes
   - Attach the GPIO extension headers to the Pi board

6. Install the AI HAT+:
   - Carefully lower the HAT onto the GPIO pins (keep the PCIe ribbon cable out of the way)
   - Push down gently until the GPIO pins are fully seated
   - Connect the PCIe ribbon cable:
     - One end goes to the AI HAT+
     - Other end goes to the Pi's PCIe port
     - Push the ribbon into the connector evenly, then press the clamp down
   - Tighten the spacer screws to secure the HAT

**Camera Installation**

7. Thread the camera adapter cable through the camera housing slit.

8. Connect the adapter ribbon to the camera module:
   - The wide end goes into the camera
   - The side with visible circuit traces faces the same direction as the lens
   - Push the ribbon in evenly, then close the clamp

9. Connect the other end to the Pi:
   - Insert into the camera port (between the two USB 3.0 ports)
   - The side with visible traces should face the USB ports
   - Push in evenly and close the clamp

10. Attach the camera housing to the swivel ball mount adapter.

11. Attach the swivel ball adapter to the tripod.

12. Reconnect the micro HDMI cable and power supply.

13. Power on the Pi - it should now boot normally with all hardware attached.

# 4. Specialised Software Setup

In this phase, we will verify hardware communication and install the Hailo software stack.

## Part A: System Preparation

1. First, ensure your Raspberry Pi OS is fully up-to-date:

```bash
sudo apt update
sudo apt full-upgrade -y
```

If a new kernel is installed, reboot:

```bash
sudo reboot
```

2. Verify firmware version (must be December 6, 2023 or later):

```bash
sudo rpi-eeprom-update
```

If the date shown is earlier than December 6, 2023, update it:

```bash
sudo raspi-config
```

Navigate to: `Advanced Options` → `Bootloader Version` → Select `Latest`

Exit and run:

```bash
sudo rpi-eeprom-update -a
sudo reboot
```

3. Configure PCIe for Gen 3 Speed (essential for full AI HAT+ performance):

```bash
sudo raspi-config
```

Navigate to: `6 Advanced Options` → `A8 PCIe Speed`

Select `Yes` to enable PCIe Gen 3 mode

Select `Finish` and choose to reboot

4. Verify the AI HAT+ is detected on PCIe:

```bash
lspci | grep Hailo
```

Expected output:
```
0001:01:00.0 Co-processor: Hailo Technologies Ltd. Hailo-8 AI Processor (rev 01)
```

If you don't see this, the HAT is not properly connected - power off and reseat it.

## Part B: Hailo Software Installation

The Hailo software requires manual installation of specific `.deb` files to ensure version compatibility.

1. Download the following files from [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) (requires free registration):
   - `hailort_4.23.0_arm64.deb` - HailoRT runtime for ARM64
   - `hailort-pcie-driver_4.23.0_all.deb` - PCIe driver

2. Transfer the files to your Pi (if downloaded on another computer):

```bash
# From your other computer (replace with your Pi's actual IP)
scp hailort_4.23.0_arm64.deb hailort-pcie-driver_4.23.0_all.deb patrick@192.168.0.39:/home/patrick/Downloads/
```

Or download directly on the Pi using a web browser.

3. Install HailoRT runtime:

```bash
cd ~/Downloads
sudo dpkg -i hailort_4.23.0_arm64.deb
```

When prompted "Do you wish to activate hailort service?", type `y` and press Enter.

4. Install the PCIe driver:

```bash
sudo dpkg -i hailort-pcie-driver_4.23.0_all.deb
```

When prompted about DKMS, type `Y` and press Enter.

**CRITICAL**: You must reboot after driver installation:

```bash
sudo reboot
```

## Part C: Verification and Permissions

1. Verify the driver version matches:

```bash
cat /sys/module/hailo_pci/version
```

Should show: `4.23.0`

2. Check the HailoRT service status:

```bash
systemctl status hailort.service
```

Should show: `Active: active (running)`

3. Verify hardware communication:

```bash
hailortcli scan
```

You should see:
```
Hailo Devices:
[-] Device: 0001:01:00.0
```

Note: The `[-]` symbol is normal at this stage - it indicates the device is detected but not actively running inference.

4. Confirm firmware version and chip details:

```bash
sudo hailortcli fw-control identify
```

Expected output:
```
Executing on device: 0001:01:00.0
Identifying board
Control Protocol Version: 2
Firmware Version: 4.23.0 (release,app,extended context switch buffer)
Logger Version: 0
Board Name: Hailo-8
Device Architecture: HAILO8L
```

5. Set up permissions for the Hailo device:

```bash
# Create hailo group (if it doesn't exist)
sudo groupadd hailo

# Add your user to the hailo group
sudo usermod -aG hailo $USER

# Set device ownership and permissions
sudo chown root:hailo /dev/hailo0
sudo chmod 660 /dev/hailo0
```

6. Apply the group changes (logout and login, or use newgrp):

```bash
newgrp hailo
```

7. Verify your user is in the hailo group:

```bash
groups
```

You should see `hailo` in the list.

## Part D: Running Pose Detection

The simplest way to run pose detection is using the built-in Raspberry Pi camera application with Hailo post-processing.

1. Verify the configuration file exists:

```bash
ls -l /usr/share/rpi-camera-assets/hailo_yolov8_pose.json
```

2. Run the pose detection demo:

```bash
rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolov8_pose.json
```

**Command breakdown:**
- `rpicam-hello` - Raspberry Pi camera application
- `-t 0` - Run indefinitely (until Ctrl+C)
- `--post-process-file` - Specifies the Hailo pose estimation configuration

3. You should see a live camera feed with pose estimation keypoints overlaid on detected people.

4. To stop the application, press `Ctrl+C` in the terminal.

## Troubleshooting

**Green light blinking during boot:**
- This indicates the Pi cannot boot from the SD card
- Try reflashing the SD card
- Ensure you're using a quality SD card (SanDisk recommended)
- Make sure the AI HAT+ is disconnected during first boot

**"Driver version mismatch" error:**
- This means the kernel module version doesn't match the HailoRT library
- Ensure you installed BOTH the hailort and hailort-pcie-driver .deb files
- Reboot after installing the PCIe driver
- Check versions match: `cat /sys/module/hailo_pci/version` and `hailortcli --version`

**Permission denied errors:**
- Ensure you've added your user to the hailo group
- Log out and back in (or use `newgrp hailo`)
- Check `/dev/hailo0` permissions: `ls -l /dev/hailo0`

**Camera not detected:**
- Verify camera ribbon is properly seated in both the camera and Pi
- Check `libcamera-hello` works: `libcamera-hello -t 5000`
- Ensure the ribbon is oriented correctly (contacts facing correct direction)

**PCIe not detected (lspci shows nothing):**
- Power off completely
- Reseat the PCIe ribbon cable on both ends
- Ensure the AI HAT+ is firmly pushed onto the GPIO pins
- Verify firmware is up to date (December 6, 2023 or later)
