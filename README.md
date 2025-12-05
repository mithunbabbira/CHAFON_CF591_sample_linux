# CHAFON CF591 RFID Reader - Raspberry Pi 5 Integration

Complete Python implementation for trigger-based RFID reading with the CHAFON CF591 on Raspberry Pi 5.

## 🎯 What This Provides

✅ **Trigger-based reading** - Start and stop reading on demand  
✅ **Auto-stop on first tag** - Automatically stops after detecting one tag  
✅ **Configurable range** - Adjust reading distance from 1-10 meters  
✅ **Simple Python API** - Easy integration into existing applications  
✅ **Complete documentation** - Everything you need to know  
✅ **Working examples** - 9 integration patterns ready to use  

---

## 📚 Documentation Files

### Start Here

1. **[QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md)** ⭐ **START HERE**
   - 5-minute setup guide
   - Quick examples for your specific requirements
   - Troubleshooting
   - **Read this first!**

2. **[UNDERSTANDING_SUMMARY.md](UNDERSTANDING_SUMMARY.md)** 📖 **OVERVIEW**
   - Complete explanation of what CHAFON CF591 is
   - Summary of all capabilities
   - Implementation details for your requirements
   - Architecture overview

3. **[COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md)** 📘 **COMPLETE REFERENCE**
   - All programmatic operations documented
   - Power/range mapping tables
   - Trigger configuration details
   - Error codes and troubleshooting
   - Advanced features

### Code Files

4. **[rfid_trigger_reader.py](rfid_trigger_reader.py)** 🐍 **MAIN LIBRARY**
   - `RFIDTriggerReader` class
   - Methods: `read_once()`, `read_multiple()`, `set_reading_range()`
   - Use this in your Python application

5. **[example_integration.py](example_integration.py)** 💡 **INTEGRATION EXAMPLES**
   - 9 complete working examples:
     1. Simple single tag read
     2. Application flow integration
     3. Context manager pattern
     4. Callback-based processing
     5. Access control system
     6. Inventory management
     7. Distance-based actions
     8. Batch processing with queue
     9. Web API integration (Flask)

---

## 🚀 Quick Start (5 Minutes)

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
```

### 3. Test

```bash
python3 rfid_trigger_reader.py --mode single --range 5
```

### 4. Use in Your Code

```python
from rfid_trigger_reader import RFIDTriggerReader

# Simplest usage
with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(5)  # 5 meters
    
    # Trigger: Read one tag
    tag = reader.read_once(timeout=10)
    
    if tag:
        print(f"Tag: {tag['epc']}")
        # Your logic here
```

**That's it!** See [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md) for more details.

---

## 📋 Your Requirements - Solutions

### ✅ Requirement 1: Trigger-Based Reading

**Solution**: Use `read_once()` method

```python
with RFIDTriggerReader() as reader:
    # Wait for your trigger (button, web request, etc.)
    trigger = wait_for_trigger()
    
    if trigger:
        # Start reading
        tag = reader.read_once(timeout=10)
```

### ✅ Requirement 2: Stop on First Tag

**Solution**: `read_once()` automatically stops after first tag

```python
# Automatically stops after detecting first tag
tag = reader.read_once(timeout=10)

# Reading has stopped - you can now process the tag
if tag:
    process_tag(tag['epc'])
```

### ✅ Requirement 3: Set Reading Range

**Solution**: Use `set_reading_range()` or `set_power()`

```python
# Method 1: Set distance in meters (simple)
reader.set_reading_range(3)   # 3 meters
reader.set_reading_range(5)   # 5 meters
reader.set_reading_range(10)  # 10 meters

# Method 2: Set power directly (0-30)
reader.set_power(5)    # Low power ~2m
reader.set_power(15)   # Medium power ~5m
reader.set_power(30)   # Max power ~10m
```

---

## 📖 What Can CHAFON CF591 Do?

### Core Features
- **Read RFID tags** from 1-10 meters away
- **Write data** to tags
- **Lock/Kill tags** permanently
- **Filter tags** by EPC pattern
- **Measure signal strength** (RSSI)
- **Trigger modes**: Software, hardware GPIO, or timer-based
- **Multi-antenna support** (up to 8 antennas)
- **Network connectivity** (TCP/IP for compatible models)

### All Operations Documented
See [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) for complete list of 50+ functions including:
- Device management
- Tag reading/writing
- Power control
- Frequency configuration
- Antenna control
- GPIO/trigger configuration
- Filtering and selection
- Network configuration
- And more...

---

## 💻 Code Examples

### Example 1: One-Liner Quick Read

```python
from rfid_trigger_reader import read_tag

