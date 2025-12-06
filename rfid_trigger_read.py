#!/usr/bin/env python3
"""
CHAFON CF591 RFID Reader - Optimized Trigger-Based Reading

This script implements optimized trigger-based RFID reading:
- Hardcoded RF Output Power: 0-26 dBm
- Press "1" to start reading
- Automatically stops after reading one tag
- Fast reading with no buffer data
- Buzzer control

Usage:
    python3 rfid_trigger_read.py [port] [power]

Arguments:
    port: Serial port (default: /dev/ttyUSB0)
    power: RF power level 0-26 dBm (default: 26, per device specification)
"""

import sys
import time
from datetime import datetime
from chafon_cf591 import CF591Reader, CF591Error

# ============================================================================
# Configuration
# ============================================================================

# RF Output Power: 0-26 dBm (adjustable, per device specification)
DEFAULT_RF_POWER = 26  # Maximum range (~5-7m)
# Adjust this value based on your needs:
#   0-5:   Very short range (~0.5-1m)
#   6-10:  Short range (~1-2m)
#   11-15: Medium range (~2-3m)
#   16-20: Medium-long range (~3-5m)
#   21-26: Long range (~5-7m)

DEFAULT_PORT = '/dev/ttyUSB0'
DEFAULT_TIMEOUT = 10000  # 10 seconds timeout for reading

# Optimization constants - Optimized for speed
BUZZER_DURATION = 5  # Buzzer duration (50ms beep)
BUFFER_FLUSH_TIMEOUT = 20  # Very fast timeout for buffer flushing (ms)
TAG_POLL_TIMEOUT = 50  # Very fast polling for new tags (ms) - reduced for speed
BUFFER_FLUSH_MAX_TIME = 0.15  # Max time to spend flushing (seconds) - minimal
BUFFER_FLUSH_CONSECUTIVE = 2  # Consecutive timeouts needed - minimal for speed


# ============================================================================
# Helper Functions
# ============================================================================

def enable_buzzer_safe(reader, max_retries=3, delay=0.3):
    """Enable buzzer with retry logic and proper delays"""
    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(delay)
            reader.enable_buzzer(duration=BUZZER_DURATION)
            return True
        except CF591Error:
            if retry < max_retries - 1:
                continue
    return False


def disable_buzzer_safe(reader, max_retries=3, delay=0.1):
    """Disable buzzer with retry logic"""
    for retry in range(max_retries):
        try:
            if retry > 0:
                time.sleep(delay)
            reader.disable_buzzer()
            return True
        except CF591Error:
            if retry < max_retries - 1:
                continue
    return False


