#!/usr/bin/env python3
"""
RFID Trigger-Based Reader for CHAFON CF591 on Raspberry Pi 5

This module provides a simple interface for trigger-based RFID reading:
- Start reading on demand (trigger)
- Stop as soon as first tag is detected
- Configurable reading range
- Easy integration with existing Python applications

Usage Example:
    from rfid_trigger_reader import RFIDTriggerReader
    
    with RFIDTriggerReader() as reader:
        reader.set_reading_range(3)  # 3 meters
        tag = reader.read_once()
        if tag:
            print(f"Tag: {tag}")

Author: Generated for CHAFON CF591 Integration
Date: 2024
"""

import os
import sys
import time
from typing import Optional, Dict, List, Callable

# Add parent directory to path to import chafon module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'geu'))

try:
    from chafon_cf591 import CHAFONCF591, CHAFONCF591Error
except ImportError:
    print("Error: Could not import chafon_cf591 module")
    print("Make sure geu/chafon_cf591.py exists")
    sys.exit(1)


class RFIDTriggerReader:
    """
    Simple trigger-based RFID reader wrapper for CHAFON CF591
    
    This class provides:
    - Trigger-based reading (start/stop on demand)
    - Automatic stop on first tag detection
    - Range control (1-10 meters)
    - Easy integration with existing code
    """
    
    # Power level mapping for distance (meters -> power)
    POWER_MAP = {
        1: 5,   # ~1 meter
        2: 8,   # ~2 meters
        3: 12,  # ~3 meters
        4: 16,  # ~4 meters
        5: 20,  # ~5 meters
        6: 23,  # ~6 meters
        7: 26,  # ~7 meters
        8: 28,  # ~8 meters
        9: 30,  # ~9 meters
        10: 30  # ~10 meters
    }
    
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 115200):
        """
        Initialize RFID reader
        
        Args:
            port: Serial port device (e.g., '/dev/ttyUSB0')
            baudrate: Communication baud rate (default: 115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.reader = CHAFONCF591()
        self.connected = False
        self.current_power = 15
        self.tag_callback = None
    
    def connect(self) -> bool:
        """
        Connect to RFID reader
        
        Returns:
            True if connection successful
            
        Raises:
            CHAFONCF591Error: If connection fails
        """
        if self.connected:
            return True
        
        try:
            self.reader.open_device(self.port, self.baudrate)
            self.connected = True
            
            # Get device info
            info = self.reader.get_info()
            print(f"Connected to CHAFON CF591")
            print(f"  Firmware: {info['firmware_version']}")
            print(f"  Hardware: {info['hardware_version']}")
            print(f"  Serial: {info['serial_number']}")
            
            # Set default power
            self.reader.set_rf_power(self.current_power)
            
            return True
            
        except CHAFONCF591Error as e:
            print(f"Failed to connect: {e}")
            raise
    
    def disconnect(self) -> None:
        """Disconnect from RFID reader"""
        if self.connected:
            try:
                self.reader.close()
            except Exception as e:
                print(f"Error during disconnect: {e}")
            finally:
                self.connected = False
    
    def set_reading_range(self, distance_meters: int) -> None:
        """
        Set the reading range in meters
        
        Args:
            distance_meters: Target reading distance (1-10 meters)
            
        Note:
            Actual range depends on tag type, antenna, and environment
        """
        if distance_meters < 1:
            distance_meters = 1
        elif distance_meters > 10:
            distance_meters = 10
        
        power = self.POWER_MAP.get(distance_meters, 15)
        self.current_power = power
        
        if self.connected:
            self.reader.set_rf_power(power)
        
        print(f"Reading range set to ~{distance_meters} meters (power: {power})")
    
    def set_power(self, power: int) -> None:
        """
        Set RF power directly
        
        Args:
            power: RF power level (0-30)
        """
        if power < 0:
            power = 0
        elif power > 30:
            power = 30
        
        self.current_power = power
        
        if self.connected:
            self.reader.set_rf_power(power)
        
        print(f"RF power set to {power}")
    
    def read_once(self, timeout: int = 10, verbose: bool = True) -> Optional[Dict]:
        """
        Trigger reading and return first tag detected, then stop
        
        This is the main method for trigger-based reading.
        It starts inventory, waits for the first tag, then stops immediately.
        
        Args:
            timeout: Maximum time to wait for tag (seconds)
            verbose: Print status messages
            
        Returns:
            Dictionary with tag information or None if no tag detected
            
        Example:
            tag = reader.read_once(timeout=5)
            if tag:
                print(f"EPC: {tag['epc']}")
                print(f"RSSI: {tag['rssi']} dBm")
        """
        if not self.connected:
            self.connect()
        
        try:
            if verbose:
                print(f"Waiting for tag (timeout: {timeout}s)...")
            
            # Start inventory
            self.reader.start_inventory()
            
            # Wait for first tag
            tag = None
            start_time = time.time()
            
            while tag is None:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    if verbose:
                        print("Timeout: No tag detected")
                    break
                
                # Try to read tag
                tag = self.reader.get_tag(timeout_ms=1000)
                
                # Call callback if set
                if tag and self.tag_callback:
                    self.tag_callback(tag)
            
            # Stop inventory immediately
            self.reader.stop_inventory()
            
            if tag and verbose:
                print(f"✓ Tag detected in {elapsed:.1f}s")
                print(f"  EPC: {tag['epc']}")
                print(f"  RSSI: {tag['rssi']:.1f} dBm")
                print(f"  Antenna: {tag['antenna']}")
            
            return tag
            
        except CHAFONCF591Error as e:
            print(f"Error reading tag: {e}")
            try:
                self.reader.stop_inventory()
            except:
                pass
            return None
    
    def read_multiple(self, 
                     duration: int = 5, 
                     max_tags: Optional[int] = None,
                     unique_only: bool = True,
                     verbose: bool = True) -> List[Dict]:
        """
        Read multiple tags for a specified duration
        
        Args:
            duration: How long to read (seconds)
            max_tags: Maximum number of unique tags to read (None = unlimited)
            unique_only: Return only unique tags (based on EPC)
            verbose: Print progress
            
        Returns:
            List of tag dictionaries
        """
        if not self.connected:
            self.connect()
        
        try:
            if verbose:
                print(f"Reading tags for {duration} seconds...")
            
            # Start inventory
            self.reader.start_inventory()
            
            tags = []
            seen_epcs = set()
            start_time = time.time()
            
            while True:
                # Check duration
                elapsed = time.time() - start_time
                if elapsed > duration:
                    break
                
                # Check max tags
                if max_tags and len(tags) >= max_tags:
                    break
                
                # Read tag
                tag = self.reader.get_tag(timeout_ms=500)
                
                if tag:
                    epc = tag['epc']
                    
                    # Check if unique
                    if unique_only:
                        if epc not in seen_epcs:
                            seen_epcs.add(epc)
                            tags.append(tag)
                            if verbose:
                                print(f"  Tag {len(tags)}: {epc} ({tag['rssi']:.1f} dBm)")
                            
                            # Call callback
                            if self.tag_callback:
                                self.tag_callback(tag)
                    else:
                        tags.append(tag)
                        if verbose:
                            print(f"  Read: {epc} ({tag['rssi']:.1f} dBm)")
            
            # Stop inventory
            self.reader.stop_inventory()
            
            if verbose:
                print(f"✓ Found {len(tags)} tag(s) in {elapsed:.1f}s")
            
            return tags
            
        except CHAFONCF591Error as e:
            print(f"Error reading tags: {e}")
            try:
                self.reader.stop_inventory()
            except:
                pass
            return []
    
    def read_until_condition(self,
                            condition: Callable[[Dict], bool],
                            timeout: int = 30,
                            verbose: bool = True) -> Optional[Dict]:
        """
        Read tags until a specific condition is met
        
        Args:
            condition: Function that takes tag dict and returns True to stop
            timeout: Maximum time to wait (seconds)
            verbose: Print status
            
        Returns:
            Tag that matched condition or None
            
        Example:
            # Read until finding a tag with specific EPC prefix
            tag = reader.read_until_condition(
                lambda t: t['epc'].startswith('E200'),
                timeout=10
            )
        """
        if not self.connected:
            self.connect()
        
        try:
            if verbose:
                print(f"Reading until condition met (timeout: {timeout}s)...")
            
            # Start inventory
            self.reader.start_inventory()
            
            start_time = time.time()
            
            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    if verbose:
                        print("Timeout reached")
                    break
                
                # Read tag
                tag = self.reader.get_tag(timeout_ms=1000)
                
                if tag:
                    # Check condition
                    if condition(tag):
                        if verbose:
                            print(f"✓ Condition met: {tag['epc']}")
                        self.reader.stop_inventory()
                        return tag
                    elif verbose:
                        print(f"  Tag {tag['epc']} doesn't meet condition")
            
            # Stop inventory
            self.reader.stop_inventory()
            return None
            
        except CHAFONCF591Error as e:
            print(f"Error: {e}")
            try:
                self.reader.stop_inventory()
            except:
                pass
            return None
    
    def read_strongest_tag(self, duration: int = 3, verbose: bool = True) -> Optional[Dict]:
        """
        Read for specified duration and return tag with strongest signal
        
        Args:
            duration: How long to scan (seconds)
            verbose: Print progress
            
        Returns:
            Tag with highest RSSI or None
        """
        tags = self.read_multiple(duration=duration, unique_only=False, verbose=verbose)
        
        if not tags:
            return None
        
        # Find strongest signal
        strongest = max(tags, key=lambda t: t['rssi'])
        
        if verbose:
            print(f"Strongest tag: {strongest['epc']} ({strongest['rssi']:.1f} dBm)")
        
        return strongest
    
    def set_tag_callback(self, callback: Callable[[Dict], None]) -> None:
        """
        Set callback function to be called when tag is detected
        
        Args:
            callback: Function that takes tag dict as argument
            
        Example:
            def on_tag(tag):
                print(f"Tag detected: {tag['epc']}")
                # Send to server, log, etc.
            
            reader.set_tag_callback(on_tag)
        """
        self.tag_callback = callback
    
    def get_device_info(self) -> Dict:
        """Get device information"""
        if not self.connected:
            self.connect()
        return self.reader.get_info()
    
    def get_device_parameters(self) -> Dict:
        """Get all device parameters"""
        if not self.connected:
            self.connect()
        return self.reader.get_device_parameters()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def __del__(self):
        """Destructor"""
        self.disconnect()


# Convenience functions for quick usage

def read_tag(port: str = '/dev/ttyUSB0', 
             distance: int = 5, 
             timeout: int = 10) -> Optional[str]:
    """
    Quick function to read a single tag
    
    Args:
        port: Serial port
        distance: Reading range in meters
        timeout: Timeout in seconds
        
    Returns:
        Tag EPC as string or None
    """
    with RFIDTriggerReader(port=port) as reader:
        reader.set_reading_range(distance)
        tag = reader.read_once(timeout=timeout)
        return tag['epc'] if tag else None


def read_tags(port: str = '/dev/ttyUSB0',
              distance: int = 5,
              duration: int = 5) -> List[str]:
    """
    Quick function to read multiple tags
    
    Args:
        port: Serial port
        distance: Reading range in meters
        duration: How long to read (seconds)
        
    Returns:
        List of tag EPCs
    """
    with RFIDTriggerReader(port=port) as reader:
        reader.set_reading_range(distance)
        tags = reader.read_multiple(duration=duration)
        return [tag['epc'] for tag in tags]


# Example usage and testing
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='CHAFON CF591 Trigger-Based RFID Reader')
    parser.add_argument('--port', default='/dev/ttyUSB0', help='Serial port')
    parser.add_argument('--range', type=int, default=5, help='Reading range in meters (1-10)')
    parser.add_argument('--timeout', type=int, default=10, help='Timeout in seconds')
    parser.add_argument('--mode', choices=['single', 'multiple', 'continuous'], 
                       default='single', help='Reading mode')
    parser.add_argument('--duration', type=int, default=5, 
                       help='Duration for multiple/continuous mode (seconds)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CHAFON CF591 Trigger-Based RFID Reader")
    print("=" * 60)
    print()
    
    try:
        if args.mode == 'single':
            # Single tag mode
            print("Mode: Single Tag Read")
            print(f"Port: {args.port}")
            print(f"Range: ~{args.range} meters")
            print(f"Timeout: {args.timeout} seconds")
            print()
            
            with RFIDTriggerReader(port=args.port) as reader:
                reader.set_reading_range(args.range)
                
                print("Place tag near reader...")
                tag = reader.read_once(timeout=args.timeout)
                
                if tag:
                    print()
                    print("=" * 60)
                    print("TAG INFORMATION")
                    print("=" * 60)
                    print(f"EPC:      {tag['epc']}")
                    print(f"RSSI:     {tag['rssi']:.1f} dBm")
                    print(f"Antenna:  {tag['antenna']}")
                    print(f"Channel:  {tag['channel']}")
                    print(f"Sequence: {tag['sequence']}")
                    print("=" * 60)
                else:
                    print("No tag detected within timeout")
        
        elif args.mode == 'multiple':
            # Multiple tags mode
            print("Mode: Multiple Tags Read")
            print(f"Port: {args.port}")
            print(f"Range: ~{args.range} meters")
            print(f"Duration: {args.duration} seconds")
            print()
            
            with RFIDTriggerReader(port=args.port) as reader:
                reader.set_reading_range(args.range)
                
                print("Place tags near reader...")
                tags = reader.read_multiple(duration=args.duration)
                
                print()
                print("=" * 60)
                print(f"FOUND {len(tags)} TAG(S)")
                print("=" * 60)
                for i, tag in enumerate(tags, 1):
                    print(f"{i}. {tag['epc']} ({tag['rssi']:.1f} dBm)")
                print("=" * 60)
        
        elif args.mode == 'continuous':
            # Continuous mode
            print("Mode: Continuous Reading")
            print(f"Port: {args.port}")
            print(f"Range: ~{args.range} meters")
            print("Press Ctrl+C to stop")
            print()
            
            with RFIDTriggerReader(port=args.port) as reader:
                reader.set_reading_range(args.range)
                
                # Set callback for real-time updates
                def on_tag_detected(tag):
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] {tag['epc']} | {tag['rssi']:.1f} dBm | Ant {tag['antenna']}")
                
                reader.set_tag_callback(on_tag_detected)
                
                # Read continuously
                try:
                    while True:
                        reader.read_multiple(duration=args.duration, verbose=False)
                except KeyboardInterrupt:
                    print("\nStopped by user")
    
    except CHAFONCF591Error as e:
        print(f"RFID Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


