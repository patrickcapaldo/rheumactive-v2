#!/bin/bash
# Hailo Device Permissions Setup Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Setting Up Hailo Device Permissions ==="
echo ""

# Check if device exists
if [ ! -e /dev/hailo0 ]; then
    echo -e "${RED}Error: /dev/hailo0 not found${NC}"
    echo "Please ensure the Hailo driver is installed and loaded."
    exit 1
fi

# Create hailo group if it doesn't exist
echo -n "Checking hailo group... "
if getent group hailo > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}Creating...${NC}"
    sudo groupadd hailo
    echo -e "${GREEN}✓ Created${NC}"
fi

# Add current user to hailo group
echo -n "Adding $USER to hailo group... "
if groups $USER | grep -q "\bhailo\b"; then
    echo -e "${GREEN}✓ Already a member${NC}"
else
    sudo usermod -aG hailo $USER
    echo -e "${GREEN}✓ Added${NC}"
    echo -e "${YELLOW}⚠ You must log out and back in (or run 'newgrp hailo') for this to take effect${NC}"
fi

# Set device ownership
echo -n "Setting device ownership... "
sudo chown root:hailo /dev/hailo0
echo -e "${GREEN}✓ Done${NC}"

# Set device permissions
echo -n "Setting device permissions... "
sudo chmod 660 /dev/hailo0
echo -e "${GREEN}✓ Done${NC}"

# Create udev rule for persistent permissions
UDEV_RULE_FILE="/etc/udev/rules.d/99-hailo.rules"
echo -n "Creating udev rule for persistent permissions... "

sudo tee $UDEV_RULE_FILE > /dev/null << 'EOF'
# Hailo device permissions
# This ensures /dev/hailo0 has correct permissions on boot
KERNEL=="hailo0", GROUP="hailo", MODE="0660"
EOF

echo -e "${GREEN}✓ Created${NC}"
echo "  Location: $UDEV_RULE_FILE"

# Reload udev rules
echo -n "Reloading udev rules... "
sudo udevadm control --reload-rules
sudo udevadm trigger
echo -e "${GREEN}✓ Done${NC}"

# Verify current permissions
echo ""
echo "Current device status:"
ls -l /dev/hailo0

echo ""
echo "Current user groups:"
groups $USER

echo ""
echo -e "${GREEN}=== Permissions setup complete ===${NC}"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} If you just added yourself to the hailo group,"
echo "you need to log out and back in, or run: newgrp hailo"
echo ""