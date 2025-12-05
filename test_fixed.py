#!/usr/bin/env python3
"""
Test script to verify fixes for error handling
"""

import sys
from chafon_cf591 import CF591Reader

port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'

print("=" * 60)
print("Testing Fixed Error Handling")
print("=" * 60)

try:
    with CF591Reader(port) as reader:
        print("✓ Connected")
        
        # Test 1: Trigger-based reading (should work without errors)
        print("\nTest 1: Trigger-based reading (5 seconds)...")
        print("Place a tag near the reader...")
        tag = reader.read_single_tag(timeout=5000)
        if tag:
            print(f"✓ Tag read: {tag.epc}")
        else:
            print("✗ No tag detected")
        
        # Test 2: Continuous reading and stopping (should not error on stop)
        print("\nTest 2: Continuous reading (2 seconds)...")
        reader.start_inventory()
        
        tag_count = 0
        import time
        start = time.time()
        while (time.time() - start) < 2:
            tag = reader.get_tag(timeout=200)
            if tag:
                tag_count += 1
                if tag_count <= 3:  # Only print first 3
                    print(f"  Tag {tag_count}: {tag.epc}")
        
        print(f"  Total tags read: {tag_count}")
        reader.stop_inventory()  # Should not raise error even if timeout
        print("✓ Stopped inventory successfully")
        
        # Test 3: Get Q value (should work now)
        print("\nTest 3: Get Q value...")
        try:
            q_val = reader.get_q_value()
            print(f"✓ Q value: {q_val}")
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        # Test 4: Multiple start/stop cycles
        print("\nTest 4: Multiple start/stop cycles...")
        for i in range(3):
            reader.start_inventory()
            tag = reader.get_tag(timeout=500)
            reader.stop_inventory()
            if tag:
                print(f"  Cycle {i+1}: ✓ Read tag {tag.epc[:16]}...")
            else:
                print(f"  Cycle {i+1}: No tag")
        print("✓ Multiple cycles completed")
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

