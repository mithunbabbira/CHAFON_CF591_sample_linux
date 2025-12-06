#!/bin/bash
# Setup persistent device name for RFID reader
# This script automatically finds your RFID reader and creates a udev rule

echo "=========================================="
echo "RFID Reader Persistent Device Setup"
echo "=========================================="
echo ""

# Find RFID reader device
echo "Finding RFID reader device..."
DEVICE=$(ls /dev/ttyUSB* 2>/dev/null | head -1)

if [ -z "$DEVICE" ]; then
    echo "✗ Error: No ttyUSB device found."
    echo "  Please connect your RFID reader and try again."
    exit 1
fi

echo "✓ Device found: $DEVICE"
echo ""

# Get device information
echo "Getting device information..."
SERIAL=$(udevadm info --name=$DEVICE 2>/dev/null | grep "ID_SERIAL_SHORT=" | cut -d'=' -f2)
VENDOR=$(udevadm info --name=$DEVICE 2>/dev/null | grep "ID_VENDOR_ID=" | cut -d'=' -f2)

if [ -z "$SERIAL" ]; then
    echo "✗ Error: Could not get device serial number."
    echo "  Device information:"
    udevadm info --name=$DEVICE 2>/dev/null | grep -E "(ID_SERIAL|ID_VENDOR|ID_MODEL)"
    exit 1
fi

if [ -z "$VENDOR" ]; then
    VENDOR="0403"  # Default FTDI vendor ID
fi

echo "✓ Device serial number: $SERIAL"
echo "✓ Vendor ID: $VENDOR"
echo ""

# Create udev rule
echo "Creating udev rule..."
RULE_FILE="/etc/udev/rules.d/99-rfid-reader.rules"
RULE="SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"$VENDOR\", ATTRS{idSerial}==\"$SERIAL\", SYMLINK+=\"rfid_reader\", MODE=\"0666\""

sudo bash -c "echo '$RULE' > $RULE_FILE"

if [ $? -ne 0 ]; then
    echo "✗ Error: Failed to create udev rule. Please run with sudo."
    exit 1
fi

echo "✓ Udev rule created: $RULE_FILE"
echo "  Rule content: $RULE"
echo ""

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

if [ $? -ne 0 ]; then
    echo "✗ Error: Failed to reload udev rules."
    exit 1
fi

echo "✓ Udev rules reloaded"
echo ""

# Wait a moment for symlink to be created
sleep 1

# Check if symlink exists
if [ -L /dev/rfid_reader ]; then
    echo "✓ Symlink created successfully!"
    ls -l /dev/rfid_reader
else
    echo "⚠ Symlink not created yet."
    echo "  Please unplug and replug your RFID reader, then run:"
    echo "    ls -l /dev/rfid_reader"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Your RFID reader will now always be available as: /dev/rfid_reader"
echo ""
echo "To verify, unplug and replug your device, then check:"
echo "  ls -l /dev/rfid_reader"
echo ""
echo "The script will automatically use this device if it exists."

