# Quick Start Guide - CHAFON CF591 on Raspberry Pi 5

## 🚀 Get Started in 5 Minutes

### Step 1: Connect the Device

```bash
# Connect CF591 to Raspberry Pi 5 via USB

# Check connection
lsusb  # Should see USB serial device

# Find serial port
ls /dev/ttyUSB*  # Usually /dev/ttyUSB0

# Set permissions
sudo chmod 666 /dev/ttyUSB0
```

### Step 2: Install Library

```bash
cd /home/bdm-office/.cursor/worktrees/CHAFON_CF591_sample_linux__SSH__office-new_/aiv

# For Raspberry Pi 5 (ARM64)
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig

# Verify
ldconfig -p | grep CFApi
```

### Step 3: Quick Test

```bash
# Test with simple read
python3 rfid_trigger_reader.py --mode single --range 5 --timeout 10
```

Expected output:
```
CHAFON CF591 Trigger-Based RFID Reader
========================================================

Mode: Single Tag Read
Port: /dev/ttyUSB0
Range: ~5 meters
Timeout: 10 seconds

Connected to CHAFON CF591
  Firmware: V1.3.0
  Hardware: V1.0
  Serial: 1234567890AB

Place tag near reader...
Waiting for tag (timeout: 10s)...
✓ Tag detected in 2.3s
  EPC: E20034120118000000000000
  RSSI: -42.5 dBm
  Antenna: 1

============================================================
TAG INFORMATION
============================================================
EPC:      E20034120118000000000000
RSSI:     -42.5 dBm
Antenna:  1
Channel:  15
Sequence: 1
============================================================
```

---

## 📝 Your Requirements Implementation

### Requirement 1: Start Reading on Trigger

```python
from rfid_trigger_reader import RFIDTriggerReader

reader = RFIDTriggerReader(port='/dev/ttyUSB0')
reader.connect()

# Trigger: Start reading when you need
reader.start_inventory()

# ... reading happens here ...
```

### Requirement 2: Stop as Soon as Tag is Read

```python
from rfid_trigger_reader import RFIDTriggerReader

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(5)  # 5 meters
    
    # This automatically stops after first tag
    tag = reader.read_once(timeout=10)
    
    if tag:
        print(f"Tag: {tag['epc']}")
        # Continue with your logic
```

### Requirement 3: Set Reading Range

```python
from rfid_trigger_reader import RFIDTriggerReader

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    # Set range in meters (1-10)
    reader.set_reading_range(3)  # Short range: ~3 meters
    # reader.set_reading_range(5)  # Medium range: ~5 meters
    # reader.set_reading_range(10)  # Long range: ~10 meters
    
    tag = reader.read_once()
```

Or set power directly:
```python
# Power: 0-30
reader.set_power(5)   # Very short range (~1-2m)
reader.set_power(15)  # Medium range (~5m)
reader.set_power(30)  # Maximum range (~10m)
```

---

## 🎯 Complete Example for Your Use Case

```python
#!/usr/bin/env python3
"""
Complete example matching your requirements:
- Trigger-based reading
- Stop on first tag
- Configurable range
"""

from rfid_trigger_reader import RFIDTriggerReader

def main():
    # Initialize reader
    reader = RFIDTriggerReader(port='/dev/ttyUSB0')
    
    try:
        # Connect once at application start
        reader.connect()
        
        # Set reading range (adjust as needed)
        reader.set_reading_range(5)  # 5 meters
        
        # Your application logic
        print("Application ready. Waiting for triggers...")
        
        while True:
            # Wait for trigger (e.g., button press, web request, etc.)
            input("\nPress Enter to trigger RFID read (or 'q' to quit): ")
            
            if input == 'q':
                break
            
            # Trigger: Start reading
            print("Reading RFID tag...")
            tag = reader.read_once(timeout=10, verbose=True)
            
            # Automatically stopped after first tag read
            
            if tag:
                # Tag detected - process it
                tag_id = tag['epc']
                signal_strength = tag['rssi']
                
                print(f"\n✓ Success!")
                print(f"  Tag ID: {tag_id}")
                print(f"  Signal: {signal_strength:.1f} dBm")
                
                # Your business logic here
                process_tag(tag_id)
                
            else:
                # No tag detected
                print("\n✗ No tag detected within timeout")
                # Handle no-tag scenario
    
    finally:
        # Cleanup
        reader.disconnect()
        print("Disconnected")

def process_tag(tag_id):
    """Your tag processing logic"""
    print(f"  → Processing: {tag_id}")
    # Add your logic here:
    # - Database lookup
    # - API call
    # - Update inventory
    # - Grant access
    # etc.

if __name__ == '__main__':
    main()
```

---

## 💡 Common Use Cases

### Use Case 1: One-Liner Quick Read

```python
from rfid_trigger_reader import read_tag

# Simplest possible way
tag_id = read_tag(port='/dev/ttyUSB0', distance=5, timeout=10)

if tag_id:
    print(f"Tag: {tag_id}")
```

### Use Case 2: Access Control

