#!/usr/bin/env python3
"""
CHAFON CF591 RFID Reader - Usage Examples

This file demonstrates various use cases for the CF591 RFID reader.
Run with: python3 examples.py
"""

import time
import sys
from chafon_cf591 import (
    CF591Reader, Tag, MemoryBank, LockAction, LockArea, Region, WorkMode
)


def example_basic_reading():
    """
    Example 1: Basic Tag Reading
    
    The simplest way to read RFID tags.
    """
    print("\n" + "=" * 60)
    print("Example 1: Basic Tag Reading")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("Reading tags for 5 seconds...")
        
        reader.start_inventory()
        
        start_time = time.time()
        while (time.time() - start_time) < 5:
            tag = reader.get_tag(timeout=500)
            if tag:
                print(f"  Tag EPC: {tag.epc} | RSSI: {tag.rssi:.1f} dBm")
        
        reader.stop_inventory()


def example_trigger_based_reading():
    """
    Example 2: Trigger-Based Reading
    
    Read a single tag on demand - perfect for access control,
    checkout systems, etc. The reader starts, waits for ONE tag,
    then stops automatically.
    """
    print("\n" + "=" * 60)
    print("Example 2: Trigger-Based Reading")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("Waiting for a tag (5 second timeout)...")
        
        # This is the key function for trigger-based reading!
        tag = reader.read_single_tag(timeout=5000)
        
        if tag:
            print(f"  Tag detected!")
            print(f"  EPC: {tag.epc}")
            print(f"  RSSI: {tag.rssi:.1f} dBm")
            print(f"  Antenna: {tag.antenna}")
        else:
            print("  No tag detected within timeout")


def example_range_control():
    """
    Example 3: Range Control via Power Settings
    
    Control the reading range by adjusting RF power.
    Lower power = shorter range, Higher power = longer range.
    """
    print("\n" + "=" * 60)
    print("Example 3: Range Control")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        # Get current power
        current_power = reader.get_rf_power()
        print(f"Current RF power: {current_power} dBm")
        
        # Power level guide:
        #   0-10 dBm:  Very short range (< 0.5m)
        #   10-20 dBm: Medium range (0.5-2m)
        #   20-30 dBm: Long range (2-5m+)
        
        print("\nTesting different power levels...")
        
        for power in [10, 20, 30]:
            reader.set_rf_power(power)
            print(f"\n  Power set to {power} dBm")
            
            tag = reader.read_single_tag(timeout=2000)
            if tag:
                print(f"    Tag found at RSSI: {tag.rssi:.1f} dBm")
            else:
                print(f"    No tag found at this power level")
        
        # Restore original power
        reader.set_rf_power(current_power)
        print(f"\nRestored power to {current_power} dBm")


def example_multiple_tags():
    """
    Example 4: Reading Multiple Tags
    
    Read all tags in range. Good for inventory counting.
    """
    print("\n" + "=" * 60)
    print("Example 4: Reading Multiple Tags")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("Reading all tags in range...")
        
        # Read up to 100 tags or until timeout
        tags = reader.read_tags(max_tags=100, timeout=1000, max_timeouts=3)
        
        print(f"\nFound {len(tags)} tag(s):")
        for i, tag in enumerate(tags, 1):
            print(f"  {i}. EPC: {tag.epc}")
        
        # Using iterator (more memory efficient for many tags)
        print("\nUsing iterator approach:")
        reader.start_inventory()
        for i, tag in enumerate(reader.read_tags_iterator(max_count=10), 1):
            print(f"  {i}. {tag.epc}")
        reader.stop_inventory()


