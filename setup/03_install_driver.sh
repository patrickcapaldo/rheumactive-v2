#!/bin/bash
# Hailo PCIe Driver Installation Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}Error: No .deb file specified${NC}"
    echo "Usage: $0 <path-to-driver.deb>"
    exit 1
fi

DEB_FILE="$1"

echo "=== Installing Hailo PCIe Driver ==="
echo ""

# Check if file exists
if [ ! -f "$DEB_FILE" ]; then
    echo -e "${RED}Error: File not found: $DEB_FILE${NC}"
    echo ""
    echo "Please download hailort-pcie-driver_4.23.0_all.deb from:"
    echo "https://hailo.ai/developer-zone/software-downloads/"
    echo ""
    echo "Save it to ~/Downloads/ and try again."
    exit 1
fi

echo "Installing: $(basename $DEB_FILE)"
echo ""

# Check if already installed
if dpkg -l | grep -q "^ii  hailort-pcie-driver ";
then
    INSTALLED_VERSION=$(dpkg -l | grep "^ii  hailort-pcie-driver " | awk '{print $3}')
    echo -e "${YELLOW}⚠ PCIe driver already installed (version: $INSTALLED_VERSION)${NC}"
    echo -n "Reinstall? [y/N] "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping installation"
        exit 0
    fi
fi

# Install the package
echo "Installing PCIe driver..."
echo -e "${YELLOW}Note: You may be prompted about DKMS. Answer 'Y' to use DKMS.${NC}"
echo ""
sudo dpkg -i "$DEB_FILE"

# Fix any dependency issues
echo "Checking dependencies..."
sudo apt-get install -f -y

# Verify installation
if dpkg -l | grep -q "^ii  hailort-pcie-driver "; then
    VERSION=$(dpkg -l | grep "^ii  hailort-pcie-driver " | awk '{print $3}')
    echo ""
    echo -e "${GREEN}✓ PCIe driver $VERSION installed successfully${NC}"
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

echo ""
echo -e "${RED}⚠⚠⚠ REBOOT REQUIRED ⚠⚠⚠${NC}"
echo ""
echo "The kernel module will not be loaded until you reboot."
echo "After rebooting, run: make verify-install"
echo ""
echo "=== PCIe driver installation complete ==="
echo ""