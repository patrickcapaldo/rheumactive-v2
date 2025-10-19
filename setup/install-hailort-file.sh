#!/bin/bash
# HailoRT Runtime Installation Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}Error: No .deb file specified${NC}"
    echo "Usage: $0 <path-to-hailort.deb>"
    exit 1
fi

DEB_FILE="$1"

echo "=== Installing HailoRT Runtime ==="
echo ""

# Check if file exists
if [ ! -f "$DEB_FILE" ]; then
    echo -e "${RED}Error: File not found: $DEB_FILE${NC}"
    echo ""
    echo "Please download hailort_4.23.0_arm64.deb from:"
    echo "https://hailo.ai/developer-zone/software-downloads/"
    echo ""
    echo "Save it to ~/Downloads/ and try again."
    exit 1
fi

echo "Installing: $(basename $DEB_FILE)"
echo ""

# Check if already installed
if dpkg -l | grep -q "^ii  hailort "; then
    INSTALLED_VERSION=$(dpkg -l | grep "^ii  hailort " | awk '{print $3}')
    echo -e "${YELLOW}⚠ HailoRT already installed (version: $INSTALLED_VERSION)${NC}"
    echo -n "Reinstall? [y/N] "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Skipping installation"
        exit 0
    fi
fi

# Install the package
echo "Installing HailoRT..."
sudo dpkg -i "$DEB_FILE"

# Fix any dependency issues
echo "Checking dependencies..."
sudo apt-get install -f -y

# Verify installation
if dpkg -l | grep -q "^ii  hailort "; then
    VERSION=$(dpkg -l | grep "^ii  hailort " | awk '{print $3}')
    echo ""
    echo -e "${GREEN}✓ HailoRT $VERSION installed successfully${NC}"
    
    # Check if service was activated
    if systemctl is-active --quiet hailort.service; then
        echo -e "${GREEN}✓ HailoRT service is running${NC}"
    else
        echo -e "${YELLOW}⚠ HailoRT service is not running${NC}"
        echo "Enabling and starting service..."
        sudo systemctl enable hailort.service
        sudo systemctl start hailort.service
    fi
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

echo ""
echo "=== HailoRT installation complete ==="
echo ""
