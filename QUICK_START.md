# Quick Start Guide - CHAFON CF591 on Raspberry Pi

## Prerequisites

1. **Raspberry Pi** with Linux OS (Raspberry Pi OS recommended)
2. **CHAFON CF591** RFID reader connected via USB
3. **RFID tags** for testing

## Step 1: Connect the Device

1. Connect the CF591 reader to your Raspberry Pi via USB
2. Check if the device is detected:
   ```bash
   lsusb
   ```
   You should see a device related to CHAFON or USB serial adapter

3. Check the serial port:
   ```bash
   ls /dev/ttyUSB* /dev/ttyACM*
   ```
   Note the device name (e.g., `/dev/ttyUSB0`)

4. Set permissions (if needed):
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   ```
   Or add your user to the dialout group:
   ```bash
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

## Step 2: Determine Your Raspberry Pi Architecture

Check your Pi's architecture:
```bash
uname -m
```

- `armv7l` → Use **ARM** library (32-bit)
- `aarch64` → Use **ARM64** library (64-bit)

## Step 3: Install the Library

### Option A: System-wide Installation (Recommended)

```bash
# For ARM (32-bit)
sudo cp API/Linux/ARM/libCFApi.so /usr/local/lib/
sudo ldconfig

# For ARM64 (64-bit)
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig
```

### Option B: Local Installation

Set the library path:
```bash
export LD_LIBRARY_PATH=$PWD/API/Linux/ARM:$LD_LIBRARY_PATH
# Or for ARM64:
export LD_LIBRARY_PATH=$PWD/API/Linux/ARM64:$LD_LIBRARY_PATH
```

## Step 4: Compile and Run the C Example

### Using Makefile (Easiest)

```bash
# For ARM (32-bit) - default
make

# For ARM64 (64-bit)
make ARM64=1

# Run the program
./rfid_reader /dev/ttyUSB0
```

### Manual Compilation

```bash
# For ARM
gcc -o rfid_reader rfid_reader_example.c -lCFApi -L./API/Linux/ARM -I./API/Linux

# For ARM64
gcc -o rfid_reader rfid_reader_example.c -lCFApi -L./API/Linux/ARM64 -I./API/Linux

# Run
./rfid_reader /dev/ttyUSB0
```

## Step 5: Run the Python Example

```bash
# Make the script executable
chmod +x rfid_reader_python.py

# Run it
python3 rfid_reader_python.py /dev/ttyUSB0
```

Or use it as a module:
```python
from rfid_reader_python import RFIDReader

reader = RFIDReader('/dev/ttyUSB0', 115200)
reader.open()
reader.start_inventory()

while True:
    tag = reader.read_tag(timeout=1000)
    if tag:
        print(f"EPC: {tag['epc']}, RSSI: {tag['rssi']} dBm")

reader.close()
```

## Troubleshooting

### Problem: "Library not found"
**Solution:**
```bash
# Install library system-wide
sudo cp API/Linux/ARM/libCFApi.so /usr/local/lib/
sudo ldconfig

# Or set LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/path/to/library:$LD_LIBRARY_PATH
```

### Problem: "Permission denied" when opening device
**Solution:**
```bash
# Option 1: Change permissions temporarily
sudo chmod 666 /dev/ttyUSB0

# Option 2: Add user to dialout group (permanent)
sudo usermod -a -G dialout $USER
# Logout and login again
```

### Problem: "Device not found"
**Solution:**
1. Check USB connection: `lsusb`
2. Check if device appears: `ls /dev/tty*`
3. Try different USB ports
4. Check if device needs drivers (see `Drive/` folder)

### Problem: No tags detected
**Solution:**
1. Ensure tags are within range (typically 1-5 meters)
2. Check antenna connection
3. Verify power settings (may need to increase RF power)
4. Try different tags
5. Check frequency region settings match your location

### Problem: Compilation errors
**Solution:**
1. Ensure you're using the correct architecture (ARM vs ARM64)
2. Check that `CFApi.h` is in the include path
3. Verify `libCFApi.so` exists in the library path
4. Install build tools if needed: `sudo apt-get install build-essential`

## Next Steps

1. **Read the full documentation**: See `RASPBERRY_PI_README.md`
2. **Explore the API**: Check `API/Linux/CFApi.h` for all available functions
3. **Review sample code**: Look at `Sample/C#/` for more examples
4. **Customize**: Modify the examples to fit your needs

## Example Output

When running successfully, you should see output like:
```
CHAFON CF591 RFID Reader Example
================================
Port: /dev/ttyUSB0
Baud Rate: 115200

Opening device...
Device opened successfully!

Device Information:
  Firmware Version: V1.3.0
  Hardware Version: V1.0
  Serial Number: 1234567890AB

Starting inventory (tag reading)...
Press Ctrl+C to stop

Reading tags...
================================
Tag #1:
  EPC: E20034120118000000000000
  Length: 12 bytes
  RSSI: -45 dBm
  Antenna: 1
  Channel: 15
  CRC: 12 34
  PC: 00 00
---
```

## Support

For more information:
- Check the user manuals in `User Guide/`
- Review the API header file: `API/Linux/CFApi.h`
- Contact CHAFON support for hardware issues

