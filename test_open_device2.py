#!/usr/bin/env python3
"""
Test OpenDevice with different handle initialization methods
"""

import ctypes
import sys

# Load library
lib = ctypes.CDLL('libCFApi.so')

# Define function signature
lib.OpenDevice.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_char_p, ctypes.c_int]
lib.OpenDevice.restype = ctypes.c_int

STAT_OK = 0x00000000
STAT_PORT_HANDLE_ERR = 0xFFFFFF01

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
baud_rate = 115200

print("Testing different handle initialization methods...\n")

# Method 1: Current method (c_int64 with -1)
print("Method 1: c_int64(-1)")
handle1 = ctypes.c_int64(-1)
result1 = lib.OpenDevice(ctypes.byref(handle1), port.encode('utf-8'), baud_rate)
print(f"  Result: 0x{result1 & 0xFFFFFFFF:08X}")
if result1 == STAT_OK:
    print("  ✓ SUCCESS!")
    lib.CloseDevice(handle1)
else:
    print(f"  ✗ Failed: {result1}")

# Method 2: Allocate memory for handle
print("\nMethod 2: Allocated memory")
handle2 = (ctypes.c_int64 * 1)(-1)
result2 = lib.OpenDevice(handle2, port.encode('utf-8'), baud_rate)
print(f"  Result: 0x{result2 & 0xFFFFFFFF:08X}")
if result2 == STAT_OK:
    print("  ✓ SUCCESS!")
    lib.CloseDevice(handle2[0])
else:
    print(f"  ✗ Failed: {result2}")

# Method 3: Zero-initialized
print("\nMethod 3: Zero-initialized")
handle3 = ctypes.c_int64(0)
result3 = lib.OpenDevice(ctypes.byref(handle3), port.encode('utf-8'), baud_rate)
print(f"  Result: 0x{result3 & 0xFFFFFFFF:08X}")
if result3 == STAT_OK:
    print("  ✓ SUCCESS!")
    lib.CloseDevice(handle3)
else:
    print(f"  ✗ Failed: {result3}")

# Method 4: Try with different port format
print("\nMethod 4: Port as bytes with null terminator")
handle4 = ctypes.c_int64(-1)
port_bytes = (port + '\0').encode('utf-8')
result4 = lib.OpenDevice(ctypes.byref(handle4), port_bytes, baud_rate)
print(f"  Result: 0x{result4 & 0xFFFFFFFF:08X}")
if result4 == STAT_OK:
    print("  ✓ SUCCESS!")
    lib.CloseDevice(handle4)
else:
    print(f"  ✗ Failed: {result4}")

# Check if device is actually accessible
print("\nChecking device accessibility...")
import os
import stat
if os.path.exists(port):
    st = os.stat(port)
    print(f"  Device exists: ✓")
    print(f"  Mode: {oct(st.st_mode)}")
    print(f"  Readable: {os.access(port, os.R_OK)}")
    print(f"  Writable: {os.access(port, os.W_OK)}")
    
    # Try to open it directly
    try:
        fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        os.close(fd)
        print(f"  Can open directly: ✓")
    except Exception as e:
        print(f"  Can open directly: ✗ ({e})")
else:
    print(f"  Device exists: ✗")