tag_id = read_tag(port='/dev/ttyUSB0', distance=5, timeout=10)
print(f"Tag: {tag_id}")
```

### Example 2: Context Manager (Recommended)

```python
from rfid_trigger_reader import RFIDTriggerReader

with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(5)
    
    tag = reader.read_once(timeout=10)
    if tag:
        print(f"EPC: {tag['epc']}")
        print(f"RSSI: {tag['rssi']:.1f} dBm")
        print(f"Antenna: {tag['antenna']}")
```

### Example 3: Application Integration

```python
from rfid_trigger_reader import RFIDTriggerReader

reader = RFIDTriggerReader(port='/dev/ttyUSB0')
reader.connect()
reader.set_reading_range(5)

# Your application loop
while True:
    # Wait for your trigger (button press, web request, etc.)
    user_input = input("Press Enter to scan RFID (or 'q' to quit): ")
    
    if user_input == 'q':
        break
    
    # Trigger: Read tag
    tag = reader.read_once(timeout=10)
    
    if tag:
        # Process tag
        process_tag(tag['epc'])
    else:
        print("No tag detected")

reader.disconnect()
```

### Example 4: Multiple Tags

```python
with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
    reader.set_reading_range(7)
    
    # Read all tags in range for 10 seconds
    tags = reader.read_multiple(duration=10)
    
    print(f"Found {len(tags)} tags:")
    for tag in tags:
        print(f"  - {tag['epc']} ({tag['rssi']:.1f} dBm)")
```

**More examples**: See [example_integration.py](example_integration.py)

---

## 🎯 Common Use Cases

| Use Case | Range | Implementation |
|----------|-------|----------------|
| **Access Control** | 1m | `set_reading_range(1)` + `read_once()` |
| **Item Checkout** | 2-3m | `set_reading_range(3)` + `read_once()` |
| **Inventory Scan** | 5-7m | `set_reading_range(7)` + `read_multiple()` |
| **Asset Tracking** | 7-10m | `set_reading_range(10)` + `read_strongest_tag()` |
| **Warehouse** | 10m | `set_power(30)` + filters |

---

## 📊 Power vs Range Mapping

| Power Setting | Approximate Range | Use Case |
|--------------|-------------------|----------|
| 0-5 | 0.5-2 meters | Close proximity, high security |
| 6-10 | 2-3 meters | Desk/counter scanning |
| 11-15 | 3-5 meters | General purpose, room coverage |
| 16-20 | 5-7 meters | Shelf scanning, wide area |
| 21-25 | 7-9 meters | Large space coverage |
| 26-30 | 9-10 meters | Maximum range, parking lots |

---

## 🔧 API Reference

### RFIDTriggerReader Class

```python
# Initialize
reader = RFIDTriggerReader(port='/dev/ttyUSB0', baudrate=115200)

# Connection
reader.connect()
reader.disconnect()

# Configuration
reader.set_reading_range(meters)     # 1-10 meters
reader.set_power(power)              # 0-30 direct power

# Reading
tag = reader.read_once(timeout=10, verbose=True)
tags = reader.read_multiple(duration=5, max_tags=None)
tag = reader.read_strongest_tag(duration=3)

# Callbacks
reader.set_tag_callback(callback_function)

