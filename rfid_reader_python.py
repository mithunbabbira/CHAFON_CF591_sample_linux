#!/usr/bin/env python3
"""
CHAFON CF591 RFID Reader Python Wrapper for Raspberry Pi

This is a Python wrapper using ctypes to interface with the libCFApi.so library.
It provides a simple Python API for reading RFID tags.

Requirements:
    - ctypes (built-in)
    - libCFApi.so must be installed or in LD_LIBRARY_PATH

Usage:
    from rfid_reader_python import RFIDReader
    
    reader = RFIDReader('/dev/ttyUSB0', 115200)
    reader.open()
    
    tags = reader.read_tags(timeout=5000)
    for tag in tags:
        print(f"EPC: {tag['epc']}, RSSI: {tag['rssi']}")
    
    reader.close()
"""

import ctypes
import ctypes.util
from ctypes import Structure, POINTER, c_int64, c_char_p, c_int, c_ubyte, c_ushort, c_short
import os
import sys

# Load the library
def load_library():
    """Load libCFApi.so from common locations"""
    # Try to find library in standard locations
    lib_paths = [
        '/usr/local/lib/libCFApi.so',
        '/usr/lib/libCFApi.so',
        './API/Linux/ARM/libCFApi.so',
        './API/Linux/ARM64/libCFApi.so',
        ctypes.util.find_library('CFApi')
    ]
    
    for lib_path in lib_paths:
        if lib_path and os.path.exists(lib_path):
            try:
                return ctypes.CDLL(lib_path)
            except OSError:
                continue
    
    raise OSError("Could not find libCFApi.so. Please ensure it is installed or in LD_LIBRARY_PATH")

try:
    lib = load_library()
except OSError as e:
    print(f"Error: {e}")
    print("\nTo fix this:")
    print("1. Copy libCFApi.so to /usr/local/lib/")
    print("2. Run: sudo ldconfig")
    print("3. Or set LD_LIBRARY_PATH to the library directory")
    sys.exit(1)

# Define constants
STAT_OK = 0x00000000
STAT_PORT_OPEN_FAILED = 0xFFFFFF02
STAT_CMD_INVENTORY_STOP = 0xFFFFFF07
STAT_CMD_COMM_TIMEOUT = 0xFFFFFF12

# Define TagInfo structure
class TagInfo(Structure):
    _fields_ = [
        ("NO", c_ushort),
        ("rssi", c_short),
        ("antenna", c_ubyte),
        ("channel", c_ubyte),
        ("crc", c_ubyte * 2),
        ("pc", c_ubyte * 2),
        ("codeLen", c_ubyte),
        ("code", c_ubyte * 255)
    ]

# Define function signatures
lib.OpenDevice.argtypes = [POINTER(c_int64), c_char_p, c_int]
lib.OpenDevice.restype = c_int

lib.CloseDevice.argtypes = [c_int64]
lib.CloseDevice.restype = c_int

lib.InventoryContinue.argtypes = [c_int64, c_ubyte, ctypes.c_ulong]
lib.InventoryContinue.restype = c_int

lib.GetTagUii.argtypes = [c_int64, POINTER(TagInfo), c_ushort]
lib.GetTagUii.restype = c_int

lib.InventoryStop.argtypes = [c_int64, c_ushort]
lib.InventoryStop.restype = c_int

lib.GetInfo.argtypes = [c_int64, POINTER(ctypes.c_ubyte * 88)]  # DeviceInfo structure
lib.GetInfo.restype = c_int