```python
from rfid_trigger_reader import RFIDTriggerReader

authorized_tags = ['E20034120118000000000000', 'E20034120118000000000001']

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(1)  # Short range for security
    
    print("Scan your badge...")
    tag = reader.read_once(timeout=30)
    
    if tag and tag['epc'] in authorized_tags:
        print("✓ Access granted")
        unlock_door()
    else:
        print("✗ Access denied")
```

### Use Case 3: Inventory Check

```python
from rfid_trigger_reader import RFIDTriggerReader

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(7)  # Longer range for shelves
    
    print("Scanning shelf...")
    tags = reader.read_multiple(duration=10)
    
    print(f"Found {len(tags)} items:")
    for tag in tags:
        print(f"  - {tag['epc']}")
```

### Use Case 4: Distance-Based Action

```python
from rfid_trigger_reader import RFIDTriggerReader

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(10)  # Max range
    
    tag = reader.read_once(timeout=10)
    
    if tag:
        rssi = tag['rssi']
        
        if rssi > -40:
            print("Tag is very close - unlock")
        elif rssi > -55:
            print("Tag is nearby - prepare")
        else:
            print("Tag is far - just detect")
```

---

## 🔧 Configuration Options

### Range Settings

| Distance | Power | Use Case |
|----------|-------|----------|
| 1 meter  | 5     | Security access, close proximity |
| 2 meters | 8     | Desk checkout, handheld scanning |
| 3 meters | 12    | Counter service, item verification |
| 5 meters | 20    | Room coverage, general purpose |
| 7 meters | 26    | Shelf scanning, wide area |
| 10 meters| 30    | Long-range detection, parking |

### Timeout Settings

| Timeout | Use Case |
|---------|----------|
| 2-5s    | Fast interaction, known tag nearby |
| 5-10s   | Normal operation, balanced |
| 10-30s  | Patient waiting, uncertain presence |

---

## 📚 API Reference

### RFIDTriggerReader Class

```python
# Initialize
reader = RFIDTriggerReader(port='/dev/ttyUSB0', baudrate=115200)

# Connection
reader.connect()               # Connect to device
reader.disconnect()            # Disconnect

# Configuration
reader.set_reading_range(meters)  # Set range (1-10 meters)
reader.set_power(power)           # Set power directly (0-30)

# Reading
tag = reader.read_once(timeout=10, verbose=True)
tags = reader.read_multiple(duration=5, max_tags=None, unique_only=True)
tag = reader.read_strongest_tag(duration=3)
tag = reader.read_until_condition(condition_func, timeout=30)

# Callbacks
reader.set_tag_callback(callback_function)

# Info
info = reader.get_device_info()
params = reader.get_device_parameters()
```

### Tag Dictionary Format

```python
tag = {
    'epc': 'E20034120118000000000000',  # Tag ID (hex string)
    'epc_bytes': b'\xe2\x00\x34...',    # Tag ID (bytes)
    'rssi': -42.5,                       # Signal strength (dBm)
    'antenna': 1,                        # Antenna number (1-4)
    'channel': 15,                       # Frequency channel
    'sequence': 1                        # Tag sequence number
}
```

---

## 🐛 Troubleshooting

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

### Problem: "No module named 'chafon_cf591'"

```bash
# Make sure you're in the correct directory
cd /home/bdm-office/.cursor/worktrees/CHAFON_CF591_sample_linux__SSH__office-new_/aiv

# Or add to Python path
export PYTHONPATH=$PYTHONPATH:/path/to/geu
```

### Problem: "No tag detected"

1. **Check power**: Increase reading range
   ```python
   reader.set_reading_range(10)  # Maximum range
   ```

2. **Check tag**: Verify it's a UHF RFID tag (860-960 MHz)

3. **Check antenna**: Ensure antenna is properly connected

4. **Check timeout**: Increase timeout
   ```python
   tag = reader.read_once(timeout=30)  # 30 seconds
   ```

---

## 📦 Files in This Package

```
aiv/
├── COMPREHENSIVE_GUIDE.md          # Complete documentation
├── QUICK_START_RASPBERRY_PI_5.md   # This file
├── rfid_trigger_reader.py          # Main library
├── example_integration.py          # Integration examples
├── API/                            # C libraries
│   └── Linux/
│       ├── ARM64/                  # For Raspberry Pi 5
│       │   ├── libCFApi.so
│       │   └── libCFApi.a
│       └── CFApi.h                 # C header file
├── Sample/                         # Official samples
└── User Guide/                     # Official documentation
```

---

## 🔗 Next Steps

1. **Test the connection**:
   ```bash
   python3 rfid_trigger_reader.py --mode single
   ```

2. **Integrate into your code**:
   - Use `RFIDTriggerReader` class
   - See `example_integration.py` for patterns
   - Adapt to your specific workflow

3. **Optimize settings**:
   - Adjust range based on your environment
   - Fine-tune timeouts
   - Configure callbacks for real-time processing

4. **Read full documentation**:
   - `COMPREHENSIVE_GUIDE.md` - All features
   - `API/Linux/CFApi.h` - Complete C API reference

---

## 📞 Support

For questions about:
- **Hardware**: Check User Guide documentation
- **Library**: Refer to COMPREHENSIVE_GUIDE.md
- **Integration**: See example_integration.py

---

**Ready to go! 🎉**

```bash
python3 rfid_trigger_reader.py --mode single --range 5
```