# Device Info
info = reader.get_device_info()
params = reader.get_device_parameters()
```

### Tag Dictionary

```python
tag = {
    'epc': 'E20034120118000000000000',  # Tag ID (hex string)
    'epc_bytes': b'\xe2\x00\x34...',    # Tag ID (bytes)
    'rssi': -42.5,                       # Signal strength (dBm)
    'antenna': 1,                        # Antenna number
    'channel': 15,                       # Frequency channel
    'sequence': 1                        # Sequence number
}
```

---

## 🐛 Troubleshooting

### Problem: "Permission denied"

```bash
sudo chmod 666 /dev/ttyUSB0
# OR
sudo usermod -a -G dialout $USER  # Then logout/login
```

### Problem: "Library not found"

```bash
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig
```

### Problem: "No tag detected"

1. Increase range: `reader.set_reading_range(10)`
2. Increase timeout: `reader.read_once(timeout=30)`
3. Check tag type (must be UHF 860-960 MHz)
4. Check antenna connection

**More troubleshooting**: See [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md#troubleshooting)

---

## 📂 Directory Structure

```
aiv/
├── README.md                         ← You are here
├── QUICK_START_RASPBERRY_PI_5.md    ← Start here!
├── UNDERSTANDING_SUMMARY.md          ← Complete overview
├── COMPREHENSIVE_GUIDE.md            ← Full documentation
├── rfid_trigger_reader.py           ← Main Python library
├── example_integration.py           ← 9 integration examples
├── API/
│   └── Linux/
│       ├── ARM64/                   ← For Raspberry Pi 5
│       │   ├── libCFApi.so
│       │   └── libCFApi.a
│       └── CFApi.h                  ← C API header
└── User Guide/                      ← Official manuals
```

---

## 🎓 Learning Path

### For Beginners
1. Read [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md)
2. Run: `python3 rfid_trigger_reader.py --mode single`
3. Try: Example 1 in [example_integration.py](example_integration.py)
4. Adapt to your needs

### For Developers
1. Read [UNDERSTANDING_SUMMARY.md](UNDERSTANDING_SUMMARY.md)
2. Study [rfid_trigger_reader.py](rfid_trigger_reader.py)
3. Review [example_integration.py](example_integration.py) patterns
4. Integrate into your application

### For Advanced Users
1. Read [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md)
2. Study `API/Linux/CFApi.h` for low-level control
3. Explore advanced features (GPIO triggers, filtering, etc.)
4. Optimize for your specific use case

---

## 🔗 Quick Links

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md) | Fast setup | Getting started |
| [UNDERSTANDING_SUMMARY.md](UNDERSTANDING_SUMMARY.md) | Complete overview | Understanding capabilities |
| [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md) | Full reference | Deep dive, all features |
| [rfid_trigger_reader.py](rfid_trigger_reader.py) | Python library | Using in your code |
| [example_integration.py](example_integration.py) | Code examples | Learning patterns |

---

## ✅ What You Get

- ✅ **Hardware support**: Raspberry Pi 5 (ARM64) optimized
- ✅ **Simple API**: Python classes and functions
- ✅ **Trigger control**: Start/stop on demand
- ✅ **Range control**: 1-10 meters adjustable
- ✅ **Auto-stop**: Stops after first tag
- ✅ **Multiple modes**: Single, multiple, continuous
- ✅ **Callbacks**: Real-time tag processing
- ✅ **Examples**: 9 integration patterns
- ✅ **Documentation**: 4 comprehensive guides
- ✅ **Error handling**: Built-in exception handling
- ✅ **Context managers**: Automatic cleanup

---

## 🚀 Next Steps

1. **Install**: Follow [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md)
2. **Test**: Run `python3 rfid_trigger_reader.py --mode single`
3. **Integrate**: Use `RFIDTriggerReader` in your code
4. **Customize**: Adjust range, timeout, callbacks as needed

---

## 📞 Support

- **Setup issues**: See [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md#troubleshooting)
- **Feature questions**: See [COMPREHENSIVE_GUIDE.md](COMPREHENSIVE_GUIDE.md)
- **Integration help**: See [example_integration.py](example_integration.py)
- **Hardware issues**: Check `User Guide/` directory

---

## 📝 Summary

**This package provides everything you need to integrate CHAFON CF591 RFID reader into your Raspberry Pi 5 Python application with:**

- ✅ Trigger-based reading (start/stop on demand)
- ✅ Automatic stop after first tag detection
- ✅ Configurable reading range (1-10 meters)
- ✅ Simple Python API
- ✅ Complete documentation
- ✅ Working examples

**Get started**: [QUICK_START_RASPBERRY_PI_5.md](QUICK_START_RASPBERRY_PI_5.md)

---

**Happy coding! 🎉**


