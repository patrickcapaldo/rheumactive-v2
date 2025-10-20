#!/bin/bash
# Hailo Installation Verification Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Verifying Hailo Installation ==="
echo ""

FAILED=0

# Check HailoRT package
echo -n "Checking HailoRT package... "
if dpkg -l | grep -q "^ii  hailort "; then
    VERSION=$(dpkg -l | grep "^ii  hailort " | awk '{print $3}')
    echo -e "${GREEN}✓ Installed (version: $VERSION)${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILED=1
fi

# Check PCIe driver package
echo -n "Checking PCIe driver package... "
if dpkg -l | grep -q "^ii  hailort-pcie-driver "; then
    VERSION=$(dpkg -l | grep "^ii  hailort-pcie-driver " | awk '{print $3}')
    echo -e "${GREEN}✓ Installed (version: $VERSION)${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    FAILED=1
fi

# Check kernel module
echo -n "Checking kernel module... "
if lsmod | grep -q "hailo_pci"; then
    echo -e "${GREEN}✓ Loaded${NC}"
    
    # Check module version
    if [ -f /sys/module/hailo_pci/version ]; then
        MODULE_VERSION=$(cat /sys/module/hailo_pci/version)
        echo "  Module version: $MODULE_VERSION"
    fi
else
    echo -e "${RED}✗ Not loaded${NC}"
    echo "  The kernel module is not loaded. Did you reboot after driver installation?"
    FAILED=1
fi

# Check HailoRT service
echo -n "Checking HailoRT service... "
if systemctl is-active --quiet hailort.service; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "  Attempting to start service..."
    sudo systemctl start hailort.service
    if systemctl is-active --quiet hailort.service; then
        echo -e "${GREEN}  ✓ Service started${NC}"
    else
        echo -e "${RED}  ✗ Failed to start service${NC}"
        FAILED=1
    fi
fi

# Check device visibility
echo -n "Checking device on PCIe bus... "
if lspci | grep -q "Hailo"; then
    echo -e "${GREEN}✓ Detected${NC}"
    DEVICE=$(lspci | grep Hailo)
    echo "  $DEVICE"
else
    echo -e "${RED}✗ Not detected${NC}"
    FAILED=1
fi

# Check /dev/hailo0
echo -n "Checking device node... "
if [ -e /dev/hailo0 ]; then
    echo -e "${GREEN}✓ /dev/hailo0 exists${NC}"
    PERMS=$(ls -l /dev/hailo0)
    echo "  Permissions: $PERMS"
else
    echo -e "${RED}✗ /dev/hailo0 not found${NC}"
    FAILED=1
fi

# Check hailortcli
echo -n "Checking hailortcli command... "
if command -v hailortcli &> /dev/null; then
    echo -e "${GREEN}✓ Available${NC}"
    CLI_VERSION=$(hailortcli --version 2>&1 | grep "HailoRT-CLI version" | awk '{print $3}')
    echo "  CLI version: $CLI_VERSION"
else
    echo -e "${RED}✗ Not found${NC}"
    FAILED=1
fi

# Test device scan
echo -n "Testing device scan... "
if hailortcli scan &> /dev/null; then
    echo -e "${GREEN}✓ Scan successful${NC}"
    SCAN_OUTPUT=$(hailortcli scan)
    echo "$SCAN_OUTPUT" | sed 's/^/  /'
    
    # Note about [-] vs [+]
    if echo "$SCAN_OUTPUT" | grep -q "\[-\]"; then
        echo -e "${YELLOW}  Note: [-] indicates device detected but not actively running inference${NC}"
        echo "  This is normal at this stage."
    fi
else
    echo -e "${RED}✗ Scan failed${NC}"
    FAILED=1
fi

# Test firmware identification
echo -n "Testing firmware identification... "
if sudo hailortcli fw-control identify &> /dev/null; then
    echo -e "${GREEN}✓ Communication successful${NC}"
    FW_INFO=$(sudo hailortcli fw-control identify 2>&1)
    
    # Extract key information
    FW_VERSION=$(echo "$FW_INFO" | grep "Firmware Version:" | cut -d: -f2- | xargs)
    BOARD_NAME=$(echo "$FW_INFO" | grep "Board Name:" | cut -d: -f2- | xargs)
    DEVICE_ARCH=$(echo "$FW_INFO" | grep "Device Architecture:" | cut -d: -f2- | xargs)
    
    echo "  Firmware Version: $FW_VERSION"
    echo "  Board Name: $BOARD_NAME"
    echo "  Device Architecture: $DEVICE_ARCH"
else
    echo -e "${RED}✗ Communication failed${NC}"
    
    # Check for version mismatch
    ERROR_OUTPUT=$(sudo hailortcli fw-control identify 2>&1 || true)
    if echo "$ERROR_OUTPUT" | grep -q "Driver version mismatch"; then
        echo -e "${RED}  Error: Driver version mismatch detected${NC}"
        echo "  This usually means the kernel module version doesn't match the library version."
        echo "  Try rebooting the system."
    fi
    FAILED=1
fi

# Check camera configuration file
echo -n "Checking pose detection config... "
CONFIG_FILE="/usr/share/rpi-camera-assets/hailo_yolov8_pose.json"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✓ Found${NC}"
    echo "  Location: $CONFIG_FILE"
else
    echo -e "${YELLOW}⚠ Not found${NC}"
    echo "  The pose detection configuration file is missing."
    echo "  You may need to install: sudo apt install rpicam-apps-hailo-postprocess"
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}=== ✓ Installation verified successfully ===${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: make setup-permissions"
    echo "  2. Test pose detection: ./scripts/run_pose_detection.sh"
    exit 0
else
    echo -e "${RED}=== ✗ Verification failed ===${NC}"
    echo ""
    echo "Some checks failed. Please review the errors above."
    exit 1
fi