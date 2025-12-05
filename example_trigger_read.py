#!/usr/bin/env python3
"""
Example: Trigger-based RFID tag reading with CHAFON CF591
This example demonstrates:
1. Reading tags based on trigger (manual trigger in this case)
2. Stopping reading as soon as a tag is read
3. Setting reading range (power level)
4. Configuring trigger mode

For Raspberry Pi 5 with CHAFON CF591 RFID Reader
"""

import time
import sys
from chafon_cf591 import CHAFONCF591, CHAFONCF591Error


def read_single_tag_triggered(reader: CHAFONCF591, power_level: int = 20, timeout_ms: int = 5000):
    """
    Read a single tag when triggered.
    Stops reading immediately after reading one tag.
    
    Args:
        reader: CHAFON CF591 reader instance
        power_level: RF power level (0-30, controls reading range)
        timeout_ms: Maximum time to wait for a tag
    
    Returns:
        Tag information dictionary or None
    """
    try:
        # Set reading range (power level)
        # Higher power = longer reading range
        print(f"Setting RF power to {power_level} (range control)...")
        reader.set_rf_power(power_level)
        
        # Configure device for trigger mode
        # WORKMODE: 0 = Answer mode (requires trigger), 1 = Active mode (continuous)
        # TRIGGLETIME: Time in seconds for trigger to be valid
        print("Configuring trigger mode...")
        reader.set_device_parameters(
            work_mode=0,  # Answer mode - requires trigger
            trigger_time=5,  # Trigger valid for 5 seconds
        )
        
        # Start inventory
        print("Starting inventory (waiting for trigger)...")
        reader.start_inventory()
        
        # Try to read a tag with timeout
        start_time = time.time()
        tag = None
        
        while (time.time() - start_time) * 1000 < timeout_ms:
            tag = reader.get_tag(timeout_ms=500)  # Check every 500ms
            if tag is not None:
                print(f"Tag read! Stopping inventory...")
                break
            time.sleep(0.1)  # Small delay to prevent CPU spinning
        
        # Stop inventory immediately after reading tag
        reader.stop_inventory()
        
        return tag
        
    except CHAFONCF591Error as e:
        print(f"Error: {e}")
        try:
            reader.stop_inventory()
        except:
            pass
        return None


def read_tags_continuous_until_trigger(reader: CHAFONCF591, power_level: int = 20):
    """
    Continuously read tags until a trigger signal (or manual stop).
    In this example, we simulate trigger by reading until user presses Enter.
    
    Args:
        reader: CHAFON CF591 reader instance
        power_level: RF power level (0-30)
    """
    try:
        # Set reading range
        print(f"Setting RF power to {power_level}...")
        reader.set_rf_power(power_level)
        
        # Configure for continuous reading with trigger
        reader.set_device_parameters(
            work_mode=0,  # Answer mode
            trigger_time=10,  # Trigger valid for 10 seconds
        )
        
        print("Starting continuous reading (Press Ctrl+C to stop)...")
        reader.start_inventory()
        
        tag_count = 0
        tags_seen = set()
        
        # Read tags until user stops
        print("Reading tags...")
        
        try:
            while True:
                # Try to read a tag
                tag = reader.get_tag(timeout_ms=100)
                if tag is not None:
                    epc = tag['epc']
                    if epc not in tags_seen:
                        tags_seen.add(epc)
                        tag_count += 1
                        print(f"\nTag #{tag_count}:")
                        print(f"  EPC: {epc}")
                        print(f"  RSSI: {tag['rssi']:.1f} dBm")
                        print(f"  Antenna: {tag['antenna']}")
                        print(f"  Channel: {tag['channel']}")
                        sys.stdout.flush()
                
                time.sleep(0.05)  # Small delay
                
        except KeyboardInterrupt:
            pass
        
        reader.stop_inventory()
        print(f"\nStopped. Total unique tags read: {tag_count}")
        
    except CHAFONCF591Error as e:
        print(f"Error: {e}")
        try:
            reader.stop_inventory()
        except:
            pass
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        try:
            reader.stop_inventory()
        except:
            pass


def main():
    """Main example function"""
    # Configuration
    SERIAL_PORT = '/dev/ttyUSB0'  # Change to your serial port
    BAUD_RATE = 115200
    POWER_LEVEL = 20  # Adjust based on desired range (0-30)
    
    print("CHAFON CF591 RFID Reader - Trigger-based Reading Example")
    print("=" * 60)
    
    # Create reader instance
    reader = CHAFONCF591()
    
    try:
        # Connect to reader
        print(f"\nConnecting to reader on {SERIAL_PORT}...")
        reader.open_device(SERIAL_PORT, BAUD_RATE)
        print("Connected successfully!")
        
        # Get device info
        info = reader.get_info()
        print(f"\nDevice Information:")
        print(f"  Firmware: {info['firmware_version']}")
        print(f"  Hardware: {info['hardware_version']}")
        print(f"  Serial: {info['serial_number']}")
        
        # Get current parameters
        params = reader.get_device_parameters()
        print(f"\nCurrent Parameters:")
        print(f"  Work Mode: {params['work_mode']} (0=Answer/Trigger, 1=Active)")
        print(f"  RF Power: {params['rf_power']}")
        print(f"  Trigger Time: {params['trigger_time']} seconds")
        
        # Example 1: Read single tag with trigger
        print("\n" + "=" * 60)
        print("Example 1: Read single tag (stops after first tag)")
        print("=" * 60)
        print("Place a tag near the reader and trigger...")
        time.sleep(2)
        
        tag = read_single_tag_triggered(reader, power_level=POWER_LEVEL, timeout_ms=5000)
        if tag:
            print(f"\n✓ Tag Read Successfully:")
            print(f"  EPC: {tag['epc']}")
            print(f"  RSSI: {tag['rssi']:.1f} dBm")
            print(f"  Antenna: {tag['antenna']}")
            print(f"  Channel: {tag['channel']}")
        else:
            print("\n✗ No tag read within timeout")
        
        # Example 2: Continuous reading until trigger
        print("\n" + "=" * 60)
        print("Example 2: Continuous reading (Press Enter to stop)")
        print("=" * 60)
        response = input("Start continuous reading? (y/n): ")
        if response.lower() == 'y':
            read_tags_continuous_until_trigger(reader, power_level=POWER_LEVEL)
        
        # Example 3: Adjust reading range
        print("\n" + "=" * 60)
        print("Example 3: Adjust reading range (power level)")
        print("=" * 60)
        print("Current power level:", reader.get_rf_power())
        
        new_power = input("Enter new power level (0-30, or press Enter to skip): ")
        if new_power.strip():
            try:
                power = int(new_power)
                if 0 <= power <= 30:
                    reader.set_rf_power(power)
                    print(f"Power level set to {power}")
                else:
                    print("Invalid power level (must be 0-30)")
            except ValueError:
                print("Invalid input")
        
    except CHAFONCF591Error as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        # Close connection
        print("\nClosing connection...")
        reader.close()
        print("Done.")


if __name__ == '__main__':
    main()

