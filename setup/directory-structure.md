# RheumActive v2 - Setup Files Structure

This document shows the complete directory structure for the automated setup system.

## Directory Layout

```
rheumactive-v2/
├── Makefile                           # Main automation orchestrator
├── scripts/
│   ├── setup/
│   │   ├── README.md                  # Setup scripts documentation
│   │   ├── 01_check_system.sh        # System requirements verification
│   │   ├── 02_install_hailort.sh     # HailoRT runtime installation
│   │   ├── 03_install_driver.sh      # PCIe driver installation
│   │   ├── 04_verify_install.sh      # Installation verification
│   │   └── 05_setup_permissions.sh   # Device permissions setup
│   └── run_pose_detection.sh          # Pose detection runner (existing)
├── docs/
│   └── 01-initial-setup.md            # Complete setup documentation
├── .install_markers/                  # Installation progress tracking (auto-created)
│   ├── 01_system_check
│   ├── 02_hailo_install
│   ├── 03_driver_install
│   ├── 04_permissions
│   └── 05_needs_reboot
└── .gitignore                         # Should include .install_markers/

```

## File Purposes

### Root Level

**Makefile**
- Provides high-level commands for users
- Tracks installation progress
- Manages dependencies between steps
- Provides colored output and help text

### scripts/

**run_pose_detection.sh** (existing)
- Final application runner
- Uses absolute path to config file
- Includes preflight checks
- Run after setup is complete

### scripts/setup/

**README.md**
- Documentation for setup scripts
- Usage instructions
- Troubleshooting guide
- Manual installation steps

**01_check_system.sh**
- OS version validation (must be Bookworm)
- Architecture check (ARM64)
- Hardware detection (RPi 5, Hailo HAT+)
- PCIe Gen3 configuration check
- Firmware version verification
- System package verification

**02_install_hailort.sh**
- HailoRT runtime installation
- Service activation
- Dependency resolution
- Installation verification

**03_install_driver.sh**
- PCIe driver installation
- DKMS configuration
- Reboot requirement notification
- Installation verification

**04_verify_install.sh**
- Package verification
- Kernel module check
- Service status check
- Device detection
- CLI tool verification
- Firmware communication test
- Configuration file check

**05_setup_permissions.sh**
- Group creation/management
- User group assignment
- Device ownership configuration
- Udev rule creation
- Persistent permissions setup

### docs/

**01-initial-setup.md** (updated)
- Complete hardware setup guide
- Software installation instructions
- Verification steps
- Troubleshooting information

## Setup Files Permissions

All scripts must be executable:

```bash
chmod +x scripts/setup/*.sh
chmod +x scripts/run_pose_detection.sh
```

## .gitignore Additions

Add these lines to `.gitignore`:

```
# Installation progress markers
.install_markers/

# Downloaded Hailo packages
*.deb

# Backup files
*.bak
*~
```

## Installation Flow

```
User runs: make full-install
    ↓
Makefile checks: .install_markers/01_system_check
    ↓ (if not exists)
Runs: scripts/setup/01_check_system.sh
    ↓ (creates marker)
Makefile checks: .install_markers/02_hailo_install
    ↓ (if not exists)
Runs: scripts/setup/02_install_hailort.sh
    ↓ (creates marker)
Makefile checks: .install_markers/03_driver_install
    ↓ (if not exists)
Runs: scripts/setup/03_install_driver.sh
    ↓ (creates marker + reboot marker)
Makefile notifies: REBOOT REQUIRED
    ↓
User reboots system
    ↓
User runs: make mark-reboot-done
    ↓ (removes reboot marker)
User runs: make verify-install
    ↓
Runs: scripts/setup/04_verify_install.sh
    ↓
User runs: make setup-permissions
    ↓
Runs: scripts/setup/05_setup_permissions.sh
    ↓ (creates marker)
Installation complete!
    ↓
User runs: ./scripts/run_pose_detection.sh
```

## Quick Setup Commands

### Initial Installation
```bash
# From repository root
cd ~/rheumactive-v2

# Make scripts executable (if needed)
chmod +x scripts/setup/*.sh scripts/*.sh

# Run full installation
make full-install

# Reboot
sudo reboot

# After reboot, verify
make mark-reboot-done
make verify-install

# Setup permissions
make setup-permissions

# Test
./scripts/run_pose_detection.sh
```

### Re-running Steps
```bash
# Re-run system check
rm .install_markers/01_system_check
make check-system

# Re-run entire installation
make clean
make full-install
```

### Viewing Help
```bash
# See all available commands
make help

# View setup script documentation
cat scripts/setup/README.md
```

## Dependencies

### Between Scripts
- `02_install_hailort.sh` requires `01_check_system.sh` to pass
- `03_install_driver.sh` requires `02_install_hailort.sh` to complete
- `04_verify_install.sh` requires system reboot after `03_install_driver.sh`
- `05_setup_permissions.sh` can run anytime after `04_verify_install.sh`

### External Dependencies
- Downloaded `.deb` files in `~/Downloads/`:
  - `hailort_4.23.0_arm64.deb`
  - `hailort-pcie-driver_4.23.0_all.deb`
- Raspberry Pi OS Bookworm (Legacy, 64-bit)
- Properly connected Hailo AI HAT+
- Internet connection (for apt packages)

## File Modifications Required

### Create New Files
1. `Makefile` - at repository root
2. `scripts/setup/README.md`
3. `scripts/setup/01_check_system.sh`
4. `scripts/setup/02_install_hailort.sh`
5. `scripts/setup/03_install_driver.sh`
6. `scripts/setup/04_verify_install.sh`
7. `scripts/setup/05_setup_permissions.sh`

### Update Existing Files
1. `docs/01-initial-setup.md` - updated with corrections
2. `.gitignore` - add `.install_markers/` and `*.deb`

### Keep Existing
1. `scripts/run_pose_detection.sh` - no changes needed

## Testing the Setup

### Test Each Script Individually
```bash
# Test system check
./scripts/setup/01_check_system.sh

# Test HailoRT installation (with actual .deb file)
./scripts/setup/02_install_hailort.sh ~/Downloads/hailort_4.23.0_arm64.deb

# And so on...
```

### Test Makefile
```bash
# Test help
make help

# Test dry-run (if you add -n flag)
make -n full-install

# Test actual installation
make full-install
```

### Test Idempotency
```bash
# Run twice - second time should skip completed steps
make full-install
make full-install
```

## Backup Strategy

Before installation, users should backup:
```bash
# Backup current system state
sudo rpi-eeprom-backup

# Document current packages
dpkg -l > ~/package_list_before.txt

# Save current config
cp /boot/firmware/config.txt ~/config.txt.bak
```

## Next Steps After Setup

Once installation is complete and verified:
1. Test pose detection: `./scripts/run_pose_detection.sh`
2. Develop application code in `src/`
3. Add more scripts to `scripts/` as needed
4. Document application usage
5. Create deployment procedures
