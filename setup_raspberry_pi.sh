#!/bin/bash
#
# CHAFON CF591 RFID Reader - Raspberry Pi Setup Script
#
# This script sets up the CHAFON CF591 RFID reader on Raspberry Pi
# Tested on: Raspberry Pi 5 with 64-bit OS
#
# Usage:
#   chmod +x setup_raspberry_pi.sh
#   ./setup_raspberry_pi.sh
#

set -e

echo "========================================"
echo "CHAFON CF591 RFID Reader Setup"
echo "========================================"
echo ""

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [ "$ARCH" = "aarch64" ]; then
    LIB_PATH="API/Linux/ARM64/libCFApi.so"
    echo "Using ARM64 library (64-bit)"
elif [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "armv6l" ]; then
    LIB_PATH="API/Linux/ARM/libCFApi.so"
    echo "Using ARM library (32-bit)"
else
    echo "Warning: Unknown architecture '$ARCH'"
    echo "Trying ARM64 library..."
    LIB_PATH="API/Linux/ARM64/libCFApi.so"
fi

# Check if library exists
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FULL_LIB_PATH="$SCRIPT_DIR/$LIB_PATH"

if [ ! -f "$FULL_LIB_PATH" ]; then
    echo "Error: Library not found at $FULL_LIB_PATH"
    exit 1
fi

echo ""
echo "Step 1: Installing library to /usr/local/lib/"
echo "-------------------------------------------------"

sudo cp "$FULL_LIB_PATH" /usr/local/lib/
echo "Library copied to /usr/local/lib/libCFApi.so"

echo ""
echo "Step 2: Running ldconfig"
echo "-------------------------------------------------"

sudo ldconfig
echo "Library cache updated"

echo ""
echo "Step 3: Setting up serial port permissions"
echo "-------------------------------------------------"

# Add user to dialout group for serial port access
if id -nG "$USER" | grep -qw "dialout"; then
    echo "User '$USER' is already in 'dialout' group"
else
    echo "Adding user '$USER' to 'dialout' group..."
    sudo usermod -a -G dialout "$USER"
    echo "Added! You'll need to logout and login for this to take effect."
fi

echo ""
echo "Step 4: Checking for USB serial device"
echo "-------------------------------------------------"

if ls /dev/ttyUSB* 2>/dev/null; then
    echo "USB serial device(s) found:"
    ls -la /dev/ttyUSB*
    
    # Set permissions on first USB device
    FIRST_USB=$(ls /dev/ttyUSB* 2>/dev/null | head -1)
    if [ -n "$FIRST_USB" ]; then
        sudo chmod 666 "$FIRST_USB"
        echo "Permissions set on $FIRST_USB"
    fi
elif ls /dev/ttyACM* 2>/dev/null; then
    echo "USB ACM device(s) found:"
    ls -la /dev/ttyACM*
    
    FIRST_ACM=$(ls /dev/ttyACM* 2>/dev/null | head -1)
    if [ -n "$FIRST_ACM" ]; then
        sudo chmod 666 "$FIRST_ACM"
        echo "Permissions set on $FIRST_ACM"
    fi
else
    echo "No USB serial devices found."
    echo "Please connect the CHAFON CF591 reader and run:"
    echo "  sudo chmod 666 /dev/ttyUSB0"
fi

echo ""
echo "Step 5: Verifying library installation"
echo "-------------------------------------------------"

if ldconfig -p | grep -q libCFApi; then
    echo "✓ Library is properly installed"
    ldconfig -p | grep libCFApi
else
    echo "✗ Library not found in ldconfig cache"
    echo "  Try running: sudo ldconfig"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Connect your CHAFON CF591 reader via USB"
echo "2. If you were added to 'dialout' group, logout and login"
echo "3. Test with: python3 chafon_cf591.py /dev/ttyUSB0 --info"
echo "4. Run examples: python3 examples.py"
echo ""
echo "Quick test command:"
echo "  python3 -c \"from chafon_cf591 import CF591Reader; r=CF591Reader('/dev/ttyUSB0'); r.open(); print(r.get_device_info()); r.close()\""
echo ""

