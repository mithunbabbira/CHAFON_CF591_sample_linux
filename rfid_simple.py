#!/usr/bin/env python3
"""
CHAFON CF591 RFID Reader - Simple Interface

A simplified interface for common use cases:
- Trigger-based reading (start, read one tag, stop)
- Range control
- Easy integration with existing code

Example:
    from rfid_simple import RFIDScanner
    
    scanner = RFIDScanner()
    
    # Wait for and read a single tag
    tag = scanner.scan()
    if tag:
        print(f"Tag: {tag['epc']}")
"""

from typing import Optional, Dict, List, Callable, Any
import time
import threading
from chafon_cf591 import CF591Reader, Tag, CF591Error


class RFIDScanner:
    """
    Simple RFID Scanner Interface
    
    Designed for easy integration with existing applications.
    Provides trigger-based scanning and range control.
    """
    
    def __init__(self, port: str = '/dev/ttyUSB0', baud_rate: int = 115200):
        """
        Initialize RFID Scanner
        
        Args:
            port: Serial port (default: /dev/ttyUSB0)
            baud_rate: Communication speed (default: 115200)
        """
        self._reader = CF591Reader(port, baud_rate)
        self._connected = False
        self._power = None
    
    def connect(self) -> bool:
        """
        Connect to the RFID reader
        
        Returns:
            True if connected successfully
        """
        if self._connected:
            return True
        
        try:
            self._reader.open()
            self._connected = True
            return True
        except CF591Error as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the reader"""
        if self._connected:
            self._reader.close()
            self._connected = False
    
    def scan(self, timeout_ms: int = 3000) -> Optional[Dict[str, Any]]:
        """
        Scan for a single RFID tag (trigger-based)
        
        This method:
        1. Starts the reader
        2. Waits until a tag is detected OR timeout
        3. Stops the reader
        4. Returns the tag data
        
        Args:
            timeout_ms: Maximum time to wait in milliseconds
            
        Returns:
            Dictionary with tag data if found, None if timeout
            
        Example:
            scanner = RFIDScanner()
            scanner.connect()
            
            tag = scanner.scan(timeout_ms=5000)
            if tag:
                print(f"Found: {tag['epc']}")
                print(f"Signal: {tag['rssi']} dBm")
        """
        if not self._connected:
            if not self.connect():
                return None
        
        try:
            tag = self._reader.read_single_tag(timeout=timeout_ms)
            if tag:
                return tag.to_dict()
            return None
        except CF591Error as e:
            print(f"Scan error: {e}")
            return None
    
    def scan_multiple(self, max_tags: int = 10, timeout_ms: int = 2000) -> List[Dict[str, Any]]:
        """
        Scan for multiple RFID tags
        
        Args:
            max_tags: Maximum number of tags to read
            timeout_ms: Timeout per read attempt
            
        Returns:
            List of tag dictionaries
        """
        if not self._connected:
            if not self.connect():
                return []
        
        try:
            tags = self._reader.read_tags(max_tags=max_tags, timeout=timeout_ms)
            return [tag.to_dict() for tag in tags]
        except CF591Error as e:
            print(f"Scan error: {e}")
            return []
    
    def set_range(self, level: str = 'medium'):
        """
        Set the reading range
        
        Args:
            level: 'short', 'medium', or 'long'
                   short  = < 0.5m  (power: 10 dBm)
                   medium = 0.5-2m  (power: 20 dBm)
                   long   = 2-5m+   (power: 30 dBm)
        """
        if not self._connected:
            if not self.connect():
                return
        
        power_levels = {
            'short': 10,
            'medium': 20,
            'long': 30
        }
        
        power = power_levels.get(level.lower(), 20)
        self._reader.set_rf_power(power)
        self._power = power
    
    def set_power(self, power_dbm: int):
        """
        Set RF power directly
        
        Args:
            power_dbm: Power in dBm (0-30)
        """
        if not self._connected:
            if not self.connect():
                return
        
        self._reader.set_rf_power(power_dbm)
        self._power = power_dbm
    
    def get_power(self) -> int:
        """Get current RF power level"""
        if not self._connected:
            if not self.connect():
                return -1
        
        return self._reader.get_rf_power()
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device information"""
        if not self._connected:
            if not self.connect():
                return {}
        
        return self._reader.get_device_info()
    
    def is_connected(self) -> bool:
        """Check if connected"""
        return self._connected
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False


