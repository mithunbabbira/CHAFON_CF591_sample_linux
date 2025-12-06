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

# Optimization constants - Optimized for maximum speed
BUZZER_DURATION = 5  # Buzzer duration (50ms beep)
BUFFER_FLUSH_TIMEOUT = 20  # Fast timeout for buffer flushing (ms)
TAG_POLL_TIMEOUT = 50  # Fast polling for new tags (ms) - balanced for speed
BUFFER_FLUSH_MAX_TIME = 0.05  # Max time to spend flushing (seconds) - very minimal
BUFFER_FLUSH_CONSECUTIVE = 1  # Consecutive timeouts needed - minimal for speed (single timeout = empty)


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


def set_rf_power_safe(reader, power, max_retries=3, initial_delay=0.3):
    """
    Set RF power with retry logic to handle intermittent communication errors.
    
    The device may need time to initialize after connection, or may experience
    temporary communication issues. This function retries with increasing delays.
    """
    for retry in range(max_retries):
        try:
            if retry > 0:
                # Exponential backoff: 0.3s, 0.5s, 0.8s
                delay = initial_delay * (1.5 ** retry)
                time.sleep(delay)
            reader.set_rf_power(power)
            return True
        except CF591Error as e:
            if retry < max_retries - 1:
                print(f"  Retry {retry + 1}/{max_retries}...", end="", flush=True)
                continue
            else:
                # Last retry failed, re-raise the exception
                raise
    return False


def flush_buffer_aggressive(reader):
    """
    Aggressively flush all buffered tags for clean reading - optimized for speed.
    Returns count of flushed tags.
    NOTE: This function is now deprecated - we restart inventory instead for faster performance.
    """
    # Quick single-pass flush
    flush_count = 0
    flush_start = time.time()
    
    # Quick flush - just check a couple times
    for _ in range(3):
        if (time.time() - flush_start) > BUFFER_FLUSH_MAX_TIME:
            break
        try:
            old_tag = reader.get_tag(timeout=BUFFER_FLUSH_TIMEOUT)
            if old_tag:
                flush_count += 1
            else:
                break  # No more tags
        except:
            break
    
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
        
        # Give device time to fully initialize after connection
        # This helps prevent intermittent "Failed to set RF power" errors
        time.sleep(0.2)
        
        # Set RF power with retry logic to handle intermittent communication errors
        print(f"Setting RF power to {power} dBm...", end="", flush=True)
        try:
            set_rf_power_safe(reader, power, max_retries=3, initial_delay=0.3)
            print(" ✓")
        except CF591Error as e:
            print(f" ✗")
            raise
        
        # Verify power was set correctly
        actual_power = reader.get_rf_power()
        if actual_power == power:
            print(f"✓ RF power set to {power} dBm (verified)")
        else:
            print(f"⚠ Warning: Requested {power} dBm, but device reports {actual_power} dBm")
        
        # Optimize for fast single-tag reading
        print("Optimizing for fast reading...", end="", flush=True)
        try:
            # Get current parameters to preserve other settings
            current_params = reader.get_device_parameters()
            
            # Set Q value to 0 for fastest single tag detection
            # Lower Q = faster for few tags, Higher Q = better for many tags
            # Q=0 is optimal for single tag trigger-based reading
            if current_params.get('q_value', 4) != 0:
                reader.set_q_value(0)
            
            # Set session to S0 (0) for fastest tag response
            # S0 = fastest response, best for single tag reads
            if current_params.get('session', 0) != 0:
                reader.set_device_parameters(session=0)
            
            print(" ✓")
        except CF591Error as e:
            print(f" ⚠ (optimization warning: {e})")
        except Exception as e:
            print(f" ⚠ (optimization skipped: {e})")
        
        print()
        
        # Initialize reader state - start inventory and keep it running
        print("Initializing reader state...")
        try:
            reader.stop_inventory()
        except:
            pass
        
        # Start inventory and keep it running continuously (like sample code)
        print("Starting inventory...", end="", flush=True)
        try:
            reader.start_inventory()
            print(" ✓")
            time.sleep(0.05)  # Small delay for inventory to stabilize
        except CF591Error as e:
            print(f" ✗ Failed: {e}")
            print("Please check your reader connection.")
            sys.exit(1)
        
        print("✓ Ready for reading (inventory running continuously)")
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
            
            # Clear any buffered tags quickly (inventory is already running)
            print("\n" + "-" * 60)
            print("Reading RFID tag...")
            print("(Place tag near reader)")
            print("-" * 60)
            
            # Quick buffer clear - read and discard any existing tags
            flush_count = 0
            flush_start = time.time()
            while (time.time() - flush_start) < 0.05:  # Max 50ms for flushing
                try:
                    old_tag = reader.get_tag(timeout=BUFFER_FLUSH_TIMEOUT)
                    if old_tag:
                        flush_count += 1
                    else:
                        break  # No more tags
                except:
                    break
            
            if flush_count > 0:
                print(f"Flushed {flush_count} old tag(s)")
            else:
                print("Ready for new tag")
            
            # Enable buzzer (with retry) - minimal delay
            enable_buzzer_safe(reader, max_retries=1, delay=0.05)  # Minimal retries
            
            # No delay - start reading immediately
            
            # Read for NEW tag (very fast polling - optimized for speed)
            tag = None
            start_time = time.time()
            timeout_sec = DEFAULT_TIMEOUT / 1000.0
            
            try:
                # Ultra-aggressive polling loop - minimal timeout for fastest detection
                while (time.time() - start_time) < timeout_sec:
                    tag = reader.get_tag(timeout=TAG_POLL_TIMEOUT)
                    if tag:
                        # Got a fresh tag - DISABLE BUZZER IMMEDIATELY (fast)
                        try:
                            reader.disable_buzzer()
                        except CF591Error:
                            pass  # Don't retry, just continue
                        break
                    # Continue immediately - no sleep, loop as fast as possible
                
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
