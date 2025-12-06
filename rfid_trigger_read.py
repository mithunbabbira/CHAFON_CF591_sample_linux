#!/usr/bin/env python3
"""
CHAFON CF591 RFID Reader - Trigger-Based Reading

This script implements trigger-based RFID reading:
- Hardcoded RF Output Power: 0-26 dBm
- Press "1" to start reading
- Automatically stops after reading one tag
- Prints tag details
- Press "1" again to read another tag

Usage:
    python3 rfid_trigger_read.py [port] [power]

Arguments:
    port: Serial port (default: /dev/ttyUSB0)
    power: RF power level 0-26 dBm (default: 20)
"""

import sys
import time
from chafon_cf591 import CF591Reader, CF591Error

# ============================================================================
# Configuration
# ============================================================================

# RF Output Power: 0-26 dBm (hardcoded)
DEFAULT_RF_POWER = 1  # Medium range (~5-7 meters)
# Adjust this value based on your needs:
#   0-5:   Very short range (~0.5-2m)
#   6-10:  Short range (~2-3m)
#   11-15: Medium range (~3-5m)
#   16-20: Medium-long range (~5-7m)
#   21-26: Long range (~7-9m)

DEFAULT_PORT = '/dev/ttyUSB0'
DEFAULT_TIMEOUT = 10000  # 10 seconds timeout for reading


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main trigger-based reading loop"""
    
    # Get port and power from command line arguments
    port = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PORT
    try:
        power = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_RF_POWER
        if power < 0 or power > 26:
            print(f"Error: Power must be between 0-26 dBm. Using default: {DEFAULT_RF_POWER}")
            power = DEFAULT_RF_POWER
    except ValueError:
        print(f"Error: Invalid power value. Using default: {DEFAULT_RF_POWER}")
        power = DEFAULT_RF_POWER
    
    print("=" * 60)
    print("CHAFON CF591 RFID Reader - Trigger-Based Reading")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"RF Power: {power} dBm (hardcoded)")
    print(f"Timeout: {DEFAULT_TIMEOUT / 1000:.0f} seconds")
    print()
    print("Instructions:")
    print("  - Press '1' and Enter to start reading")
    print("  - Reading will stop automatically after detecting one tag")
    print("  - Press '1' again to read another tag")
    print("  - Press 'q' and Enter to quit")
    print("=" * 60)
    print()
    
    try:
        # Initialize reader
        reader = CF591Reader(port=port)
        
        # Connect to reader
        print("Connecting to reader...")
        reader.open()
        print("✓ Connected successfully")
        
        # Set RF power (hardcoded)
        print(f"Setting RF power to {power} dBm...")
        reader.set_rf_power(power)
        print(f"✓ RF power set to {power} dBm")
        print()
        
        # Ensure inventory is stopped first (in case it was running from previous session)
        print("Initializing reader state...")
        try:
            reader.stop_inventory()
        except:
            pass  # Ignore errors - might not be running
        
        # Small delay to let reader settle
        time.sleep(0.3)
        
        # Start inventory once and keep it running (more efficient)
        print("Starting inventory (will keep running in background)...")
        inventory_started = False
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                reader.start_inventory()
                inventory_started = True
                print("✓ Inventory started")
                break
            except CF591Error as e:
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries}...", end="", flush=True)
                    time.sleep(0.5)  # Wait before retry
                else:
                    print(f"\n⚠ Warning: Failed to start inventory initially: {e}")
                    print("  Will attempt to start when you press '1' for the first time.")
                    inventory_started = False
        
        print()
        
        # Main loop
        while True:
            # Wait for user input
            user_input = input("Press '1' to read tag (or 'q' to quit): ").strip()
            
            if user_input.lower() == 'q':
                print("\nExiting...")
                break
            
            if user_input != '1':
                print("Invalid input. Please press '1' to read or 'q' to quit.")
                continue
            
            # Ensure inventory is running (in case it failed to start initially)
            if not inventory_started:
                try:
                    print("Starting inventory...", end="", flush=True)
                    reader.start_inventory()
                    inventory_started = True
                    print(" ✓")
                except CF591Error as e:
                    print(f" ✗ Failed: {e}")
                    print("Please try again or check your reader connection.")
                    continue
            
            # Clear any buffered tags first (flush old tags)
            print("\n" + "-" * 60)
            print("Reading RFID tag...")
            print("(Place tag near reader)")
            print("-" * 60)
            
            # Aggressively flush ALL old tags from buffer
            # Keep flushing until we get a timeout (no more tags)
            print("Flushing old tags from buffer...", end="", flush=True)
            flush_count = 0
            flush_start = time.time()
            consecutive_timeouts = 0
            
            while consecutive_timeouts < 3:  # Need 3 consecutive timeouts to be sure
                try:
                    old_tag = reader.get_tag(timeout=100)  # Quick read to clear buffer
                    if old_tag:
                        flush_count += 1
                        consecutive_timeouts = 0  # Reset counter if we got a tag
                    else:
                        consecutive_timeouts += 1
                except CF591Error:
                    # Timeout or error means no more tags
                    consecutive_timeouts += 1
                except:
                    consecutive_timeouts += 1
                
                # Safety timeout - don't flush forever
                if (time.time() - flush_start) > 1.0:  # Max 1 second flushing
                    break
            
            if flush_count > 0:
                print(f" (cleared {flush_count} old tag(s))")
            else:
                print(" (buffer was empty)")
            
            # Small delay after flushing to ensure buffer is truly empty
            # and to give time for any new tag to be detected
            time.sleep(0.2)
            
            # Now read for a NEW tag (not from buffer)
            tag = None
            start_time = time.time()
            timeout_sec = DEFAULT_TIMEOUT / 1000.0
            
            try:
                while (time.time() - start_time) < timeout_sec:
                    tag = reader.get_tag(timeout=500)  # Poll every 500ms
                    if tag:
                        # Got a tag - since we flushed aggressively, this should be fresh
                        break
                    time.sleep(0.01)  # Small delay
                
                if tag:
                    # Print tag details
                    print("\n" + "=" * 60)
                    print("TAG DETECTED!")
                    print("=" * 60)
                    print(f"EPC:        {tag.epc}")
                    print(f"RSSI:       {tag.rssi:.1f} dBm")
                    print(f"Antenna:    {tag.antenna}")
                    print(f"Channel:    {tag.channel}")
                    print(f"Length:     {tag.length} bytes")
                    print(f"CRC:        {tag.crc}")
                    print(f"PC:         {tag.pc}")
                    print(f"Sequence:   {tag.sequence}")
                    print("=" * 60)
                    print()
                    print("✓ Tag read successfully")
                    print()
                else:
                    print("\n✗ No tag detected within timeout")
                    print()
            
            except CF591Error as e:
                print(f"\n✗ Error reading tag: {e}")
                print()
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                print()
        
        # Cleanup
        print("Stopping inventory...")
        try:
            reader.stop_inventory()
        except:
            pass
        print("Closing connection...")
        reader.close()
        print("✓ Disconnected")
        
    except CF591Error as e:
        print(f"\n✗ Connection error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if device is connected: ls /dev/ttyUSB*")
        print("  2. Check permissions: sudo chmod 666 /dev/ttyUSB0")
        print("  3. Verify library is installed: ldconfig -p | grep CFApi")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Closing...")
        try:
            reader.close()
        except:
            pass
        sys.exit(0)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

