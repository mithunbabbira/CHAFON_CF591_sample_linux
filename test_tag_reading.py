#!/usr/bin/env python3
"""
Test tag reading with the CHAFON CF591
"""

import sys
import time
from chafon_cf591 import CF591Reader

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'

print("=" * 60)
print("CHAFON CF591 Tag Reading Test")
print("=" * 60)
print(f"Port: {port}")
print()

try:
    with CF591Reader(port) as reader:
        print("✓ Connected to reader")
        
        # Get device info
        info = reader.get_device_info()
        print(f"\nDevice Info:")
        print(f"  Firmware: {info['firmware_version']}")
        print(f"  Hardware: {info['hardware_version']}")
        print(f"  Serial:   {info['serial_number']}")
        
        # Get current power
        power = reader.get_rf_power()
        print(f"\nCurrent RF Power: {power} dBm")
        
        # Test 1: Read single tag (trigger-based)
        print("\n" + "=" * 60)
        print("Test 1: Reading single tag (trigger-based)")
        print("=" * 60)
        print("Place an RFID tag near the reader...")
        print("Waiting up to 10 seconds...\n")
        
        tag = reader.read_single_tag(timeout=10000)
        
        if tag:
            print("✓ TAG DETECTED!")
            print(f"  EPC:     {tag.epc}")
            print(f"  RSSI:    {tag.rssi:.1f} dBm")
            print(f"  Antenna: {tag.antenna}")
            print(f"  Channel: {tag.channel}")
            print(f"  Length:  {tag.length} bytes")
        else:
            print("✗ No tag detected within timeout")
        
        # Test 2: Continuous reading
        print("\n" + "=" * 60)
        print("Test 2: Continuous reading (5 seconds)")
        print("=" * 60)
        print("Move tags near the reader...\n")
        
        reader.start_inventory()
        
        start_time = time.time()
        tag_count = 0
        
        while (time.time() - start_time) < 5:
            tag = reader.get_tag(timeout=500)
            if tag:
                tag_count += 1
                print(f"Tag #{tag_count}: {tag.epc} (RSSI: {tag.rssi:.1f} dBm)")
        
        reader.stop_inventory()
        print(f"\nTotal tags read: {tag_count}")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

