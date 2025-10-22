# RheumActive v2 - Installation Makefile
# This automates the Hailo software stack installation on Raspberry Pi 5

.PHONY: all check-system install-hailo verify-install setup-permissions test-camera help clean

# Color output
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
NC=\033[0m # No Color

# Installation markers (to track completed steps)
MARKER_DIR := .install_markers
SYSTEM_CHECK_MARKER := $(MARKER_DIR)/01_system_check
HAILO_INSTALL_MARKER := $(MARKER_DIR)/02_hailo_install
DRIVER_INSTALL_MARKER := $(MARKER_DIR)/03_driver_install
PERMISSIONS_MARKER := $(MARKER_DIR)/04_permissions
REBOOT_MARKER := $(MARKER_DIR)/05_needs_reboot

# Hailo package versions
HAILORT_VERSION := 4.23.0
HAILORT_DEB := hailort_$(HAILORT_VERSION)_arm64.deb
DRIVER_DEB := hailort-pcie-driver_$(HAILORT_VERSION)_all.deb

# Download directory
DOWNLOADS_DIR := $(HOME)/Downloads

all: help

help:
	@echo "$(GREEN)RheumActive v2 - Automated Installation$(NC)"
	@echo ""
	@echo "Available targets:"
	@echo "  $(YELLOW)make check-system$(NC)         - Verify system requirements (OS version, hardware)"
	@echo "  $(YELLOW)make install-hailo$(NC)        - Install Hailo software (requires .deb files in ~/Downloads)"
	@echo "  $(YELLOW)make verify-install$(NC)       - Verify Hailo installation and firmware"
	@echo "  $(YELLOW)make setup-permissions$(NC)    - Configure device permissions"
	@echo "  $(YELLOW)make test-camera$(NC)           - Run a quick camera test"
	@echo "  $(YELLOW)make full-install$(NC)         - Run pre-reboot installation steps (check + install Hailo)"
	@echo "  $(YELLOW)make post-reboot-install$(NC)  - Run post-reboot installation steps (verify + permissions)"
	@echo "  $(YELLOW)make clean$(NC)                 - Remove installation markers (to re-run steps)"
	@echo "  $(YELLOW)make mark-reboot-done$(NC)     - Clear reboot marker after rebooting"
	@echo ""
	@echo "$(RED)IMPORTANT:$(NC) Before running 'make install-hailo', download these files"
	@echo "from https://hailo.ai/developer-zone/software-downloads/ to ~/Downloads/:"
	@echo "  - $(HAILORT_DEB)"
	@echo "  - $(DRIVER_DEB)"

# Full installation workflow
full-install: check-system install-hailo
	@echo "$(GREEN)✓ Pre-reboot installation steps complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Reboot your system: sudo reboot"
	@echo "  2. After reboot, run: make post-reboot-install"

post-reboot-install: verify-install setup-permissions
	@echo "$(GREEN)✓ Post-reboot installation steps complete!$(NC)"
	@echo ""
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Test pose detection: ./scripts/run_pose_detection.sh"

# System requirements check
check-system: $(SYSTEM_CHECK_MARKER)

$(SYSTEM_CHECK_MARKER):
	@echo "$(YELLOW)Setting script permissions...$(NC)"
	@chmod +x setup/*.sh scripts/run_pose_detection.sh
	@echo "$(YELLOW)Checking system requirements...$(NC)"
	@mkdir -p $(MARKER_DIR)
	@./setup/01_check_system.sh
	@touch $(SYSTEM_CHECK_MARKER)
	@echo "$(GREEN)✓ System check passed$(NC)"

# Hailo software installation
install-hailo: check-system $(HAILO_INSTALL_MARKER) $(DRIVER_INSTALL_MARKER)

$(HAILO_INSTALL_MARKER):
	@echo "$(YELLOW)Installing HailoRT runtime...$(NC)"
	@./setup/02_install_hailort.sh $(DOWNLOADS_DIR)/$(HAILORT_DEB)
	@touch $(HAILO_INSTALL_MARKER)
	@echo "$(GREEN)✓ HailoRT runtime installed$(NC)"

$(DRIVER_INSTALL_MARKER): $(HAILO_INSTALL_MARKER)
	@echo "$(YELLOW)Installing PCIe driver...$(NC)"
	@./setup/03_install_driver.sh $(DOWNLOADS_DIR)/$(DRIVER_DEB)
	@touch $(DRIVER_INSTALL_MARKER)
	@touch $(REBOOT_MARKER)
	@echo "$(GREEN)✓ PCIe driver installed$(NC)"
	@echo "$(RED)⚠ REBOOT REQUIRED$(NC) - Run 'sudo reboot' now, then run 'make post-reboot-install'"

# Verification
verify-install: $(DRIVER_INSTALL_MARKER)
	@if [ -f $(REBOOT_MARKER) ]; then \
		echo "$(RED)ERROR: You must reboot before verification!$(NC)"; \
		echo "Run: sudo reboot"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Verifying Hailo installation...$(NC)"
	@./setup/04_verify_install.sh
	@echo "$(GREEN)✓ Installation verified successfully$(NC)"

# Permission setup
setup-permissions: $(PERMISSIONS_MARKER)

$(PERMISSIONS_MARKER):
	@echo "$(YELLOW)Setting up device permissions...$(NC)"
	@./setup/05_setup_permissions.sh
	@touch $(PERMISSIONS_MARKER)
	@echo "$(GREEN)✓ Permissions configured$(NC)"
	@echo "$(YELLOW)Note: You may need to log out and back in for group changes to take effect$(NC)"

# Camera test
test-camera:
	@echo "$(YELLOW)Running 5-second camera test...$(NC)"
	@libcamera-hello -t 5000
	@echo "$(GREEN)✓ Camera test complete$(NC)"

# Clean markers (allows re-running installation)
clean:
	@echo "$(YELLOW)Removing installation markers...$(NC)"
	@rm -rf $(MARKER_DIR)
	@echo "$(GREEN)✓ Markers removed$(NC)"

# Mark reboot as complete (run this after rebooting)
mark-reboot-done:
	@rm -f $(REBOOT_MARKER)
	@echo "$(GREEN)✓ Reboot marker cleared$(NC)"