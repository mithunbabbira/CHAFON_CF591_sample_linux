# CHAFON CF591 RFID Reader - Complete Programming Guide for Raspberry Pi 5

## Table of Contents
1. [Overview](#overview)
2. [Hardware Connection](#hardware-connection)
3. [All Programmatic Operations](#all-programmatic-operations)
4. [Trigger-Based Reading](#trigger-based-reading)
5. [Range Control](#range-control)
6. [Implementation Examples](#implementation-examples)

---

## Overview

### What is the CHAFON CF591?
The CHAFON CF591 is a **UHF RFID reader/writer** that can read passive RFID tags from a distance (typically 1-10 meters depending on power settings). It connects to your Raspberry Pi 5 via USB and appears as a serial port device.

### Key Capabilities
- **Read Range**: 1-10 meters (adjustable via power settings)
- **Reading Speed**: Can read multiple tags per second
- **Connection**: USB (appears as `/dev/ttyUSB0` or `/dev/ttyACM0`)
- **Frequency**: UHF 860-960 MHz (region dependent)
- **Supported Protocols**: ISO 18000-6C (EPC Gen2), ISO 18000-6B, GB/T 29768

---

## Hardware Connection

### 1. Connect the Device
```bash
# Check if device is connected
lsusb

# Check serial port
ls /dev/ttyUSB* /dev/ttyACM*

# Set permissions
sudo chmod 666 /dev/ttyUSB0

# Or add user to dialout group (permanent)
sudo usermod -a -G dialout $USER
# Then logout and login
```

### 2. Install the Library
For Raspberry Pi 5 (64-bit OS):
```bash
# Copy library to system
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig

# Verify installation
ldconfig -p | grep CFApi
```

---

## All Programmatic Operations

### 1. Device Management

#### Open Device (Serial)
```c
int OpenDevice(int64_t* hComm, char* pcCom, int iBaudRate);
```
- Opens serial port connection
- **Parameters**: Serial port path (`/dev/ttyUSB0`), baud rate (115200)
- **Returns**: `STAT_OK` on success

#### Open Device (Network)
```c
int OpenNetConnection(int64_t* hComm, char* strIP, unsigned short wPort, long timeoutMs);
```
- Opens TCP/IP connection for network-enabled readers
- **Parameters**: IP address, port (default 4001), timeout

#### Close Device
```c
int CloseDevice(int64_t hComm);
```
- Closes the device connection

### 2. Device Information

#### Get Device Info
```c
int GetInfo(int64_t hComm, DeviceInfo* devInfo);
```
- Returns firmware version, hardware version, serial number

#### Get Device Parameters
```c
int GetDevicePara(int64_t hComm, DevicePara* devInfo);
```
Returns comprehensive device configuration:
- Work mode (Answer mode = 0, Active mode = 1)
- RF power level (0-30)
- Antenna configuration
- Frequency region
- Trigger time settings
- Filter time
- Session settings

#### Set Device Parameters
```c
int SetDevicePara(int64_t hComm, DevicePara devInfo);
```
- Configures device parameters

### 3. Tag Reading (Inventory)

#### Start Inventory (Continuous Reading)
```c
int InventoryContinue(int64_t hComm, unsigned char btInvCount, unsigned long dwInvParam);
```
- **btInvCount = 0**: Continuous reading mode
- **btInvCount = N**: Stop after reading N tags
- **dwInvParam = 0**: Default parameters

#### Get Tag Information
```c
int GetTagUii(int64_t hComm, TagInfo* tag_info, unsigned short timeout);
```
Returns `TagInfo` structure with:
- **EPC Code**: Unique tag ID (code array)
- **RSSI**: Signal strength (in 0.1 dBm units)
- **Antenna**: Which antenna detected the tag
- **Channel**: Frequency channel used
- **Length**: EPC code length in bytes

**Return Codes**:
- `STAT_OK`: Tag successfully read
- `STAT_CMD_INVENTORY_STOP`: No more tags
- `STAT_CMD_COMM_TIMEOUT`: Timeout (no tag detected)

#### Stop Inventory
```c
int InventoryStop(int64_t hComm, unsigned short timeout);
```
- Stops the tag reading process

### 4. Tag Operations (Read/Write)

#### Read Tag Memory
```c
int ReadTag(int64_t hComm, unsigned char option, unsigned char* accPwd, 
            unsigned char memBank, unsigned short wordPtr, unsigned char wordCount);
int GetReadTagResp(int64_t hComm, TagResp* resp, unsigned char* wordCount, 
                   unsigned char* readData, unsigned short timeout);
```
- Read specific memory banks (EPC, TID, USER, Reserved)
- Requires access password for locked tags

#### Write Tag Memory
```c
int WriteTag(int64_t hComm, unsigned char option, unsigned char* accPwd, 
             unsigned char memBank, unsigned short wordPtr, 
             unsigned char wordCount, unsigned char* writeData);
```
- Write data to tag memory
- Can write to EPC, USER, or Reserved banks

#### Lock Tag
```c
int LockTag(int64_t hComm, unsigned char* accPwd, unsigned char erea, unsigned char action);
```
- Lock/unlock tag memory areas
- Prevent unauthorized modifications

#### Kill Tag
```c
int KillTag(int64_t hComm, unsigned char* accPwd);
```
- Permanently disable a tag (requires kill password)

### 5. Power and Range Control

#### Get RF Power
```c
int GetRFPower(int64_t hComm, unsigned char* power, unsigned char* reserved);
```
- Returns current RF power level (0-30)

#### Set RF Power
```c
int SetRFPower(int64_t hComm, unsigned char power, unsigned char reserved);
```
- **Power range**: 0-30 (higher = longer range)
- **0**: Minimum power (~1 meter)
- **15**: Medium power (~3-5 meters)
- **30**: Maximum power (~8-10 meters)
- **Controls reading range directly**

#### Get/Set Antenna Power
```c
int GetAntPower(int64_t hComm, AntPower* type);
int SetAntPower(int64_t hComm, AntPower type);
```
- Set individual power levels for each antenna (1-8)
- Allows fine-grained control per antenna

### 6. Frequency Configuration

#### Get Frequency
```c
int GetFreq(int64_t hComm, FreqInfo* freqInfo);
```
Returns:
- Region (US, EU, China, etc.)
- Start frequency
- Stop frequency
- Step frequency
- Channel count

#### Set Frequency
```c
int SetFreq(int64_t hComm, const FreqInfo* freqInfo);
```
- Configure frequency hopping
- Must match regional regulations

### 7. Antenna Configuration

#### Get Antenna
```c
int GetAntenna(int64_t hComm, unsigned char* antenna);
```
- Returns active antenna configuration

#### Set Antenna
```c
int SetAntenna(int64_t hComm, unsigned char* antenna);
```
- Select which antennas to use (bitmask)
- Example: 0x01 = Antenna 1, 0x03 = Antennas 1 & 2, 0x0F = All 4

### 8. Tag Filtering (Select/Sort)

#### Set Select Mask
```c
int SetSelectMask(int64_t hComm, unsigned short maskPtr, unsigned char maskBits, unsigned char* mask);
```
- Filter tags by EPC pattern
- Read only tags matching specific criteria

#### Get/Set Permission Parameters
```c
int GetPermissonPara(int64_t hComm, PermissonPara* PermissonPara);
int SetPermissonPara(int64_t hComm, PermissonPara PermissonPara);
```
- Set access codes for reading specific tags
- Configure mask filtering

### 9. GPIO and Trigger Configuration

#### Get GPIO Parameters
```c
int GetGpioPara(int64_t hComm, GpioPara* GpioPara);
```
Returns GPIO configuration including:
- **TriggleMode**: Trigger mode setting
- **KCEn**: Key control enable
- **RelayTime**: Relay activation time
- **BufferEn**: Buffer enable for storing tags

#### Set GPIO Parameters
```c
int SetGpioPara(int64_t hComm, GpioPara GpioPara);
```
Configure GPIO for:
- External trigger input
- Output signals (relay, LED, buzzer)
- Protocol forwarding

**Trigger Modes**:
- **Mode 0**: No trigger (continuous reading)
- **Mode 1**: External trigger (GPIO input)
- **Mode 2**: Software trigger
- **Mode 3**: Auto-trigger with timer

### 10. Advanced Operations

#### Q Value Configuration
```c
int GetCoilPRM(int64_t hComm, unsigned char* pqVal, unsigned char* reserved);
int SetCoilPRM(int64_t hComm, unsigned char qVal, unsigned char reserved);
```
- Adjust Q parameter for tag reading efficiency
- Higher Q = faster reading with more tags
- Lower Q = more reliable with fewer tags

#### Query Parameters
```c
int QueryCfgGet(int64_t hComm, unsigned char proto, QueryParam* param);
int QueryCfgSet(int64_t hComm, unsigned char proto, QueryParam param);
```
- Configure tag query parameters
- Session settings (S0, S1, S2, S3)
- Target settings (A or B)

#### Network Configuration
```c
int GetNetInfo(int64_t hComm, NetInfo* type);
int SetNetInfo(int64_t hComm, NetInfo type);
```
- Configure IP, port, gateway for network readers
- Set MAC address

#### Reboot Device
```c
int RebootDevice(int64_t hComm);
```
- Factory reset or restart the reader

---

## Trigger-Based Reading

### Software Trigger Implementation

**Method 1: Start/Stop on Demand**
```python
# Start reading when triggered
reader.start_inventory()

# Read until tag found
tag = reader.get_tag(timeout=2000)

# Stop immediately
reader.stop_inventory()
```

**Method 2: Active Mode with Trigger Time**
```python
# Set device to active mode with trigger time
params = reader.get_device_parameters()
params['work_mode'] = 1  # Active mode
params['trigger_time'] = 5  # Read for 5 seconds then stop
reader.set_device_parameters(**params)

# Now start inventory - it will auto-stop after trigger_time
reader.start_inventory()
tag = reader.get_tag(timeout=6000)
```

**Method 3: GPIO Hardware Trigger**
```python
# Configure GPIO for external trigger
gpio_para = GpioPara()
gpio_para.TriggleMode = 1  # External trigger mode
gpio_para.KCEn = 1  # Enable key control
reader.set_gpio_parameters(gpio_para)

# Reader will only read when GPIO input is active
```

### Work Modes

**Answer Mode (Mode 0)**:
- Reader waits for commands
- Manual control via software
- Best for precise control

**Active Mode (Mode 1)**:
- Reader operates autonomously
- Can trigger automatically based on timer
- Best for standalone operation

---

## Range Control

### Methods to Control Reading Range

#### 1. RF Power Adjustment (Primary Method)
```python
# Short range (~1-2 meters)
reader.set_rf_power(5)

# Medium range (~3-5 meters)
reader.set_rf_power(15)

# Long range (~8-10 meters)
reader.set_rf_power(30)
```

**Power to Distance Mapping** (approximate):
- Power 0-5: 0.5-2 meters
- Power 6-10: 2-3 meters
- Power 11-15: 3-5 meters
- Power 16-20: 5-7 meters
- Power 21-25: 7-9 meters
- Power 26-30: 9-10 meters

#### 2. RSSI Filtering (Secondary Method)
```python
# Only accept tags with strong signal (closer tags)
while True:
    tag = reader.get_tag()
    if tag and tag['rssi'] > -40:  # Strong signal = close tag
        print(f"Close tag detected: {tag['epc']}")
        break
```

**RSSI Reference**:
- -20 to -30 dBm: Very close (< 1 meter)
- -30 to -45 dBm: Close (1-3 meters)
- -45 to -60 dBm: Medium (3-6 meters)
- -60 to -80 dBm: Far (6-10 meters)

#### 3. Antenna Power Control
```python
# Set different power levels for different antennas
antenna_powers = [10, 0, 0, 0, 0, 0, 0, 0]  # Only antenna 1 at power 10
reader.set_antenna_power(enable=True, antenna_powers=antenna_powers)
```

---

## Implementation Examples

### Example 1: Read Single Tag on Trigger
```python
from chafon_cf591 import CHAFONCF591

def read_single_tag_on_trigger(port='/dev/ttyUSB0'):
    """Read one tag when triggered, then stop"""
    reader = CHAFONCF591()
    
    try:
        # Open connection
        reader.open_device(port, 115200)
        print("Reader connected")
        
        # Set medium range
        reader.set_rf_power(15)
        
        # Wait for trigger (e.g., button press, external signal)
        input("Press Enter to start reading...")
        
        # Start inventory
        reader.start_inventory()
        print("Reading tags...")
        
        # Read until first tag found
        tag = None
        timeout_count = 0
        max_timeouts = 10  # 10 seconds total timeout
        
        while tag is None and timeout_count < max_timeouts:
            tag = reader.get_tag(timeout_ms=1000)
            if tag is None:
                timeout_count += 1
        
        # Stop immediately after reading
        reader.stop_inventory()
        
        if tag:
            print(f"Tag detected!")
            print(f"  EPC: {tag['epc']}")
            print(f"  RSSI: {tag['rssi']:.1f} dBm")
            print(f"  Antenna: {tag['antenna']}")
            return tag
        else:
            print("No tag detected within timeout")
            return None
            
    finally:
        reader.close()

# Usage
tag = read_single_tag_on_trigger()
```

### Example 2: Set Specific Reading Range
```python
from chafon_cf591 import CHAFONCF591

def read_tags_in_range(port='/dev/ttyUSB0', max_distance_meters=3):
    """Read only tags within specific distance"""
    reader = CHAFONCF591()
    
    try:
        reader.open_device(port, 115200)
        
        # Map distance to power setting
        power_map = {
            1: 5,
            2: 8,
            3: 12,
            4: 16,
            5: 20,
            6: 23,
            7: 26,
            8: 28,
            9: 30,
            10: 30
        }
        
        power = power_map.get(max_distance_meters, 15)
        reader.set_rf_power(power)
        print(f"Reading range set to ~{max_distance_meters} meters (power: {power})")
        
        # Start reading
        reader.start_inventory()
        
        # Read for 10 seconds
        import time
        start_time = time.time()
        tags_found = set()
        
        while time.time() - start_time < 10:
            tag = reader.get_tag(timeout_ms=500)
            if tag:
                epc = tag['epc']
                if epc not in tags_found:
                    tags_found.add(epc)
                    print(f"Tag: {epc}, RSSI: {tag['rssi']:.1f} dBm")
        
        reader.stop_inventory()
        print(f"\nTotal unique tags found: {len(tags_found)}")
        
    finally:
        reader.close()

# Usage
read_tags_in_range(max_distance_meters=3)
```

### Example 3: Trigger-Based with Auto-Stop
```python
from chafon_cf591 import CHAFONCF591
import time

def triggered_read_with_autostop(port='/dev/ttyUSB0', read_duration=5):
    """
    Set reader to active mode with trigger time.
    It will auto-stop after specified duration.
    """
    reader = CHAFONCF591()
    
    try:
        reader.open_device(port, 115200)
        
        # Configure device for active mode with trigger time
        reader.set_device_parameters(
            work_mode=1,  # Active mode
            rf_power=15,  # Medium range
            trigger_time=read_duration  # Auto-stop after N seconds
        )
        
        print(f"Reader configured for {read_duration}s auto-read")
        
        # Wait for trigger
        input("Press Enter to trigger reading...")
        
        # Start inventory - will auto-stop after trigger_time
        reader.start_inventory()
        print(f"Reading for {read_duration} seconds...")
        
        tags_found = []
        start = time.time()
        
        # Read all tags during the trigger period
        while time.time() - start < read_duration + 1:
            tag = reader.get_tag(timeout_ms=500)
            if tag:
                tags_found.append(tag)
                print(f"  Tag: {tag['epc']}")
        
        print(f"\nFound {len(tags_found)} tag reads")
        
        # Reader has auto-stopped after trigger_time
        return tags_found
        
    finally:
        reader.close()

# Usage
tags = triggered_read_with_autostop(read_duration=5)
```

### Example 4: Read Until First Tag, Then Stop
```python
from chafon_cf591 import CHAFONCF591

def read_first_tag_and_stop(port='/dev/ttyUSB0', power=15, timeout=30):
    """
    Most efficient implementation:
    Start reading, stop as soon as first tag detected
    """
    reader = CHAFONCF591()
    
    try:
        # Connect and configure
        reader.open_device(port, 115200)
        reader.set_rf_power(power)
        
        print("Waiting for tag...")
        
        # Start inventory
        reader.start_inventory()
        
        # Read until first tag
        tag = None
        elapsed = 0
        
        while tag is None and elapsed < timeout:
            tag = reader.get_tag(timeout_ms=1000)
            elapsed += 1
        
        # Stop immediately
        reader.stop_inventory()
        
        if tag:
            print(f"✓ Tag detected: {tag['epc']}")
            print(f"  RSSI: {tag['rssi']:.1f} dBm")
            print(f"  Antenna: {tag['antenna']}")
            print(f"  Time: {elapsed}s")
            return tag
        else:
            print("✗ No tag detected")
            return None
            
    finally:
        reader.close()

# Usage
tag = read_first_tag_and_stop(power=20, timeout=10)
```

### Example 5: Integration with Your Python Logic
```python
class RFIDReader:
    """
    Wrapper class for easy integration with existing Python code
    """
    def __init__(self, port='/dev/ttyUSB0', power=15):
        from chafon_cf591 import CHAFONCF591
        self.reader = CHAFONCF591()
        self.port = port
        self.power = power
        self.connected = False
    
    def connect(self):
        """Connect to reader"""
        self.reader.open_device(self.port, 115200)
        self.reader.set_rf_power(self.power)
        self.connected = True
    
    def disconnect(self):
        """Disconnect from reader"""
        if self.connected:
            self.reader.close()
            self.connected = False
    
    def set_range(self, distance_meters):
        """Set reading range in meters (1-10)"""
        power_map = {1:5, 2:8, 3:12, 4:16, 5:20, 6:23, 7:26, 8:28, 9:30, 10:30}
        power = power_map.get(distance_meters, 15)
        self.reader.set_rf_power(power)
    
    def read_tag(self, timeout=10):
        """
        Trigger reading and return first tag detected
        Returns tag EPC as string or None
        """
        if not self.connected:
            self.connect()
        
        try:
            # Start reading
            self.reader.start_inventory()
            
            # Wait for tag
            tag = None
            for _ in range(timeout):
                tag = self.reader.get_tag(timeout_ms=1000)
                if tag:
                    break
            
            # Stop reading
            self.reader.stop_inventory()
            
            return tag['epc'] if tag else None
            
        except Exception as e:
            print(f"Error reading tag: {e}")
            return None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.disconnect()

# Usage in your existing Python code
with RFIDReader(port='/dev/ttyUSB0', power=15) as rfid:
    # Set reading range to 3 meters
    rfid.set_range(3)
    
    # Trigger 1: Read tag
    print("Scan your RFID tag...")
    tag_id = rfid.read_tag(timeout=10)
    
    if tag_id:
        print(f"Tag ID: {tag_id}")
        # Your logic here
        process_tag(tag_id)
    else:
        print("No tag detected")
    
    # Trigger 2: Read another tag
    print("Scan next tag...")
    tag_id = rfid.read_tag(timeout=5)
    # ... more logic
```

---

## Best Practices

### 1. Always Stop Inventory
Always call `stop_inventory()` before closing or before starting a new inventory:
```python
try:
    reader.start_inventory()
    # ... read tags
finally:
    reader.stop_inventory()
    reader.close()
```

### 2. Use Appropriate Timeouts
- Short timeout (100-500ms): Fast response, may miss tags
- Medium timeout (1000-2000ms): Balanced
- Long timeout (5000+ms): Ensure tag detection, slower response

### 3. Power Settings for Range
- Start with medium power (15) and adjust based on results
- Higher power = more RF interference, higher power consumption
- Lower power = more reliable in dense tag environments

### 4. Error Handling
```python
try:
    reader.start_inventory()
    tag = reader.get_tag()
except CHAFONCF591Error as e:
    print(f"RFID Error: {e}")
    reader.stop_inventory()
```

### 5. Multiple Tags
If multiple tags are in range, `GetTagUii()` will return them one by one. Keep calling it in a loop to get all tags.

---

## Summary of Capabilities

| Feature | Supported | Notes |
|---------|-----------|-------|
| Read tags | ✓ | Continuous or single tag |
| Write tags | ✓ | Requires access password for locked tags |
| Lock/Kill tags | ✓ | Permanent operations |
| Adjust range | ✓ | Via RF power (0-30) |
| Trigger control | ✓ | Software or hardware GPIO trigger |
| Filter by EPC | ✓ | Using select mask |
| RSSI measurement | ✓ | Signal strength in dBm |
| Multi-antenna | ✓ | Up to 8 antennas (hardware dependent) |
| Network connection | ✓ | TCP/IP for compatible models |
| Read TID/User memory | ✓ | Full memory access |
| Session control | ✓ | S0, S1, S2, S3 |
| Frequency hopping | ✓ | Regional compliance |

---

## Troubleshooting

### Device Not Found
```bash
# Check connection
lsusb
ls -l /dev/ttyUSB*

# Fix permissions
sudo chmod 666 /dev/ttyUSB0
```

### Library Not Found
```bash
# Install library
sudo cp API/Linux/ARM64/libCFApi.so /usr/local/lib/
sudo ldconfig
```

### No Tags Detected
1. Check power settings (increase if needed)
2. Verify tags are UHF compatible
3. Check antenna connection
4. Verify frequency region matches your location

### Slow Reading
1. Increase RF power
2. Adjust Q value
3. Optimize session settings
4. Reduce filter time

---

## Quick Reference

### Workflow
1. **Open** → 2. **Set Power** → 3. **Start Inventory** → 4. **Get Tags** → 5. **Stop** → 6. **Close**

### Key Functions for Your Use Case
```python
# Connect
reader.open_device('/dev/ttyUSB0', 115200)

# Set range (3 meters)
reader.set_rf_power(12)

# Trigger: Start reading
reader.start_inventory()

# Read first tag
tag = reader.get_tag(timeout_ms=5000)

# Stop immediately
reader.stop_inventory()

# Process
if tag:
    print(tag['epc'])

# Disconnect
reader.close()
```

---

## Additional Resources

- **API Header**: `API/Linux/CFApi.h` - Complete function reference
- **Sample Code**: `rfid_reader_example.c` - C implementation
- **Python Wrapper**: `rfid_reader_python.py` - Basic wrapper
- **Advanced Wrapper**: `chafon_cf591.py` - Full-featured wrapper

For questions or issues, refer to the official CHAFON documentation in the `User Guide/` directory.


