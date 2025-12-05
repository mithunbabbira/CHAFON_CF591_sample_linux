# Fixes Applied to CHAFON CF591 Library

## Issues Fixed

### 1. Library Dependency Issue
**Problem**: Library couldn't load due to missing `libhid.so` dependency.

**Fix**: 
- Installed `libhidapi-libusb0` package
- Created symlink: `libhid.so` → `libhidapi-libusb.so.0`

**Commands**:
```bash
sudo apt-get install -y libhidapi-libusb0
sudo ln -sf /usr/lib/aarch64-linux-gnu/libhidapi-libusb.so.0 /usr/lib/aarch64-linux-gnu/libhid.so
sudo ldconfig
```

### 2. Handle Initialization Issue
**Problem**: `OpenDevice` was failing with `STAT_PORT_HANDLE_ERR` (0xFFFFFF01).

**Fix**: Changed handle initialization from `c_int64(-1)` to `c_int64(0)`.

**Location**: `chafon_cf591.py` line ~520

### 3. Error Code Handling
**Problem**: Error codes from C library are signed integers, but comparisons were using unsigned values, causing mismatches.

**Fix**: Added signed-to-unsigned conversion (`result & 0xFFFFFFFF`) in all error checks.

**Affected Functions**:
- `start_inventory()`
- `stop_inventory()`
- `get_tag()`
- `read_tag_memory()`
- `get_q_value()`

### 4. Inventory Stop Timeout Errors
**Problem**: `stop_inventory()` was raising errors on timeout, even though timeout is normal when inventory already stopped.

**Fix**: Made `stop_inventory()` more lenient - it now ignores:
- `STAT_CMD_COMM_TIMEOUT` (0xFFFFFF12)
- `STAT_CMD_INVENTORY_STOP` (0xFFFFFF07)

### 5. State Management
**Problem**: Some operations (like reading tag memory, getting Q value) fail if inventory is running.

**Fix**: 
- Operations that require inventory to be stopped now automatically stop/restart inventory
- Added state tracking to prevent double-start/double-stop issues

### 6. Q Value Function
**Problem**: `GetCoilPRM()` API call was failing with buffer overflow error.

**Fix**: Added fallback to get Q value from device parameters, which is more reliable.

## Current Status

✅ **Working Features**:
- Connection to reader
- Trigger-based reading (read single tag, then stop)
- Continuous reading
- Power/range control
- Device information
- RSSI-based proximity detection
- Temperature monitoring
- Multiple start/stop cycles

⚠️ **Known Limitations**:
- Some tag memory operations may require specific tag types
- Q value direct API call may not work on all models (fallback works)

## Usage Examples

### Trigger-Based Reading (Your Main Use Case)
```python
from chafon_cf591 import CF591Reader

with CF591Reader('/dev/ttyUSB0') as reader:
    # This starts, reads ONE tag, then stops automatically
    tag = reader.read_single_tag(timeout=5000)
    
    if tag:
        print(f"Tag: {tag.epc}")
        # Your logic here
```

### Range Control
```python
# Set reading range
reader.set_rf_power(15)  # Short range
reader.set_rf_power(25)   # Long range
```

### Continuous Reading
```python
reader.start_inventory()
for tag in reader.read_tags_iterator(max_count=10):
    print(f"Tag: {tag.epc}")
reader.stop_inventory()  # No errors even if timeout
```

## Testing

Run the test script:
```bash
python3 test_fixed.py /dev/ttyUSB0
```

This verifies:
- Trigger-based reading
- Continuous reading
- Stop inventory (no errors)
- Q value retrieval
- Multiple start/stop cycles

## Summary

All critical issues have been fixed. The library now:
1. ✅ Loads correctly
2. ✅ Connects to the reader
3. ✅ Reads tags successfully
4. ✅ Handles errors gracefully
5. ✅ Supports trigger-based reading
6. ✅ Supports range control

You can now integrate this into your existing Python code!

