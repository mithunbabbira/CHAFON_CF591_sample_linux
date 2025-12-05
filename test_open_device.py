#!/usr/bin/env python3
"""
Direct test of OpenDevice function
"""

import ctypes
import sys

# Load library
lib = ctypes.CDLL('libCFApi.so')

# Define function signature
lib.OpenDevice.argtypes = [ctypes.POINTER(ctypes.c_int64), ctypes.c_char_p, ctypes.c_int]
lib.OpenDevice.restype = ctypes.c_int

# Constants
STAT_OK = 0x00000000
STAT_PORT_HANDLE_ERR = 0xFFFFFF01
STAT_PORT_OPEN_FAILED = 0xFFFFFF02

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
baud_rate = 115200

print(f"Testing OpenDevice with:")
print(f"  Port: {port}")
print(f"  Baud: {baud_rate}")
print()

# Initialize handle
handle = ctypes.c_int64(-1)
print(f"Handle before: {handle.value} (0x{handle.value & 0xFFFFFFFFFFFFFFFF:016X})")

# Prepare port string
port_bytes = port.encode('utf-8')
print(f"Port bytes: {port_bytes} (length: {len(port_bytes)})")

# Call OpenDevice
print("\nCalling OpenDevice...")
result = lib.OpenDevice(ctypes.byref(handle), port_bytes, baud_rate)

print(f"Handle after: {handle.value} (0x{handle.value & 0xFFFFFFFFFFFFFFFF:016X})")
print(f"Result: 0x{result & 0xFFFFFFFF:08X} ({result})")

if result == STAT_OK:
    print("✓ SUCCESS!")
    lib.CloseDevice(handle)
elif result == STAT_PORT_HANDLE_ERR:
    print("✗ PORT_HANDLE_ERR - Handle or parameter error")
elif result == STAT_PORT_OPEN_FAILED:
    print("✗ PORT_OPEN_FAILED - Failed to open serial port")
else:
    print(f"✗ Unknown error: 0x{result & 0xFFFFFFFF:08X}")

