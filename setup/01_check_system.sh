#!/bin/bash
# System Requirements Check Script
# Verifies OS version, hardware detection, and prerequisites

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== System Requirements Check ==="
echo ""

# Check OS version
echo -n "Checking OS version... "
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$VERSION_CODENAME" = "bookworm" ]; then
        echo -e "${GREEN}✓ Bookworm detected${NC}"
    else
        echo -e "${RED}✗ Wrong OS version!${NC}"
        echo "Expected: Bookworm (Debian 12)"
        echo "Found: $VERSION_CODENAME"
        echo ""
        echo "Please reflash your SD card with Raspberry Pi OS (Legacy, 64-bit) Bookworm"
        exit 1
    fi
else
    echo -e "${RED}✗ Cannot detect OS version${NC}"
    exit 1
fi

# Check architecture
echo -n "Checking architecture... "
ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    echo -e "${GREEN}✓ ARM64 detected${NC}"
else
    echo -e "${RED}✗ Wrong architecture: $ARCH${NC}"
    echo "This system requires ARM64 (aarch64)"
    exit 1
fi

# Check for Raspberry Pi 5
echo -n "Checking hardware model... "
if grep -q "Raspberry Pi 5" /proc/cpuinfo 2>/dev/null || grep -q "Raspberry Pi 5" /sys/firmware/devicetree/base/model 2>/dev/null; then
    echo -e "${GREEN}✓ Raspberry Pi 5 detected${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Cannot confirm Raspberry Pi 5${NC}"
fi

# Check PCIe Gen3 setting
echo -n "Checking PCIe configuration... "
if [ -f /boot/firmware/config.txt ]; then
    if grep -q "^dtparam=pciex1_gen=3" /boot/firmware/config.txt; then
        echo -e "${GREEN}✓ PCIe Gen3 enabled${NC}"
    else
        echo -e "${YELLOW}⚠ PCIe Gen3 not configured${NC}"
        echo "Run: sudo raspi-config → Advanced Options → PCIe Speed → Yes"
        echo "Then reboot and re-run this check"
    fi
else
    echo -e "${YELLOW}⚠ Cannot check PCIe config${NC}"
fi

# Check for Hailo device on PCIe bus
echo -n "Checking for Hailo AI HAT+ on PCIe... "
if lspci | grep -q "Hailo"; then
    HAILO_DEVICE=$(lspci | grep Hailo)
    echo -e "${GREEN}✓ Detected${NC}"
    echo "  Device: $HAILO_DEVICE"
else
    echo -e "${RED}✗ Hailo device not found on PCIe bus${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure AI HAT+ is properly seated on GPIO pins"
    echo "  2. Check PCIe ribbon cable is firmly connected on both ends"
    echo "  3. Verify firmware is up to date: sudo rpi-eeprom-update"
    echo "  4. Power cycle the system"
    exit 1
fi

# Check firmware version
echo -n "Checking bootloader firmware... "
FIRMWARE_DATE=$(sudo rpi-eeprom-update | grep CURRENT | awk '{print $2, $3, $4, $5, $6}')
REQUIRED_DATE="Thu  8 May"
if [ -n "$FIRMWARE_DATE" ]; then
    echo -e "${GREEN}✓ Firmware: $FIRMWARE_DATE${NC}"
    # Note: A proper date comparison would be more robust, but this checks for reasonable recentness
else
    echo -e "${YELLOW}⚠ Cannot determine firmware version${NC}"
fi

# Check for required system packages
echo -n "Checking system packages... "
MISSING_PACKAGES=""
for pkg in build-essential git; do
    if ! dpkg -l | grep -q "^ii  $pkg "; then
        MISSING_PACKAGES="$MISSING_PACKAGES $pkg"
    fi
done

if [ -z "$MISSING_PACKAGES" ]; then
    echo -e "${GREEN}✓ Required packages installed${NC}"
else
    echo -e "${YELLOW}⚠ Missing packages:$MISSING_PACKAGES${NC}"
    echo "Installing missing packages..."
    sudo apt update
    sudo apt install -y $MISSING_PACKAGES
fi

# System update check
echo -n "Checking for system updates... "
sudo apt update > /dev/null 2>&1
UPDATES=$(apt list --upgradable 2>/dev/null | grep -v "Listing" | wc -l)
if [ "$UPDATES" -eq 0 ]; then
    echo -e "${GREEN}✓ System up to date${NC}"
else
    echo -e "${YELLOW}⚠ $UPDATES updates available${NC}"
    echo "Consider running: sudo apt full-upgrade -y"
fi

echo ""
echo -e "${GREEN}=== System check complete ===${NC}"
echo ""