def example_continuous_with_callback():
    """
    Example 5: Continuous Reading with Processing
    
    Continuously read tags and process them as they arrive.
    Useful for tracking, monitoring applications.
    """
    print("\n" + "=" * 60)
    print("Example 5: Continuous Reading with Processing")
    print("=" * 60)
    
    # Keep track of unique tags
    seen_tags = set()
    
    def process_tag(tag):
        """Process each tag - your logic goes here"""
        if tag.epc not in seen_tags:
            seen_tags.add(tag.epc)
            print(f"  NEW tag: {tag.epc}")
            # Your logic here: database insert, API call, etc.
            return True
        return False
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("Monitoring for new tags (5 seconds)...")
        print("(Only showing new/unique tags)")
        
        reader.start_inventory()
        
        start_time = time.time()
        new_count = 0
        
        while (time.time() - start_time) < 5:
            tag = reader.get_tag(timeout=500)
            if tag and process_tag(tag):
                new_count += 1
        
        reader.stop_inventory()
        print(f"\nTotal unique tags found: {len(seen_tags)}")


def example_device_configuration():
    """
    Example 6: Device Configuration
    
    Read and modify device settings.
    """
    print("\n" + "=" * 60)
    print("Example 6: Device Configuration")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        # Get device info
        info = reader.get_device_info()
        print("Device Information:")
        print(f"  Firmware: {info['firmware_version']}")
        print(f"  Hardware: {info['hardware_version']}")
        print(f"  Serial:   {info['serial_number']}")
        
        # Get device parameters
        params = reader.get_device_parameters()
        print("\nDevice Parameters:")
        print(f"  RF Power:     {params['rf_power']} dBm")
        print(f"  Region:       {params['region']}")
        print(f"  Q Value:      {params['q_value']}")
        print(f"  Work Mode:    {params['work_mode']}")
        print(f"  Antenna Mask: {params['antenna_mask']:04b}")
        print(f"  Filter Time:  {params['filter_time']}")
        
        # Get frequency info
        freq = reader.get_frequency()
        print("\nFrequency Settings:")
        print(f"  Region:       {freq['region']}")
        print(f"  Start Freq:   {freq['start_freq'] / 100:.2f} MHz")
        print(f"  Stop Freq:    {freq['stop_freq'] / 100:.2f} MHz")
        print(f"  Step:         {freq['step_freq'] / 100:.2f} MHz")
        print(f"  Channels:     {freq['channel_count']}")


def example_tag_memory_operations():
    """
    Example 7: Tag Memory Operations
    
    Read and write tag memory (TID, EPC, USER memory).
    WARNING: Write operations modify the tag permanently!
    """
    print("\n" + "=" * 60)
    print("Example 7: Tag Memory Operations")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("First, reading a tag...")
        tag = reader.read_single_tag(timeout=3000)
        
        if not tag:
            print("No tag found. Please place a tag near the reader.")
            return
        
        print(f"Tag found: {tag.epc}")
        print("\n⚠️  IMPORTANT: Keep the tag in range during memory operations!")
        print("   Some tags may not support memory reading or may require passwords.")
        
        # Read TID (Tag Identifier - unique manufacturer ID, read-only)
        print("\nReading TID memory...")
        try:
            # Try with longer timeout and ensure tag is selected
            tid = reader.read_tag_memory(MemoryBank.TID, 0, 6, epc=tag.epc_bytes, timeout=3000)
            print(f"  ✓ TID: {tid.hex().upper()}")
        except Exception as e:
            print(f"  ✗ Failed to read TID: {e}")
            print("     Note: Some tags may not support TID reading or may be locked.")
        
        # Read EPC memory
        print("\nReading EPC memory...")
        try:
            epc = reader.read_tag_memory(MemoryBank.EPC, 0, 8, epc=tag.epc_bytes, timeout=3000)
            print(f"  ✓ EPC Memory: {epc.hex().upper()}")
        except Exception as e:
            print(f"  ✗ Failed to read EPC: {e}")
            print("     Note: EPC memory may be locked or the tag may not support reading.")
        
        # Read USER memory (if available)
        print("\nReading USER memory...")
        try:
            user = reader.read_tag_memory(MemoryBank.USER, 0, 4, epc=tag.epc_bytes, timeout=3000)
            print(f"  ✓ USER: {user.hex().upper()}")
        except Exception as e:
            print(f"  ✗ Failed to read USER: {e}")
            print("     Note: USER memory may not exist on this tag or may require a password.")
        
        # Writing example (COMMENTED OUT - uncomment to test)
        # WARNING: This will modify the tag!
        """
        print("\nWriting to USER memory...")
        data_to_write = bytes([0x12, 0x34, 0x56, 0x78])
        reader.write_tag_memory(MemoryBank.USER, 0, data_to_write)
        print("  Write successful!")
        """


