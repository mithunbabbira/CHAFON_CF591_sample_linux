# Setting Up Persistent Device Name for RFID Reader

## Problem
Linux assigns USB serial device numbers (ttyUSB0, ttyUSB1, etc.) based on detection order, not physical port. When you unplug/replug the device, the number can change. This makes it difficult to use the same script on different systems or after replugging.

## Solution: Create Persistent Symlink

This setup creates a permanent symlink `/dev/rfid_reader` that always points to your RFID reader, regardless of which ttyUSB number it gets assigned.

### Step 1: Find Your Device

First, connect your RFID reader and find which device it's using:

```bash
ls /dev/ttyUSB*
```

You should see something like `/dev/ttyUSB0`, `/dev/ttyUSB1`, or `/dev/ttyUSB2`.

### Step 2: Get Device Information

Get the unique serial number and vendor information:

```bash
# Replace ttyUSB0 with your actual device
udevadm info --name=/dev/ttyUSB0 | grep -E "(ID_SERIAL_SHORT|ID_VENDOR_ID|ID_MODEL_ID)"
```

**Important:** Note the `ID_SERIAL_SHORT` value (e.g., `FTB6SPL3`). This is unique to your device and will be used in the udev rule.

Example output:
```
E: ID_SERIAL_SHORT=FTB6SPL3
E: ID_VENDOR_ID=0403
E: ID_MODEL_ID=6001
```

### Step 3: Create Udev Rule

Create the udev rule file (replace `FTB6SPL3` with your device's `ID_SERIAL_SHORT` value):

```bash
sudo nano /etc/udev/rules.d/99-rfid-reader.rules
```

Add this line (replace `FTB6SPL3` with your device's serial number from Step 2):
```
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idSerial}=="FTB6SPL3", SYMLINK+="rfid_reader", MODE="0666"
```

**Or use this one-liner** (replace `FTB6SPL3` with your serial number):
```bash
sudo bash -c 'echo "SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"0403\", ATTRS{idSerial}==\"FTB6SPL3\", SYMLINK+=\"rfid_reader\", MODE=\"0666\"" > /etc/udev/rules.d/99-rfid-reader.rules'
```

### Step 4: Reload Udev Rules

Apply the new rule:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Step 5: Verify Setup

Unplug and replug your RFID reader, then check if the symlink was created:

```bash
ls -l /dev/rfid_reader
```

You should see output like:
```
lrwxrwxrwx 1 root root 10 Dec  6 18:45 /dev/rfid_reader -> ttyUSB2
```

The symlink should point to whatever ttyUSB number your device currently has.

### Step 6: Test

Run the script without specifying a port - it should automatically find `/dev/rfid_reader`:

```bash
python3 rfid_trigger_read.py
```

## Quick Setup Script

For convenience, here's a script to automate the setup (save as `setup_rfid_device.sh`):

```bash
#!/bin/bash
# Setup persistent device name for RFID reader

echo "Finding RFID reader device..."
DEVICE=$(ls /dev/ttyUSB* 2>/dev/null | head -1)

if [ -z "$DEVICE" ]; then
    echo "Error: No ttyUSB device found. Please connect your RFID reader."
    exit 1
fi

echo "Device found: $DEVICE"
echo "Getting device information..."

SERIAL=$(udevadm info --name=$DEVICE 2>/dev/null | grep "ID_SERIAL_SHORT=" | cut -d'=' -f2)

if [ -z "$SERIAL" ]; then
    echo "Error: Could not get device serial number."
    exit 1
fi

echo "Device serial number: $SERIAL"
echo "Creating udev rule..."

sudo bash -c "echo 'SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"0403\", ATTRS{idSerial}==\"$SERIAL\", SYMLINK+=\"rfid_reader\", MODE=\"0666\"' > /etc/udev/rules.d/99-rfid-reader.rules"

echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "Setup complete! Please unplug and replug your device, then run:"
echo "  ls -l /dev/rfid_reader"
echo ""
echo "The device should now always be available as /dev/rfid_reader"
```

Make it executable and run:
```bash
chmod +x setup_rfid_device.sh
./setup_rfid_device.sh
```

## Alternative: Auto-Detection

The script now includes auto-detection that will find the RFID reader automatically by:
1. Checking for `/dev/rfid_reader` symlink (if udev rule is set up)
2. Scanning for FTDI devices (vendor ID 0403)
3. Falling back to the first available ttyUSB device

So you can use the script without setting up the persistent name, but the persistent name is recommended for reliability.

## Troubleshooting

**Symlink not created after replugging:**
- Check the rule file: `cat /etc/udev/rules.d/99-rfid-reader.rules`
- Verify serial number matches: `udevadm info --name=/dev/ttyUSB0 | grep ID_SERIAL_SHORT`
- Check udev logs: `sudo journalctl -u systemd-udevd | tail -20`

**Permission denied errors:**
- The rule includes `MODE="0666"` which should give read/write access to all users
- If issues persist, try: `sudo chmod 666 /dev/rfid_reader`

**Multiple RFID readers:**
- Each reader needs its own udev rule with its unique serial number
- You can create multiple symlinks like `/dev/rfid_reader_1`, `/dev/rfid_reader_2`, etc.

