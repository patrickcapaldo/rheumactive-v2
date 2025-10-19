# Setup Guide - Part 2: Hailo Software Installation

This phase installs the necessary drivers and runtime for the Hailo AI HAT+.

## 1. System Update

First, ensure your Raspberry Pi OS is fully up-to-date.

```bash
sudo apt update
sudo apt upgrade -y
```

If a new kernel is installed, reboot your system:

```bash
sudo reboot
```

2. Configure PCIe for Gen 3 Speed

This is critical for getting full performance from the AI HAT.

	1. Run the Raspberry Pi configuration tool:
	```bash
	sudo raspi-config
	```
	2. Navigate to: `6 Advanced Options` → `A8 PCIe Speed`.
	3. Select `Yes` to enable PCIe Gen 3 mode.
	4. Select `Finish` and choose to reboot.

3. Install Hailo Software Stack

After rebooting, install the complete Hailo driver, runtime, and tools.

```bash
sudo apt install hailo-all -y
```

Once the installation is complete, reboot one more time to load the new driver and firmware.

```bash
sudo reboot
```

4. Verify Installation

After the final reboot, verify that the system can see the Hailo chip.

**Check 1: PCIe Bus**

```bash
lspci | grep Hailo
```

You must see this output (or similar): `0001:01:00.0 Co-processor: Hailo Technologies Ltd. Hailo-8 AI Processor (rev 01)`

**Check 2: Hailo Runtime**

```bash
hailortcli scan
```

You must see a successful output, like:

```
Executing on device: 0001:01:00.0
...
Firmware Version: 4.20.0 (release,app,extended context switch buffer)
Board Name: Hailo-8
Device Architecture: HAILO8L
...
```

If both checks pass, your software is correctly installed and you can proceed.
