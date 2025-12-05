# CHAFON CF591 RFID Reader - Complete API Documentation

## Overview

This document provides comprehensive information about all programmable operations available for the CHAFON CF591 RFID reader on Linux/Raspberry Pi 5.

## Table of Contents

1. [Connection Management](#connection-management)
2. [Device Information](#device-information)
3. [Tag Reading Operations](#tag-reading-operations)
4. [Power and Range Control](#power-and-range-control)
5. [Trigger Configuration](#trigger-configuration)
6. [Antenna Configuration](#antenna-configuration)
7. [Frequency Configuration](#frequency-configuration)
8. [GPIO Operations](#gpio-operations)
9. [Tag Operations](#tag-operations)
10. [Network Configuration](#network-configuration)
11. [Error Codes](#error-codes)

---

## Connection Management

### Serial Port Connection

```python
reader = CHAFONCF591()
reader.open_device('/dev/ttyUSB0', baudrate=115200)
```

**Parameters:**
- `port`: Serial port path (e.g., `/dev/ttyUSB0`, `/dev/ttyACM0`)
- `baudrate`: Baud rate (typically 115200)

**Common Serial Ports:**
- `/dev/ttyUSB0` - USB to Serial adapter
- `/dev/ttyACM0` - USB CDC device
- `/dev/ttyAMA0` - Raspberry Pi GPIO serial

### Network Connection

```python
reader.open_network('192.168.1.100', port=4001, timeout_ms=2000)
```

**Parameters:**
- `ip`: IP address of the reader
- `port`: Network port (default: 4001)
- `timeout_ms`: Connection timeout in milliseconds

### Close Connection

```python
reader.close()
```

---

## Device Information

### Get Device Info

```python
info = reader.get_info()
# Returns: {'firmware_version', 'hardware_version', 'serial_number'}
```

### Get Device Parameters

```python
params = reader.get_device_parameters()
# Returns dictionary with all device parameters
```

**Key Parameters:**
- `work_mode`: 0 = Answer mode (trigger required), 1 = Active mode (continuous)
- `rf_power`: RF power level (0-30)
- `trigger_time`: Trigger valid time in seconds
- `antenna`: Active antenna (bitmask)
- `q_value`: Q algorithm value
- `session`: Session parameter
- `region`: Frequency region
- `start_frequency`, `stop_frequency`, `step_frequency`: Frequency range

### Set Device Parameters

```python
reader.set_device_parameters(
    work_mode=0,        # 0=Answer/Trigger mode, 1=Active mode
    rf_power=20,       # 0-30
    trigger_time=5,    # seconds
    antenna=0xFF,      # Bitmask for antennas
    q_value=4,         # Q algorithm value
    session=0          # Session parameter
)
```

---

## Tag Reading Operations

### Start Inventory

```python
reader.start_inventory(inv_count=0, inv_param=0)
```

**Parameters:**
- `inv_count`: Number of inventory rounds (0 = continuous)
- `inv_param`: Inventory parameter (default: 0)

### Get Tag

```python
tag = reader.get_tag(timeout_ms=1000)
```

**Returns:** Dictionary with:
- `epc`: EPC code as hex string
- `epc_bytes`: EPC as bytes
- `rssi`: RSSI in dBm
- `antenna`: Antenna number (1-8)
- `channel`: Channel number
- `sequence`: Tag sequence number

**Returns `None` if:**
- No tag available
- Inventory ended
- Timeout occurred

### Stop Inventory

```python
reader.stop_inventory(timeout_ms=1000)
```

### Read Single Tag (Convenience Method)

```python
tag = reader.read_tag_once(timeout_ms=2000)
# Automatically starts inventory, reads one tag, then stops
```

---

## Power and Range Control

### Get RF Power

```python
power = reader.get_rf_power()
# Returns: 0-30
```

### Set RF Power (Reading Range)

```python
reader.set_rf_power(power=20)  # 0-30, higher = longer range
```

**Power Levels:**
- **0-10**: Short range (0.5-1 meter)
- **11-20**: Medium range (1-3 meters)
- **21-30**: Long range (3-5+ meters)

**Note:** Higher power increases reading range but may cause interference and consume more power.

### Get Antenna Power

```python
ant_power = reader.get_antenna_power()
# Returns: {'enable': bool, 'antenna_powers': [list of 8 power levels]}
```

### Set Antenna Power (Individual Antennas)

```python
reader.set_antenna_power(
    enable=True,
    antenna_powers=[20, 20, 20, 20, 0, 0, 0, 0]  # Power for antennas 1-8
)
```

**Use Cases:**
- Different power levels for different antennas
- Disable specific antennas by setting power to 0
- Optimize reading pattern for specific antenna configuration

---

## Trigger Configuration

### Trigger Modes

The CHAFON CF591 supports two work modes:

1. **Answer Mode (Work Mode = 0)**
   - Requires trigger signal to start reading
   - Reading stops after trigger time expires or manually stopped
   - Ideal for on-demand reading

2. **Active Mode (Work Mode = 1)**
   - Continuous reading without trigger
   - Reading continues until manually stopped
   - Ideal for continuous monitoring

### Configure Trigger Mode

```python
# Answer mode with 5-second trigger window
reader.set_device_parameters(
    work_mode=0,        # Answer mode (trigger required)
    trigger_time=5      # Trigger valid for 5 seconds
)

# Active mode (no trigger needed)
reader.set_device_parameters(
    work_mode=1         # Active mode (continuous)
)
```

### Trigger Implementation Example

```python
# Wait for trigger, then read until tag found
reader.set_device_parameters(work_mode=0, trigger_time=10)
reader.start_inventory()

tag = None
while tag is None:
    tag = reader.get_tag(timeout_ms=500)
    # Process trigger signal here if needed

reader.stop_inventory()
```

---

## Antenna Configuration

### Get Antenna Configuration

```python
antenna = reader.get_antenna()
# Returns: Antenna bitmask (0xFF = all antennas)
```

### Set Antenna Configuration

```python
# Enable specific antennas
reader.set_antenna(antenna_mask=0x0F)  # Enable antennas 1-4
```

**Antenna Bitmask:**
- Bit 0: Antenna 1
- Bit 1: Antenna 2
- Bit 2: Antenna 3
- Bit 3: Antenna 4
- Bit 4: Antenna 5
- Bit 5: Antenna 6
- Bit 6: Antenna 7
- Bit 7: Antenna 8
- `0xFF`: All antennas
- `0x01`: Only antenna 1

---

## Frequency Configuration

### Get Frequency Settings

```python
freq_info = reader.get_freq()
# Returns: {'region', 'StartFreq', 'StopFreq', 'StepFreq', 'cnt'}
```

### Set Frequency Settings

```python
from chafon_cf591 import FreqInfo

freq = FreqInfo()
freq.region = 1  # Region code
freq.StartFreq = 920  # Start frequency in MHz
freq.StopFreq = 925   # Stop frequency in MHz
freq.StepFreq = 1     # Step frequency in MHz
freq.cnt = 1          # Count

reader.set_freq(freq)
```

**Common Regions:**
- Region 0: China (920-925 MHz)
- Region 1: US (902-928 MHz)
- Region 2: Europe (865-868 MHz)
- Region 3: Japan (952-955 MHz)

---

## GPIO Operations

### GPIO Parameters

The reader supports GPIO (General Purpose Input/Output) for:
- Trigger input
- Relay control
- External device control

**Note:** GPIO functions require hardware support and may not be available on all models.

---

## Tag Operations

### Read Tag Data

The reader supports reading data from tag memory banks:
- **Bank 0**: Reserved
- **Bank 1**: EPC
- **Bank 2**: TID
- **Bank 3**: User

**Note:** These operations require low-level API access and are not currently implemented in the high-level wrapper. They can be added if needed.

### Write Tag Data

Writing to tag memory banks is supported but requires:
- Access password
- Proper memory bank selection
- Write permissions

### Lock Tag

Locking tags prevents further writes to specific memory areas.

### Kill Tag

Killing a tag permanently disables it (irreversible).

---

## Network Configuration

### Network Parameters

The reader can be configured for network operation:
- IP address
- Subnet mask
- Gateway
- Port configuration

**Note:** Network configuration requires device-specific setup and may vary by model.

---

## Error Codes

### Success Codes

- `STAT_OK (0x00000000)`: Operation successful

### Error Codes

- `STAT_PORT_HANDLE_ERR (0xFFFFFF01)`: Port handle error
- `STAT_PORT_OPEN_FAILED (0xFFFFFF02)`: Failed to open port
- `STAT_CMD_PARAM_ERR (0xFFFFFF04)`: Parameter error
- `STAT_CMD_INVENTORY_STOP (0xFFFFFF07)`: Inventory stopped or ended
- `STAT_CMD_TAG_NO_RESP (0xFFFFFF08)`: Tag not responding
- `STAT_CMD_COMM_TIMEOUT (0xFFFFFF12)`: Communication timeout
- `STAT_CMD_NOMORE_DATA (0xFFFFFF15)`: No more data available

### Handling Errors

```python
try:
    tag = reader.get_tag()
except CHAFONCF591Error as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

---

## Best Practices

### 1. Reading Range Optimization

```python
# Start with medium power
reader.set_rf_power(20)

# Adjust based on results
# If tags too close: reduce power
# If tags too far: increase power
```

### 2. Trigger-Based Reading

```python
# Configure for trigger mode
reader.set_device_parameters(work_mode=0, trigger_time=5)

# Start inventory
reader.start_inventory()

# Read until tag found
tag = None
while tag is None:
    tag = reader.get_tag(timeout_ms=500)
    # Check for trigger signal here

# Stop immediately after reading
reader.stop_inventory()
```

### 3. Continuous Reading

```python
# Configure for active mode
reader.set_device_parameters(work_mode=1)

# Start continuous reading
reader.start_inventory()

tags = []
try:
    while True:
        tag = reader.get_tag(timeout_ms=1000)
        if tag:
            tags.append(tag)
            print(f"Tag: {tag['epc']}")
except KeyboardInterrupt:
    pass
finally:
    reader.stop_inventory()
```

### 4. Power Management

```python
# Use appropriate power level for your use case
# Lower power = less interference, shorter range
# Higher power = longer range, more interference

# For close-range reading (0.5-1m)
reader.set_rf_power(10)

# For medium-range reading (1-3m)
reader.set_rf_power(20)

# For long-range reading (3-5m+)
reader.set_rf_power(30)
```

---

## Advanced Features

### RSSI Filtering

RSSI (Received Signal Strength Indicator) filtering allows filtering tags based on signal strength:

```python
# This requires low-level API access
# Can be implemented if needed
```

### Q Algorithm Configuration

The Q algorithm controls tag collision handling:

```python
reader.set_device_parameters(q_value=4)  # Typical values: 0-15
```

**Q Value Guidelines:**
- **Low Q (0-4)**: Few tags, faster reading
- **Medium Q (4-8)**: Moderate tag count
- **High Q (8-15)**: Many tags, slower but more reliable

### Session Configuration

Session parameter controls tag state:

```python
reader.set_device_parameters(session=0)  # 0-3
```

**Session Values:**
- **0**: S0 (default)
- **1**: S1
- **2**: S2
- **3**: S3

---

## Troubleshooting

### Common Issues

1. **Cannot connect to device**
   - Check serial port path: `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`
   - Verify baud rate matches device configuration
   - Check USB connection and drivers

2. **No tags read**
   - Verify tags are within range
   - Check RF power level (increase if needed)
   - Verify antenna connection
   - Check work mode (trigger vs active)

3. **Tags read intermittently**
   - Increase RF power
   - Check antenna positioning
   - Verify tag orientation
   - Check for interference

4. **Timeout errors**
   - Increase timeout value
   - Check device connection
   - Verify device is responding

---

## Additional Resources

- CHAFON CF591 User Manual
- Linux API Header: `API/Linux/CFApi.h`
- Sample Code: `Sample/C#/` and `Sample/VB/`

---

## Support

For additional support, refer to:
- CHAFON official documentation
- Device user manual
- Technical support contacts

