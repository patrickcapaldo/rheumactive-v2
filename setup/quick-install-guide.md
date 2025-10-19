# RheumActive v2 - Quick Installation Guide

This guide gets you from a fresh Raspberry Pi 5 with Hailo AI HAT+ to running pose detection in 10 minutes.

## Prerequisites Checklist

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

## Step 1: Download Required Files

1. Go to [Hailo Developer Zone](https://hailo.ai/developer-zone/software-downloads/) (requires free registration)

2. Download these files to your **Downloads** folder:
   - `hailort_4.23.0_arm64.deb`
   - `hailort-pcie-driver_4.23.0_all.deb`

3. Verify files are in the correct location:
   ```bash
   ls -lh ~/Downloads/*.deb
   ```
   
   You should see both `.deb` files listed.

## Step 2: Clone This Repository

```bash
cd ~
git clone https://github.com/patrickcapaldo/rheumactive-v2.git
cd rheumactive-v2
```

## Step 3: Make Scripts Executable

```bash
chmod +x scripts/setup/*.sh
chmod +x scripts/*.sh
```

## Step 4: Run Automated Installation

```bash
make full-install
```

This will:
- ✓ Check your system meets requirements
- ✓ Install HailoRT runtime
- ✓ Install PCIe driver
- ✓ Verify hardware communication
- ✓ Setup device permissions

**Expected duration**: 5-10 minutes

### What You'll See

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

## Step 5: Reboot

After installation completes, you'll see:

```
⚠⚠⚠ REBOOT REQUIRED ⚠⚠⚠
```

Reboot your system:

```bash
sudo reboot
```

## Step 6: Verify Installation (After Reboot)

```bash
cd ~/rheumactive-v2
make mark-reboot-done
make verify-install
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

## Step 7: Setup Permissions

```bash
make setup-permissions
```

**Important**: After this step, either:
- Log out and log back in, OR
- Run: `newgrp hailo`

## Step 8: Test Pose Detection! 🎉

```bash
./scripts/run_pose_detection.sh
```

You should see your camera feed with pose detection keypoints overlaid on any people in frame!

Press `Ctrl+C` to stop.

## Troubleshooting Quick Fixes

### "OS version wrong" error
You installed Trixie instead of Bookworm. Reflash with **Raspberry Pi OS (Legacy, 64-bit)**.

### "Hailo device not found"
1. Power off completely
2. Check AI HAT+ is firmly seated
3. Check PCIe ribbon cable connections
4. Power on and try again

### "Driver version mismatch"
```bash
sudo reboot
cd ~/rheumactive-v2
make verify-install
```

### "Permission denied" errors
```bash
newgrp hailo
# Or log out and back in
```

### Installation stuck or failed
```bash
make clean
make full-install
```

## Manual Installation (Alternative)

If you prefer to run steps individually:

```bash
# 1. System check
./scripts/setup/01_check_system.sh

# 2. Install HailoRT
./scripts/setup/02_install_hailort.sh ~/Downloads/hailort_4.23.0_arm64.deb

# 3. Install driver
./scripts/setup/03_install_driver.sh ~/Downloads/hailort-pcie-driver_4.23.0_all.deb

# 4. Reboot
sudo reboot

# 5. Verify
./scripts/setup/04_verify_install.sh

# 6. Permissions
./scripts/setup/05_setup_permissions.sh
newgrp hailo

# 7. Test
./scripts/run_pose_detection.sh
```

## What's Next?

After successful installation:

1. **Explore the application**:
   - Camera feed should show pose keypoints in real-time
   - Try different poses and movements

2. **Review documentation**:
   - Full setup guide: `docs/01-initial-setup.md`
   - Setup scripts: `scripts/setup/README.md`

3. **Start developing**:
   - Application code will go in `src/`
   - See project roadmap for features

## Getting Help

- **View all commands**: `make help`
- **Check specific step**: Run individual scripts in `scripts/setup/`
- **Review logs**: Check terminal output for error messages
- **System status**: `make verify-install` shows detailed status

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

## Success Indicators

You know it's working when:
- ✓ `make verify-install` shows all green checkmarks
- ✓ `hailortcli scan` shows `[-] Device: 0001:01:00.0`
- ✓ `./scripts/run_pose_detection.sh` shows camera feed with pose overlays
- ✓ No red error messages

## Installation Time Estimate

| Step | Duration |
|------|----------|
| Download .deb files | 2-3 min |
| Clone repository | < 1 min |
| Run full-install | 5-10 min |
| Reboot | 1-2 min |
| Verify + permissions | 1 min |
| **Total** | **10-15 minutes** |

---

**Ready to start?** Jump to [Step 1](#step-1-download-required-files)!
