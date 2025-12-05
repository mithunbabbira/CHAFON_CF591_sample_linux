# CHAFON CF591 RFID Reader - Complete Guide for Raspberry Pi 5

Complete Python implementation for the CHAFON CF591 UHF RFID reader on Raspberry Pi 5.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [All Programmatic Operations](#all-programmatic-operations)
8. [Troubleshooting](#troubleshooting)
9. [Power and Range Control](#power-and-range-control)

---

## Overview

### What is the CHAFON CF591?

The CHAFON CF591 is a **UHF RFID reader/writer** that can read passive RFID tags from a distance (typically 1-10 meters depending on power settings).

**Key Features:**
- **Reading Range**: 1-10 meters (adjustable via power settings)
- **Connection**: USB (appears as `/dev/ttyUSB0` or `/dev/ttyACM0`)
- **Frequency**: UHF 860-960 MHz (region dependent)
- **Protocols**: ISO 18000-6C (EPC Gen2), ISO 18000-6B, GB/T 29768
- **Reading Speed**: Multiple tags per second
- **Antennas**: Supports up to 8 antennas (hardware dependent)

### What This Package Provides

✅ **Trigger-based reading** - Start and stop reading on demand  
✅ **Auto-stop on first tag** - Automatically stops after detecting one tag  
✅ **Configurable range** - Adjust reading distance from 1-10 meters  
✅ **Simple Python API** - Easy integration into existing applications  
✅ **Complete documentation** - Everything you need to know  
✅ **Working examples** - 12 integration examples ready to use  

---

## Quick Start

### 1. Hardware Setup

```bash
# Connect CHAFON CF591 to Raspberry Pi 5 via USB

# Check connection
lsusb
ls /dev/ttyUSB*

# Set permissions
sudo chmod 666 /dev/ttyUSB0
```

### 2. Install Library

```bash
# For Raspberry Pi 5 (ARM64)
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig

# Install HID dependency (if needed)
sudo apt-get install -y libhidapi-libusb0
sudo ln -sf /usr/lib/aarch64-linux-gnu/libhidapi-libusb.so.0 /usr/lib/aarch64-linux-gnu/libhid.so
sudo ldconfig
```

### 3. Test

```bash
python3 examples.py
```

### 4. Use in Your Code

```python
from chafon_cf591 import CF591Reader

# Simplest usage - trigger-based reading
with CF591Reader('/dev/ttyUSB0') as reader:
    # This starts, reads ONE tag, then stops automatically
    tag = reader.read_single_tag(timeout=5000)
    
    if tag:
        print(f"Tag: {tag.epc}")
        # Your logic here
```

**That's it!** See [Examples](#examples) section for more patterns.

---

## Installation

### Step 1: Connect Hardware

```bash
# Check if device is connected
lsusb

# Check serial port
ls /dev/ttyUSB* /dev/ttyACM*

# Set permissions (temporary)
sudo chmod 666 /dev/ttyUSB0

# Or add user to dialout group (permanent)
sudo usermod -a -G dialout $USER
# Then logout and login
```

### Step 2: Install Library Files

```bash
# Copy library to system
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig

# Verify installation
ldconfig -p | grep CFApi
```

### Step 3: Install Dependencies

If you get `libhid.so: cannot open shared object file` error:

```bash
# Install HID library
sudo apt-get install -y libhidapi-libusb0

# Create symlink
sudo ln -sf /usr/lib/aarch64-linux-gnu/libhidapi-libusb.so.0 /usr/lib/aarch64-linux-gnu/libhid.so

# Update library cache
sudo ldconfig

# Verify
python3 -c "from chafon_cf591 import CF591Reader; print('Success!')"
```

---

## Basic Usage

### Requirement 1: Trigger-Based Reading

```python
from chafon_cf591 import CF591Reader

with CF591Reader('/dev/ttyUSB0') as reader:
    # Wait for your trigger (button, web request, etc.)
    # Then start reading
    tag = reader.read_single_tag(timeout=10000)
    
    if tag:
        print(f"Tag detected: {tag.epc}")
```

### Requirement 2: Stop on First Tag

```python
# read_single_tag() automatically stops after first tag
tag = reader.read_single_tag(timeout=5000)

# Reading has stopped - you can now process the tag
if tag:
    process_tag(tag.epc)
```

### Requirement 3: Set Reading Range

```python
# Method 1: Set power directly (0-30)
reader.set_rf_power(5)    # Short range (~1-2m)
reader.set_rf_power(15)   # Medium range (~5m)
reader.set_rf_power(30)   # Maximum range (~10m)

# Method 2: Use helper function
reader.set_rf_power_for_range(3)   # ~3 meters
reader.set_rf_power_for_range(5)   # ~5 meters
reader.set_rf_power_for_range(10)  # ~10 meters
```

---

## API Reference

### CF591Reader Class

#### Initialization

```python
reader = CF591Reader(port='/dev/ttyUSB0', baud_rate=115200, auto_connect=False)
```

#### Connection Management

```python
reader.open()                    # Open connection
reader.close()                    # Close connection
reader.is_open                    # Check if connected

# Context manager (recommended)
with CF591Reader('/dev/ttyUSB0') as reader:
    # Use reader
    pass
```

#### Tag Reading

```python
# Trigger-based: Read one tag then stop
tag = reader.read_single_tag(timeout=5000)

# Continuous reading
reader.start_inventory()
tag = reader.get_tag(timeout=1000)
reader.stop_inventory()

# Read multiple tags
tags = reader.read_tags(max_tags=100, timeout=1000, max_timeouts=3)

# Iterator approach
reader.start_inventory()
for tag in reader.read_tags_iterator(max_count=10):
    print(tag.epc)
reader.stop_inventory()
```

#### Power and Range Control

```python
# Get/set RF power (0-30)
power = reader.get_rf_power()
reader.set_rf_power(20)

# Get/set antenna power
ant_power = reader.get_antenna_power()
reader.set_antenna_power(antenna=1, power=20)
```

#### Device Information

```python
# Device info
info = reader.get_device_info()
# Returns: {'firmware_version', 'hardware_version', 'serial_number'}

# Device parameters
params = reader.get_device_parameters()
# Returns: {'rf_power', 'region', 'q_value', 'work_mode', 'antenna_mask', ...}

# Frequency settings
freq = reader.get_frequency()
# Returns: {'region', 'start_freq', 'stop_freq', 'step_freq', 'channel_count'}

# Temperature
temp = reader.get_temperature()
# Returns: {'current', 'limit'}
```

#### Tag Operations

```python
# Read tag memory (requires tag to be in range)
tid = reader.read_tag_memory(MemoryBank.TID, 0, 6, epc=tag.epc_bytes)
epc = reader.read_tag_memory(MemoryBank.EPC, 0, 8, epc=tag.epc_bytes)
user = reader.read_tag_memory(MemoryBank.USER, 0, 4, epc=tag.epc_bytes)

# Write tag memory
reader.write_tag_memory(MemoryBank.USER, 0, data, epc=tag.epc_bytes)

# Lock/unlock tag
reader.lock_tag(LockArea.USER, LockAction.LOCK, password)

# Kill tag
reader.kill_tag(kill_password)
```

#### Tag Filtering

```python
# Filter by EPC prefix
reader.filter_by_epc_prefix(epc_prefix_bytes)

# Clear filter
reader.clear_filter()

# Set custom select mask
reader.set_select_mask(mask_ptr, mask_bits, mask_data)
```

### Tag Object

```python
tag.epc              # EPC code as hex string
tag.epc_bytes        # EPC as raw bytes
tag.rssi             # Signal strength in dBm
tag.antenna          # Antenna number (1-4)
tag.channel          # Frequency channel
tag.crc              # CRC as hex string
tag.pc               # Protocol Control as hex string
tag.length           # EPC length in bytes
tag.sequence         # Tag sequence number
```

---

## Examples

### Example 1: Basic Tag Reading

```python
from chafon_cf591 import CF591Reader

with CF591Reader('/dev/ttyUSB0') as reader:
    print("Reading tags for 5 seconds...")
    
    reader.start_inventory()
    
    start_time = time.time()
    while (time.time() - start_time) < 5:
        tag = reader.get_tag(timeout=500)
        if tag:
            print(f"Tag EPC: {tag.epc} | RSSI: {tag.rssi:.1f} dBm")
    
    reader.stop_inventory()
```

### Example 2: Trigger-Based Reading (Your Main Use Case)

```python
from chafon_cf591 import CF591Reader

with CF591Reader('/dev/ttyUSB0') as reader:
    print("Waiting for a tag (5 second timeout)...")
    
    # This is the key function for trigger-based reading!
    tag = reader.read_single_tag(timeout=5000)
    
    if tag:
        print(f"Tag detected!")
        print(f"EPC: {tag.epc}")
        print(f"RSSI: {tag.rssi:.1f} dBm")
        print(f"Antenna: {tag.antenna}")
    else:
        print("No tag detected within timeout")
```

### Example 3: Range Control

```python
from chafon_cf591 import CF591Reader

with CF591Reader('/dev/ttyUSB0') as reader:
    # Get current power
    current_power = reader.get_rf_power()
    print(f"Current RF power: {current_power} dBm")
    
    # Test different power levels
    for power in [10, 20, 30]:
        reader.set_rf_power(power)
        print(f"\nPower set to {power} dBm")
        
        tag = reader.read_single_tag(timeout=2000)
        if tag:
            print(f"Tag found at RSSI: {tag.rssi:.1f} dBm")
    
    # Restore original power
    reader.set_rf_power(current_power)
```

### Example 4: Application Integration

```python
from chafon_cf591 import CF591Reader

def main():
    reader = CF591Reader('/dev/ttyUSB0')
    
    try:
        reader.open()
        reader.set_rf_power(15)  # Medium range
        
        print("Application ready. Waiting for triggers...")
        
        while True:
            # Wait for trigger (e.g., button press, web request, etc.)
            user_input = input("\nPress Enter to scan RFID (or 'q' to quit): ")
            
            if user_input == 'q':
                break
            
            # Trigger: Read tag
            print("Reading RFID tag...")
            tag = reader.read_single_tag(timeout=10000)
            
            if tag:
                # Process tag
                process_tag(tag.epc)
            else:
                print("No tag detected")
    
    finally:
        reader.close()

def process_tag(epc):
    """Your tag processing logic"""
    print(f"Processing tag: {epc}")
    # Add your logic here:
    # - Database lookup
    # - API call
    # - Update inventory
    # - Grant access
    # etc.

if __name__ == '__main__':
    main()
```

### Example 5: Access Control System

```python
from chafon_cf591 import CF591Reader

# Authorized tags
AUTHORIZED_TAGS = {
    'E20034120118000000000001': 'Alice',
    'E20034120118000000000002': 'Bob',
    'E20034120118000000000003': 'Charlie',
}

with CF591Reader('/dev/ttyUSB0') as reader:
    # Use lower power for close-range access control
    reader.set_rf_power(15)
    
    print("Access Control System Active")
    print("Present your tag (10 seconds)...\n")
    
    start_time = time.time()
    while (time.time() - start_time) < 10:
        tag = reader.read_single_tag(timeout=1000)
        
        if tag:
            epc = tag.epc
            if epc in AUTHORIZED_TAGS:
                user = AUTHORIZED_TAGS[epc]
                print(f"✓ ACCESS GRANTED: Welcome, {user}!")
                # In real use: activate relay, open door, etc.
            else:
                print(f"✗ ACCESS DENIED: Unknown tag {epc}")
            
            time.sleep(1)  # Debounce
```

**More examples**: Run `python3 examples.py` for 12 interactive examples.

---

## All Programmatic Operations

### 1. Device Connection

- `OpenDevice()` - Connect via serial port
- `OpenNetConnection()` - Connect via TCP/IP (network models)
- `OpenHidConnection()` - Connect via USB HID interface
- `CloseDevice()` - Disconnect

### 2. Device Information

- `GetInfo()` - Firmware, hardware version, serial number
- `GetDeviceInfo()` - Extended device information
- `GetDevicePara()` - All configuration parameters
- `SetDevicePara()` - Configure device settings

### 3. Tag Reading (Primary Functions)

- `InventoryContinue()` - Start continuous tag reading
- `GetTagUii()` - Get tag information (EPC, RSSI, antenna)
- `InventoryStop()` - Stop tag reading

**Tag Information Returned:**
- EPC Code (unique tag ID)
- RSSI (signal strength in dBm)
- Antenna number that detected the tag
- Frequency channel used
- CRC and PC bytes
- Tag sequence number

### 4. Tag Operations

- `ReadTag()` - Read tag memory (EPC, TID, USER, Reserved banks)
- `WriteTag()` - Write data to tag memory
- `LockTag()` - Lock/unlock tag memory areas
- `KillTag()` - Permanently disable a tag

### 5. Power and Range Control

- `GetRFPower()` - Get current RF power level (0-30)
- `SetRFPower()` - Set RF power level (controls range)
- `GetAntPower()` - Get individual antenna power settings
- `SetAntPower()` - Set power per antenna (fine control)

### 6. Frequency Configuration

- `GetFreq()` - Get frequency settings
- `SetFreq()` - Set frequency (must match regional regulations)

### 7. Antenna Configuration

- `GetAntenna()` - Get active antenna configuration
- `SetAntenna()` - Select which antennas to use (bitmask)

### 8. Tag Filtering

- `SetSelectMask()` - Filter tags by EPC pattern
- `GetPermissonPara()` - Get access permission settings
- `SetPermissonPara()` - Set access codes and filters

### 9. GPIO and Trigger Configuration

- `GetGpioPara()` - Get GPIO configuration
- `SetGpioPara()` - Configure GPIO for triggers and outputs

**Trigger Modes:**
- Mode 0: No trigger (continuous reading)
- Mode 1: External trigger (GPIO input)
- Mode 2: Software trigger
- Mode 3: Auto-trigger with timer

### 10. Advanced Operations

- `GetCoilPRM()` / `SetCoilPRM()` - Q value configuration
- `QueryCfgGet()` / `QueryCfgSet()` - Query parameters
- `GetTemperature()` - Get reader temperature
- `GetWorkMode()` / `SetWorkMode()` - Work mode settings

**All 50+ functions are available in `chafon_cf591.py`!**

---

## Power and Range Control

### Power to Distance Mapping

| Power Setting | Approximate Range | Use Case |
|--------------|-------------------|----------|
| 0-5 | 0.5-2 meters | Very short range, high security |
| 6-10 | 2-3 meters | Desk/counter scanning |
| 11-15 | 3-5 meters | General purpose, room coverage |
| 16-20 | 5-7 meters | Shelf scanning, wide area |
| 21-25 | 7-9 meters | Large space coverage |
| 26-30 | 9-10 meters | Maximum range, parking lots |

### Common Use Cases

| Use Case | Range | Power Setting |
|----------|-------|---------------|
| **Access Control** | 1m | `set_rf_power(5)` |
| **Item Checkout** | 2-3m | `set_rf_power(10)` |
| **Inventory Scan** | 5-7m | `set_rf_power(20)` |
| **Asset Tracking** | 7-10m | `set_rf_power(30)` |
| **Warehouse** | 10m | `set_rf_power(30)` |

---

## Troubleshooting

### Problem: "Permission denied"

```bash
# Solution 1: Temporary fix
sudo chmod 666 /dev/ttyUSB0

# Solution 2: Permanent fix
sudo usermod -a -G dialout $USER
# Then logout and login again
```

### Problem: "Library not found"

```bash
# Install library
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig

# Verify
ldconfig -p | grep CFApi
```

### Problem: "libhid.so: cannot open shared object file"

```bash
# Install HID library
sudo apt-get install -y libhidapi-libusb0

# Create symlink
sudo ln -sf /usr/lib/aarch64-linux-gnu/libhidapi-libusb.so.0 /usr/lib/aarch64-linux-gnu/libhid.so

# Update library cache
sudo ldconfig
```

### Problem: "No tag detected"

1. **Increase range**: `reader.set_rf_power(30)`
2. **Increase timeout**: `reader.read_single_tag(timeout=30000)`
3. **Check tag type**: Must be UHF RFID tag (860-960 MHz)
4. **Check antenna**: Ensure antenna is properly connected
5. **Check tag position**: Move tag closer to reader

### Problem: "Failed to open device"

1. **Check connection**: `ls /dev/ttyUSB*`
2. **Check permissions**: `ls -la /dev/ttyUSB0`
3. **Check if device is in use**: `lsof /dev/ttyUSB0`
4. **Try different port**: `/dev/ttyACM0` or `/dev/ttyUSB1`

### Problem: Tag memory operations timeout

- **Keep tag in range**: Tag must remain close during memory operations
- **Some tags don't support memory reading**: Check tag specifications
- **Memory banks may be locked**: Some tags require passwords
- **Tag type limitations**: Some tag types have limited memory access

---

## Important Notes

### Known Issues and Fixes

1. **Handle Initialization**: Must use `c_int64(0)` not `c_int64(-1)` for handle initialization
2. **Error Code Handling**: C library returns signed integers, converted to unsigned for comparison
3. **Inventory Stop**: Timeout errors are normal when inventory already stopped
4. **Tag Memory Operations**: Require tag to be in range and may not work on all tag types

### Best Practices

1. **Use context managers**: `with CF591Reader(...) as reader:`
2. **Always stop inventory**: Use `try/finally` to ensure cleanup
3. **Handle timeouts gracefully**: Timeouts are normal when no tags are present
4. **Keep tags in range**: For memory operations, keep tag close to reader
5. **Test with examples**: Run `python3 examples.py` to verify setup

---

## File Structure

```
CHAFON_CF591_sample_linux/
├── README.md                    ← This file
├── chafon_cf591.py              ← Main Python library
├── examples.py                  ← 12 working examples
├── API/
│   └── Linux/
│       ├── ARM64/               ← For Raspberry Pi 5
│       │   ├── libCFApi.so
│       │   └── libCFApi.a
│       └── CFApi.h              ← C API header
└── User Guide/                  ← Official documentation
```

---

## Support

- **Setup issues**: See [Installation](#installation) and [Troubleshooting](#troubleshooting)
- **API questions**: See [API Reference](#api-reference)
- **Examples**: Run `python3 examples.py`
- **Hardware issues**: Check `User Guide/` directory

---

## Summary

**This package provides everything you need to integrate CHAFON CF591 RFID reader into your Raspberry Pi 5 Python application with:**

- ✅ Trigger-based reading (start/stop on demand)
- ✅ Automatic stop after first tag detection
- ✅ Configurable reading range (1-10 meters)
- ✅ Simple Python API
- ✅ Complete documentation
- ✅ Working examples

**Get started**: Follow [Quick Start](#quick-start) section above.

**Happy coding! 🎉**