def example_tag_filtering():
    """
    Example 8: Tag Filtering
    
    Read only tags that match specific criteria.
    """
    print("\n" + "=" * 60)
    print("Example 8: Tag Filtering")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        # First, read all tags
        print("Reading all tags (no filter)...")
        tags = reader.read_tags(max_tags=10, timeout=1000)
        print(f"  Found {len(tags)} tags")
        for tag in tags:
            print(f"    {tag.epc}")
        
        if len(tags) > 0:
            # Set filter to match first tag's EPC prefix (first 4 bytes)
            epc_prefix = tags[0].epc_bytes[:4]
            print(f"\nSetting filter for prefix: {epc_prefix.hex().upper()}")
            reader.filter_by_epc_prefix(epc_prefix)
            
            print("Reading with filter...")
            filtered_tags = reader.read_tags(max_tags=10, timeout=1000)
            print(f"  Found {len(filtered_tags)} matching tags")
            
            # Clear filter
            reader.clear_filter()
            print("\nFilter cleared")


def example_rssi_based_proximity():
    """
    Example 9: RSSI-Based Proximity Detection
    
    Use signal strength (RSSI) to determine tag proximity.
    """
    print("\n" + "=" * 60)
    print("Example 9: RSSI-Based Proximity Detection")
    print("=" * 60)
    
    # RSSI thresholds (adjust based on your setup)
    VERY_CLOSE = -40   # dBm
    CLOSE = -50        # dBm
    MEDIUM = -60       # dBm
    
    def get_proximity(rssi):
        if rssi > VERY_CLOSE:
            return "VERY CLOSE (< 10cm)"
        elif rssi > CLOSE:
            return "CLOSE (10-30cm)"
        elif rssi > MEDIUM:
            return "MEDIUM (30-100cm)"
        else:
            return "FAR (> 100cm)"
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        print("Monitoring tag proximity (5 seconds)...")
        print("Move the tag closer/farther to see changes\n")
        
        reader.start_inventory()
        
        start_time = time.time()
        while (time.time() - start_time) < 5:
            tag = reader.get_tag(timeout=200)
            if tag:
                proximity = get_proximity(tag.rssi)
                # Create a visual bar
                bar_len = int((tag.rssi + 80) / 2)  # Scale to 0-20
                bar = '█' * max(0, bar_len) + '░' * max(0, 20 - bar_len)
                print(f"  {bar} RSSI: {tag.rssi:6.1f} dBm | {proximity}")
        
        reader.stop_inventory()


def example_q_value_optimization():
    """
    Example 10: Q-Value Optimization
    
    The Q value affects how well the reader handles multiple tags.
    Lower Q = faster for few tags, Higher Q = better for many tags.
    """
    print("\n" + "=" * 60)
    print("Example 10: Q-Value Optimization")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        original_q = reader.get_q_value()
        print(f"Current Q value: {original_q}")
        
        print("\nTesting different Q values...")
        print("(Lower Q = faster for few tags, Higher Q = better for many tags)")
        
        for q in [2, 4, 8]:
            reader.set_q_value(q)
            # Small delay to ensure Q value is set
            time.sleep(0.2)
            
            start = time.time()
            tags = reader.read_tags(max_tags=50, timeout=500, max_timeouts=2)
            elapsed = time.time() - start
            
            print(f"\n  Q={q}: Found {len(tags)} tags in {elapsed:.2f}s")
            
            # Small delay between tests
            time.sleep(0.2)
        
        # Restore original
        reader.set_q_value(original_q)
        print(f"\nRestored Q value to {original_q}")