class RFIDReader:
    """Python wrapper for CHAFON CF591 RFID Reader"""
    
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200):
        """
        Initialize RFID reader
        
        Args:
            port: Serial port path (e.g., '/dev/ttyUSB0')
            baud_rate: Baud rate (default: 115200)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.handle = c_int64(-1)
        self.is_open = False
    
    def open(self):
        """Open connection to RFID reader"""
        if self.is_open:
            raise RuntimeError("Reader is already open")
        
        port_bytes = self.port.encode('utf-8')
        result = lib.OpenDevice(ctypes.byref(self.handle), port_bytes, self.baud_rate)
        
        if result != STAT_OK:
            raise IOError(f"Failed to open device: Error code 0x{result:08X}")
        
        self.is_open = True
        return True
    
    def close(self):
        """Close connection to RFID reader"""
        if not self.is_open:
            return
        
        lib.CloseDevice(self.handle)
        self.handle = c_int64(-1)
        self.is_open = False
    
    def start_inventory(self, inv_count=0, inv_param=0):
        """
        Start inventory (tag reading)
        
        Args:
            inv_count: Number of tags to read (0 = continuous)
            inv_param: Inventory parameters (0 = default)
        """
        if not self.is_open:
            raise RuntimeError("Reader is not open")
        
        result = lib.InventoryContinue(self.handle, inv_count, inv_param)
        if result != STAT_OK:
            raise IOError(f"Failed to start inventory: Error code 0x{result:08X}")
    
    def stop_inventory(self, timeout=5000):
        """
        Stop inventory
        
        Args:
            timeout: Timeout in milliseconds
        """
        if not self.is_open:
            raise RuntimeError("Reader is not open")
        
        result = lib.InventoryStop(self.handle, timeout)
        if result != STAT_OK:
            raise IOError(f"Failed to stop inventory: Error code 0x{result:08X}")
    
    def read_tag(self, timeout=1000):
        """
        Read a single tag
        
        Args:
            timeout: Timeout in milliseconds
        
        Returns:
            Dictionary with tag information or None if no tag found
        """
        if not self.is_open:
            raise RuntimeError("Reader is not open")
        
        tag_info = TagInfo()
        result = lib.GetTagUii(self.handle, ctypes.byref(tag_info), timeout)
        
        if result == STAT_OK:
            # Convert EPC code to hex string
            epc_bytes = bytes(tag_info.code[:tag_info.codeLen])
            epc_hex = ''.join(f'{b:02X}' for b in epc_bytes)
            
            return {
                'epc': epc_hex,
                'epc_bytes': epc_bytes,
                'rssi': tag_info.rssi / 10.0,  # Convert to dBm
                'antenna': tag_info.antenna,
                'channel': tag_info.channel,
                'crc': bytes(tag_info.crc).hex().upper(),
                'pc': bytes(tag_info.pc).hex().upper(),
                'length': tag_info.codeLen,
                'sequence': tag_info.NO
            }
        elif result == STAT_CMD_INVENTORY_STOP:
            return None  # No more tags
        elif result == STAT_CMD_COMM_TIMEOUT:
            return None  # Timeout
        else:
            raise IOError(f"Failed to read tag: Error code 0x{result:08X}")
    
    def read_tags(self, max_tags=None, timeout=1000, stop_on_timeout=False):
        """
        Read multiple tags
        
        Args:
            max_tags: Maximum number of tags to read (None = unlimited)
            timeout: Timeout per tag read in milliseconds
            stop_on_timeout: Stop reading if timeout occurs
        
        Returns:
            List of tag dictionaries
        """
        tags = []
        consecutive_timeouts = 0
        max_consecutive_timeouts = 3 if stop_on_timeout else 1000
        
        while True:
            if max_tags and len(tags) >= max_tags:
                break
            
            tag = self.read_tag(timeout)
            
            if tag:
                tags.append(tag)
                consecutive_timeouts = 0
            else:
                consecutive_timeouts += 1
                if consecutive_timeouts >= max_consecutive_timeouts:
                    break
        
        return tags
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == '__main__':
    import time
    
    print("CHAFON CF591 RFID Reader - Python Example")
    print("=" * 40)
    
    # Get port from command line or use default
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    try:
        # Create reader instance
        reader = RFIDReader(port, 115200)
        
        # Open connection
        print(f"Opening connection to {port}...")
        reader.open()
        print("Connected!")
        
        # Start inventory
        print("\nStarting inventory...")
        reader.start_inventory()
        print("Reading tags (Press Ctrl+C to stop)...\n")
        
        tag_count = 0
        
        try:
            while True:
                tag = reader.read_tag(timeout=1000)
                
                if tag:
                    tag_count += 1
                    print(f"Tag #{tag_count}:")
                    print(f"  EPC: {tag['epc']}")
                    print(f"  RSSI: {tag['rssi']:.1f} dBm")
                    print(f"  Antenna: {tag['antenna']}")
                    print(f"  Channel: {tag['channel']}")
                    print()
                
                time.sleep(0.1)  # Small delay
                
        except KeyboardInterrupt:
            print("\nStopping...")
        
        # Stop inventory
        reader.stop_inventory()
        
        # Close connection
        reader.close()
        
        print(f"\nTotal tags read: {tag_count}")
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

