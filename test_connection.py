#!/usr/bin/env python3
"""
Test script to debug CHAFON CF591 connection
"""

import sys
import ctypes
from chafon_cf591 import CF591Reader, StatusCode

def test_connection(port='/dev/ttyUSB0', baud_rate=115200):
    """Test connection with detailed error reporting"""
    
    print("=" * 60)
    print("CHAFON CF591 Connection Test")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"Baud Rate: {baud_rate}")
    print()
    
    # Check device exists
    import os
    if not os.path.exists(port):
        print(f"ERROR: Device {port} does not exist!")
        print("Available devices:")
        import glob
        for dev in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
            print(f"  {dev}")
        return False
    
    print(f"✓ Device {port} exists")
    
    # Check permissions
    import stat
    mode = os.stat(port).st_mode
    if not (mode & stat.S_IRUSR and mode & stat.S_IWUSR):
        print(f"⚠ WARNING: May not have read/write permissions on {port}")
    else:
        print(f"✓ Permissions OK")
    
    print()
    print("Attempting to connect...")
    
    # Try different baud rates
    baud_rates = [115200, 9600, 19200, 38400, 57600]
    
    for baud in baud_rates:
        print(f"\nTrying baud rate: {baud}...")
        try:
            reader = CF591Reader(port, baud)
            reader.open()
            print(f"✓ SUCCESS! Connected at {baud} baud")
            
            # Try to get device info
            try:
                info = reader.get_device_info()
                print("\nDevice Information:")
                print(f"  Firmware: {info['firmware_version']}")
                print(f"  Hardware: {info['hardware_version']}")
                print(f"  Serial:   {info['serial_number']}")
            except Exception as e:
                print(f"⚠ Could not get device info: {e}")
            
            reader.close()
            return True
            
        except Exception as e:
            error_code = getattr(e, 'error_code', None)
            if error_code is not None:
                # Convert to unsigned for display
                if error_code < 0:
                    unsigned_code = error_code & 0xFFFFFFFF
                else:
                    unsigned_code = error_code
                print(f"  Error code: 0x{unsigned_code:08X} ({error_code})")
                
                # Map error codes
                error_messages = {
                    0xFFFFFF01: "PORT_HANDLE_ERR - Handle error or input serial port parameter error",
                    0xFFFFFF02: "PORT_OPEN_FAILED - Failed to open serial port",
                    0xFFFFFF03: "DLL_INNER_FAILED - Internal error in dynamic library",
                }
                if unsigned_code in error_messages:
                    print(f"  Meaning: {error_messages[unsigned_code]}")
            else:
                print(f"  Error: {e}")
            continue
    
    print("\n✗ Failed to connect with all baud rates")
    return False

if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    success = test_connection(port)
    sys.exit(0 if success else 1)