def example_access_control_simulation():
    """
    Example 11: Access Control Simulation
    
    Simulates an access control system where specific tags
    are authorized to access.
    """
    print("\n" + "=" * 60)
    print("Example 11: Access Control Simulation")
    print("=" * 60)
    
    # Authorized tags (in real use, load from database)
    AUTHORIZED_TAGS = {
        'E20034120118000000000001': 'Alice',
        'E20034120118000000000002': 'Bob',
        'E20034120118000000000003': 'Charlie',
    }
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        # Use lower power for close-range access control
        reader.set_rf_power(15)
        
        print("Access Control System Active")
        print("Present your tag (10 seconds)...\n")
        
        start_time = time.time()
        while (time.time() - start_time) < 10:
            tag = reader.read_single_tag(timeout=1000)
            
            if tag:
                epc = tag.epc
                if epc in AUTHORIZED_TAGS:
                    user = AUTHORIZED_TAGS[epc]
                    print(f"  ✓ ACCESS GRANTED: Welcome, {user}!")
                    # In real use: activate relay, open door, etc.
                    # reader.activate_relay(time_100ms=10)
                else:
                    print(f"  ✗ ACCESS DENIED: Unknown tag {epc}")
                
                time.sleep(1)  # Debounce
        
        print("\nAccess control demo complete")


def example_temperature_monitoring():
    """
    Example 12: Temperature Monitoring
    
    Monitor reader temperature (important for industrial use).
    """
    print("\n" + "=" * 60)
    print("Example 12: Temperature Monitoring")
    print("=" * 60)
    
    with CF591Reader('/dev/ttyUSB0') as reader:
        temp = reader.get_temperature()
        print(f"Reader Temperature: {temp['current']}°C")
        print(f"Temperature Limit:  {temp['limit']}°C")
        
        if temp['current'] > temp['limit'] - 10:
            print("\n⚠️ WARNING: Temperature is approaching limit!")


def run_interactive_demo():
    """
    Interactive Demo
    
    Run this for an interactive demonstration.
    """
    print("\n" + "=" * 60)
    print("CHAFON CF591 RFID Reader - Interactive Demo")
    print("=" * 60)
    
    print("""
Available Examples:
  1.  Basic Tag Reading
  2.  Trigger-Based Reading (Single Tag)
  3.  Range Control (Power Settings)
  4.  Multiple Tags
  5.  Continuous Reading with Processing
  6.  Device Configuration
  7.  Tag Memory Operations
  8.  Tag Filtering
  9.  RSSI Proximity Detection
  10. Q-Value Optimization
  11. Access Control Simulation
  12. Temperature Monitoring
  0.  Run All Examples
  q.  Quit
""")
    
    examples = {
        '1': example_basic_reading,
        '2': example_trigger_based_reading,
        '3': example_range_control,
        '4': example_multiple_tags,
        '5': example_continuous_with_callback,
        '6': example_device_configuration,
        '7': example_tag_memory_operations,
        '8': example_tag_filtering,
        '9': example_rssi_based_proximity,
        '10': example_q_value_optimization,
        '11': example_access_control_simulation,
        '12': example_temperature_monitoring,
    }
    
    while True:
        choice = input("\nSelect example (1-12, 0=all, q=quit): ").strip().lower()
        
        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == '0':
            for func in examples.values():
                try:
                    func()
                except Exception as e:
                    print(f"Error: {e}")
                input("\nPress Enter for next example...")
        elif choice in examples:
            try:
                examples[choice]()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Invalid selection")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific example by number
        example_num = sys.argv[1]
        examples = {
            '1': example_basic_reading,
            '2': example_trigger_based_reading,
            '3': example_range_control,
            '4': example_multiple_tags,
            '5': example_continuous_with_callback,
            '6': example_device_configuration,
            '7': example_tag_memory_operations,
            '8': example_tag_filtering,
            '9': example_rssi_based_proximity,
            '10': example_q_value_optimization,
            '11': example_access_control_simulation,
            '12': example_temperature_monitoring,
        }
        if example_num in examples:
            try:
                examples[example_num]()
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print(f"Unknown example: {example_num}")
            sys.exit(1)
    else:
        run_interactive_demo()