class RFIDMonitor:
    """
    Continuous RFID Monitor with Callbacks
    
    Monitors for tags and calls your callback function when found.
    Useful for background monitoring applications.
    
    Example:
        def on_tag_found(tag):
            print(f"Tag detected: {tag['epc']}")
            # Your logic here
        
        monitor = RFIDMonitor(on_tag_found)
        monitor.start()
        
        # ... your other code ...
        
        monitor.stop()
    """
    
    def __init__(self, callback: Callable[[Dict], None], 
                 port: str = '/dev/ttyUSB0',
                 debounce_ms: int = 1000):
        """
        Initialize RFID Monitor
        
        Args:
            callback: Function to call when tag is detected
            port: Serial port
            debounce_ms: Minimum time between same tag callbacks
        """
        self._callback = callback
        self._scanner = RFIDScanner(port)
        self._debounce_ms = debounce_ms
        self._running = False
        self._thread = None
        self._last_tags = {}  # EPC -> timestamp
    
    def start(self):
        """Start monitoring in background thread"""
        if self._running:
            return
        
        if not self._scanner.connect():
            raise CF591Error("Failed to connect to reader")
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        self._scanner.disconnect()
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        self._scanner._reader.start_inventory()
        
        try:
            while self._running:
                tag_obj = self._scanner._reader.get_tag(timeout=500)
                
                if tag_obj:
                    tag = tag_obj.to_dict()
                    epc = tag['epc']
                    now = time.time() * 1000
                    
                    # Debounce: don't report same tag too frequently
                    last_time = self._last_tags.get(epc, 0)
                    if (now - last_time) > self._debounce_ms:
                        self._last_tags[epc] = now
                        try:
                            self._callback(tag)
                        except Exception as e:
                            print(f"Callback error: {e}")
        finally:
            try:
                self._scanner._reader.stop_inventory()
            except:
                pass
    
    @property
    def is_running(self) -> bool:
        """Check if monitor is running"""
        return self._running


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_scan(port: str = '/dev/ttyUSB0', timeout_ms: int = 3000) -> Optional[Dict]:
    """
    Quick one-shot scan for a tag
    
    Args:
        port: Serial port
        timeout_ms: Timeout in milliseconds
        
    Returns:
        Tag dictionary or None
        
    Example:
        tag = quick_scan()
        if tag:
            print(f"Found: {tag['epc']}")
    """
    with RFIDScanner(port) as scanner:
        return scanner.scan(timeout_ms)


def wait_for_tag(port: str = '/dev/ttyUSB0', 
                 epc_filter: str = None,
                 timeout_sec: float = None) -> Optional[Dict]:
    """
    Wait indefinitely (or until timeout) for a specific tag
    
    Args:
        port: Serial port
        epc_filter: Optional EPC to match (partial match ok)
        timeout_sec: Optional timeout in seconds (None = wait forever)
        
    Returns:
        Tag dictionary or None
        
    Example:
        # Wait for any tag
        tag = wait_for_tag()
        
        # Wait for specific tag prefix
        tag = wait_for_tag(epc_filter='E200')
    """
    with RFIDScanner(port) as scanner:
        start_time = time.time()
        
        while True:
            tag = scanner.scan(timeout_ms=1000)
            
            if tag:
                if epc_filter is None or epc_filter in tag['epc']:
                    return tag
            
            if timeout_sec and (time.time() - start_time) > timeout_sec:
                return None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("RFID Simple Scanner Demo")
    print("=" * 50)
    
    port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0'
    
    # Example 1: Quick scan
    print("\n1. Quick Scan (waiting 5 seconds for a tag)...")
    tag = quick_scan(port, timeout_ms=5000)
    if tag:
        print(f"   Found tag: {tag['epc']}")
        print(f"   Signal:    {tag['rssi']:.1f} dBm")
    else:
        print("   No tag found")
    
    # Example 2: Using the scanner object
    print("\n2. Using RFIDScanner object...")
    with RFIDScanner(port) as scanner:
        # Set to medium range
        scanner.set_range('medium')
        print(f"   Power: {scanner.get_power()} dBm")
        
        # Read device info
        info = scanner.get_device_info()
        print(f"   Device: {info.get('firmware_version', 'Unknown')}")
        
        # Scan for tags
        print("   Scanning for tags...")
        tags = scanner.scan_multiple(max_tags=5)
        print(f"   Found {len(tags)} tag(s)")
    
    # Example 3: Callback-based monitoring
    print("\n3. Callback-based monitoring (5 seconds)...")
    
    def on_tag(tag):
        print(f"   -> Tag detected: {tag['epc'][:16]}... RSSI: {tag['rssi']:.1f}")
    
    monitor = RFIDMonitor(on_tag, port)
    monitor.start()
    
    time.sleep(5)
    
    monitor.stop()
    print("   Monitoring stopped")
    
    print("\nDemo complete!")