def flush_buffer_aggressive(reader):
    """
    Aggressively flush all buffered tags for clean reading - optimized for speed.
    Returns count of flushed tags.
    """
    flush_count = 0
    consecutive_timeouts = 0
    flush_start = time.time()
    
    # Stop inventory temporarily for cleaner buffer flush
    try:
        reader.stop_inventory()
        time.sleep(0.01)  # Minimal delay
    except:
        pass
    
    # Flush all buffered tags quickly - minimal iterations for speed
    while consecutive_timeouts < BUFFER_FLUSH_CONSECUTIVE:
        # Check timeout - strict limit
        if (time.time() - flush_start) > BUFFER_FLUSH_MAX_TIME:
            break
        
        try:
            old_tag = reader.get_tag(timeout=BUFFER_FLUSH_TIMEOUT)
            if old_tag:
                flush_count += 1
                consecutive_timeouts = 0
            else:
                consecutive_timeouts += 1
        except CF591Error:
            consecutive_timeouts += 1
        except:
            consecutive_timeouts += 1
    
    # Restart inventory for fresh reading
    try:
        reader.start_inventory()
        time.sleep(0.02)  # Minimal delay for faster restart
    except:
        pass
    
    return flush_count


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
            print(f"Error: Power must be between 0-26 dBm (per device specification). Using default: {DEFAULT_RF_POWER}")
            power = DEFAULT_RF_POWER
    except ValueError:
        print(f"Error: Invalid power value. Using default: {DEFAULT_RF_POWER}")
        power = DEFAULT_RF_POWER
    
    print("=" * 60)
    print("CHAFON CF591 RFID Reader - Optimized Trigger-Based Reading")
    print("=" * 60)
    print(f"Port: {port}")
    print(f"RF Power: {power} dBm")
    print(f"Timeout: {DEFAULT_TIMEOUT / 1000:.0f} seconds")
    print()
    print("Instructions:")
    print("  - Press '1' and Enter to start reading (buzzer enabled)")
    print("  - Reading will stop automatically after detecting one tag")
    print("  - Buzzer will sound when tag is detected")
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
        
        # Set RF power
        print(f"Setting RF power to {power} dBm...")
        reader.set_rf_power(power)
        
        # Verify power was set correctly
        actual_power = reader.get_rf_power()
        if actual_power == power:
            print(f"✓ RF power set to {power} dBm (verified)")
        else:
            print(f"⚠ Warning: Requested {power} dBm, but device reports {actual_power} dBm")
        print()
        
        # Initialize reader state
        print("Initializing reader state...")
        try:
            reader.stop_inventory()
        except:
            pass
        
        time.sleep(0.2)  # Short delay for device to settle
        
        # Start inventory
        print("Starting inventory...")
        inventory_started = False
        for attempt in range(3):
            try:
                reader.start_inventory()
                inventory_started = True
                print("✓ Inventory started")
                time.sleep(0.2)  # Short delay for device to be ready
                break
            except CF591Error as e:
                if attempt < 2:
                    print(f"  Retry {attempt + 1}/3...", end="", flush=True)
                    time.sleep(0.3)
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
            
            # Record timestamp when user presses "1"
            read_start_time = time.time()
            read_start_datetime = datetime.now()
            print(f"\n[Timestamp: {read_start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}] Reading started")
            
            # Ensure inventory is running
            if not inventory_started:
                try:
                    print("Starting inventory...", end="", flush=True)
                    reader.start_inventory()
                    inventory_started = True
                    print(" ✓")
                    time.sleep(0.2)
                except CF591Error as e:
                    print(f" ✗ Failed: {e}")
                    print("Please try again or check your reader connection.")
                    continue
            
            # Clear buffer FIRST (before enabling buzzer) for speed
            print("\n" + "-" * 60)
            print("Reading RFID tag...")
            print("(Place tag near reader)")
            print("-" * 60)
            
            print("Flushing buffer...", end="", flush=True)
            flush_count = flush_buffer_aggressive(reader)
            
            if flush_count > 0:
                print(f" (cleared {flush_count} old tag(s))")
            else:
                print(" (buffer was empty)")
            
            # Enable buzzer (with retry) - after buffer flush
            enable_buzzer_safe(reader, max_retries=2, delay=0.1)  # Reduced retries for speed
            
            # No delay - start reading immediately
            
            # Read for NEW tag (very fast polling - optimized for speed)
            tag = None
            start_time = time.time()
            timeout_sec = DEFAULT_TIMEOUT / 1000.0
            
            try:
                # Aggressive polling loop - no delays
                while (time.time() - start_time) < timeout_sec:
                    tag = reader.get_tag(timeout=TAG_POLL_TIMEOUT)
                    if tag:
                        # Got a fresh tag - DISABLE BUZZER IMMEDIATELY (fast)
                        try:
                            reader.disable_buzzer()
                        except CF591Error:
                            # Single retry if needed
                            try:
                                time.sleep(0.02)
                                reader.disable_buzzer()
                            except CF591Error:
                                pass
                        break
                    # Continue immediately - no sleep
                
                if tag:
                    # Record timestamp when tag is detected
                    tag_detect_time = time.time()
                    tag_detect_datetime = datetime.now()
                    read_duration = (tag_detect_time - read_start_time) * 1000  # Convert to milliseconds
                    
                    # Print tag details with timestamps
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
                    print("-" * 60)
                    print(f"Start Time:  {read_start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"Detect Time: {tag_detect_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"Duration:   {read_duration:.2f} ms")
                    print("=" * 60)
                    print()
                    print("✓ Tag read successfully")
                    print()
                else:
                    # Record timestamp when timeout occurs
                    timeout_time = time.time()
                    timeout_datetime = datetime.now()
                    timeout_duration = (timeout_time - read_start_time) * 1000  # Convert to milliseconds
                    
                    print("\n✗ No tag detected within timeout")
                    print("-" * 60)
                    print(f"Start Time:  {read_start_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"Timeout Time: {timeout_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    print(f"Duration:   {timeout_duration:.2f} ms")
                    print("-" * 60)
                    print()
                    
                    # Disable buzzer if no tag detected
                    disable_buzzer_safe(reader)
            
            except CF591Error as e:
                print(f"\n✗ Error reading tag: {e}")
                print()
                disable_buzzer_safe(reader)
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"\n✗ Unexpected error: {e}")
                print()
                disable_buzzer_safe(reader)
        
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
