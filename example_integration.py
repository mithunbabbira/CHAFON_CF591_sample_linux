#!/usr/bin/env python3
"""
Example Integration Scripts for CHAFON CF591 RFID Reader

This file demonstrates how to integrate the RFID reader 
into your existing Python application with various use cases.
"""

from rfid_trigger_reader import RFIDTriggerReader, read_tag, read_tags
import time


# ============================================================================
# EXAMPLE 1: Simple Single Tag Reading
# ============================================================================

def example_1_simple_read():
    """
    Simplest example: Read one tag when triggered
    """
    print("Example 1: Simple Single Tag Read")
    print("-" * 60)
    
    # Quick one-liner
    tag_id = read_tag(port='/dev/ttyUSB0', distance=3, timeout=10)
    
    if tag_id:
        print(f"✓ Tag ID: {tag_id}")
        # Your application logic here
        process_tag(tag_id)
    else:
        print("✗ No tag detected")


# ============================================================================
# EXAMPLE 2: Integration with Existing Application Flow
# ============================================================================

def example_2_application_flow():
    """
    Integration with typical application workflow
    """
    print("Example 2: Application Flow Integration")
    print("-" * 60)
    
    # Initialize RFID reader
    reader = RFIDTriggerReader(port='/dev/ttyUSB0')
    
    try:
        # Connect once at application start
        reader.connect()
        reader.set_reading_range(5)  # 5 meters range
        
        # Your application logic
        print("Application started...")
        
        # Trigger Point 1: User action (e.g., button press, web request)
        print("\n[Trigger 1] User scanned badge at entrance")
        tag = reader.read_once(timeout=10, verbose=True)
        if tag:
            user_id = lookup_user(tag['epc'])
            grant_access(user_id)
        
        time.sleep(2)
        
        # Trigger Point 2: Another action
        print("\n[Trigger 2] Item checkout")
        tag = reader.read_once(timeout=5, verbose=True)
        if tag:
            item_id = tag['epc']
            checkout_item(item_id)
        
        time.sleep(2)
        
        # Trigger Point 3: Multiple items
        print("\n[Trigger 3] Bulk inventory check")
        tags = reader.read_multiple(duration=10, verbose=True)
        for tag in tags:
            update_inventory(tag['epc'])
        
    finally:
        # Disconnect at application end
        reader.disconnect()


# ============================================================================
# EXAMPLE 3: Context Manager Pattern (Recommended)
# ============================================================================

def example_3_context_manager():
    """
    Using context manager for automatic connection/disconnection
    """
    print("Example 3: Context Manager Pattern")
    print("-" * 60)
    
    # Automatic connection and cleanup
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        reader.set_reading_range(3)
        
        # Your logic here - connection is automatically managed
        while True:
            print("\nReady to scan. Press Enter to trigger (or 'q' to quit)...")
            user_input = input()
            
            if user_input.lower() == 'q':
                break
            
            # Trigger reading
            tag = reader.read_once(timeout=10)
            
            if tag:
                print(f"Processing tag: {tag['epc']}")
                # Your processing here
            else:
                print("No tag detected. Try again.")
    
    # Reader is automatically disconnected here


# ============================================================================
# EXAMPLE 4: Callback-Based Real-Time Processing
# ============================================================================

def example_4_callback():
    """
    Real-time tag processing using callbacks
    """
    print("Example 4: Callback-Based Processing")
    print("-" * 60)
    
    # Define callback function
    def handle_tag(tag):
        """Called immediately when tag is detected"""
        print(f"\n→ Tag detected: {tag['epc']}")
        print(f"  Signal strength: {tag['rssi']:.1f} dBm")
        print(f"  Distance estimate: {estimate_distance(tag['rssi'])}")
        
        # Process immediately
        send_to_server(tag['epc'])
        update_database(tag['epc'], tag['rssi'])
        log_event(tag)
    
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        reader.set_reading_range(5)
        reader.set_tag_callback(handle_tag)
        
        # Read for 30 seconds with callback
        print("Monitoring for 30 seconds...")
        reader.read_multiple(duration=30, verbose=False)


# ============================================================================
# EXAMPLE 5: Access Control System
# ============================================================================

def example_5_access_control():
    """
    Simulated access control system
    """
    print("Example 5: Access Control System")
    print("-" * 60)
    
    # Authorized tags database
    authorized_tags = {
        'E200341201180000': {'name': 'John Doe', 'access_level': 'admin'},
        'E200341201180001': {'name': 'Jane Smith', 'access_level': 'user'},
        'E200341201180002': {'name': 'Bob Johnson', 'access_level': 'user'},
    }
    
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        # Short range for security (only close tags)
        reader.set_reading_range(1)
        
        print("Access Control System Active")
        print("Present badge to reader...")
        
        while True:
            # Wait for tag
            tag = reader.read_once(timeout=30, verbose=False)
            
            if tag:
                epc = tag['epc']
                print(f"\nBadge scanned: {epc}")
                
                # Check authorization
                if epc in authorized_tags:
                    user = authorized_tags[epc]
                    print(f"✓ Access GRANTED for {user['name']} ({user['access_level']})")
                    # Trigger door unlock, log access, etc.
                    unlock_door(duration=5)
                else:
                    print("✗ Access DENIED - Unknown badge")
                    # Log unauthorized attempt
                    log_security_event(epc)
                
                # Wait before next scan
                time.sleep(2)
                print("\nReady for next badge...")


# ============================================================================
# EXAMPLE 6: Inventory Management
# ============================================================================

def example_6_inventory():
    """
    Inventory management system
    """
    print("Example 6: Inventory Management")
    print("-" * 60)
    
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        reader.set_reading_range(7)  # Longer range for shelf scanning
        
        while True:
            print("\n=== Inventory Menu ===")
            print("1. Check single item")
            print("2. Scan shelf/area")
            print("3. Find specific item")
            print("4. Exit")
            
            choice = input("\nSelect option: ")
            
            if choice == '1':
                # Single item check
                print("\nScan item...")
                tag = reader.read_once(timeout=10)
                if tag:
                    item = lookup_item(tag['epc'])
                    display_item_info(item)
            
            elif choice == '2':
                # Area scan
                print("\nScanning area for 15 seconds...")
                tags = reader.read_multiple(duration=15)
                print(f"\nFound {len(tags)} items:")
                for tag in tags:
                    item = lookup_item(tag['epc'])
                    print(f"  - {item['name']} (SKU: {item['sku']})")
                
                # Generate report
                generate_inventory_report(tags)
            
            elif choice == '3':
                # Find specific item
                target_epc = input("Enter target EPC (or prefix): ")
                print(f"\nSearching for {target_epc}...")
                
                tag = reader.read_until_condition(
                    lambda t: t['epc'].startswith(target_epc),
                    timeout=30
                )
                
                if tag:
                    print(f"✓ Found! Signal: {tag['rssi']:.1f} dBm")
                else:
                    print("✗ Item not found in range")
            
            elif choice == '4':
                break


# ============================================================================
# EXAMPLE 7: Distance-Based Actions
# ============================================================================

def example_7_distance_based():
    """
    Perform different actions based on tag distance (RSSI)
    """
    print("Example 7: Distance-Based Actions")
    print("-" * 60)
    
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        reader.set_reading_range(10)  # Maximum range
        
        print("Monitoring tag proximity...")
        
        while True:
            tag = reader.read_once(timeout=5, verbose=False)
            
            if tag:
                rssi = tag['rssi']
                
                # Determine distance zone
                if rssi > -30:
                    zone = "VERY CLOSE (< 1m)"
                    action = "Unlock"
                elif rssi > -45:
                    zone = "CLOSE (1-3m)"
                    action = "Prepare"
                elif rssi > -60:
                    zone = "MEDIUM (3-6m)"
                    action = "Alert"
                else:
                    zone = "FAR (6-10m)"
                    action = "Detect"
                
                print(f"\nTag: {tag['epc']}")
                print(f"RSSI: {rssi:.1f} dBm")
                print(f"Zone: {zone}")
                print(f"Action: {action}")
                
                # Execute action
                execute_action(action, tag['epc'])
                
                time.sleep(1)


# ============================================================================
# EXAMPLE 8: Batch Processing with Queue
# ============================================================================

def example_8_batch_queue():
    """
    Batch tag processing with queue
    """
    print("Example 8: Batch Processing")
    print("-" * 60)
    
    from queue import Queue
    from threading import Thread
    
    tag_queue = Queue()
    
    def tag_processor():
        """Background thread to process tags"""
        while True:
            tag = tag_queue.get()
            if tag is None:  # Poison pill to stop thread
                break
            
            # Process tag
            print(f"Processing: {tag['epc']}")
            # Your processing logic here
            time.sleep(0.5)  # Simulate processing time
            
            tag_queue.task_done()
    
    # Start processor thread
    processor = Thread(target=tag_processor, daemon=True)
    processor.start()
    
    # Read tags and queue them
    with RFIDTriggerReader(port='/dev/ttyUSB0') as reader:
        reader.set_reading_range(5)
        
        def on_tag(tag):
            tag_queue.put(tag)
        
        reader.set_tag_callback(on_tag)
        
        print("Reading tags for 30 seconds...")
        reader.read_multiple(duration=30, verbose=False)
    
    # Wait for queue to empty
    tag_queue.join()
    
    # Stop processor
    tag_queue.put(None)
    processor.join()
    
    print("Batch processing complete")


# ============================================================================
# EXAMPLE 9: Web API Integration (Flask Example)
# ============================================================================

def example_9_web_api():
    """
    Example Flask web API for RFID operations
    """
    print("Example 9: Web API Integration")
    print("-" * 60)
    
    # Note: Requires Flask: pip install flask
    try:
        from flask import Flask, jsonify, request
    except ImportError:
        print("Flask not installed. Install with: pip install flask")
        return
    
    app = Flask(__name__)
    reader = RFIDTriggerReader(port='/dev/ttyUSB0')
    
    @app.route('/rfid/status', methods=['GET'])
    def status():
        """Check reader status"""
        try:
            if not reader.connected:
                reader.connect()
            info = reader.get_device_info()
            return jsonify({
                'status': 'connected',
                'info': info
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/rfid/read', methods=['POST'])
    def read():
        """Trigger tag reading"""
        try:
            data = request.json or {}
            timeout = data.get('timeout', 10)
            distance = data.get('distance', 5)
            
            if not reader.connected:
                reader.connect()
            
            reader.set_reading_range(distance)
            tag = reader.read_once(timeout=timeout, verbose=False)
            
            if tag:
                return jsonify({
                    'success': True,
                    'tag': tag
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No tag detected'
                })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/rfid/scan', methods=['POST'])
    def scan():
        """Scan for multiple tags"""
        try:
            data = request.json or {}
            duration = data.get('duration', 5)
            distance = data.get('distance', 5)
            
            if not reader.connected:
                reader.connect()
            
            reader.set_reading_range(distance)
            tags = reader.read_multiple(duration=duration, verbose=False)
            
            return jsonify({
                'success': True,
                'count': len(tags),
                'tags': tags
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    print("Starting Flask API server...")
    print("Endpoints:")
    print("  GET  /rfid/status")
    print("  POST /rfid/read")
    print("  POST /rfid/scan")
    app.run(host='0.0.0.0', port=5000)


# ============================================================================
# Helper Functions (Placeholders - Implement Based on Your Needs)
# ============================================================================

def process_tag(tag_id):
    """Process detected tag"""
    print(f"  → Processing tag: {tag_id}")

def lookup_user(epc):
    """Look up user by tag EPC"""
    return f"User_{epc[:8]}"

def grant_access(user_id):
    """Grant access to user"""
    print(f"  → Access granted for {user_id}")

def checkout_item(item_id):
    """Checkout item"""
    print(f"  → Checked out: {item_id}")

def update_inventory(epc):
    """Update inventory database"""
    print(f"  → Updated inventory: {epc}")

def send_to_server(epc):
    """Send tag data to server"""
    pass  # Implement your server communication

def update_database(epc, rssi):
    """Update database"""
    pass  # Implement your database logic

def log_event(tag):
    """Log event"""
    print(f"  → Logged: {tag['epc']} at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def estimate_distance(rssi):
    """Estimate distance from RSSI"""
    if rssi > -30:
        return "< 1m"
    elif rssi > -45:
        return "1-3m"
    elif rssi > -60:
        return "3-6m"
    else:
        return "> 6m"

def unlock_door(duration):
    """Unlock door for specified duration"""
    print(f"  → Door unlocked for {duration} seconds")

def log_security_event(epc):
    """Log security event"""
    print(f"  ⚠ Unauthorized access attempt: {epc}")

def lookup_item(epc):
    """Look up item by EPC"""
    return {
        'epc': epc,
        'name': f"Item_{epc[:8]}",
        'sku': f"SKU_{epc[8:16]}"
    }

def display_item_info(item):
    """Display item information"""
    print(f"  Name: {item['name']}")
    print(f"  SKU: {item['sku']}")

def generate_inventory_report(tags):
    """Generate inventory report"""
    print(f"  → Report generated for {len(tags)} items")

def execute_action(action, epc):
    """Execute action based on distance"""
    print(f"  → Executing: {action}")


# ============================================================================
# Main Menu
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("CHAFON CF591 Integration Examples")
    print("=" * 60)
    print()
    print("Select an example to run:")
    print("1. Simple single tag read")
    print("2. Application flow integration")
    print("3. Context manager pattern")
    print("4. Callback-based processing")
    print("5. Access control system")
    print("6. Inventory management")
    print("7. Distance-based actions")
    print("8. Batch processing with queue")
    print("9. Web API integration (Flask)")
    print()
    
    choice = input("Enter example number (1-9): ")
    print()
    
    examples = {
        '1': example_1_simple_read,
        '2': example_2_application_flow,
        '3': example_3_context_manager,
        '4': example_4_callback,
        '5': example_5_access_control,
        '6': example_6_inventory,
        '7': example_7_distance_based,
        '8': example_8_batch_queue,
        '9': example_9_web_api,
    }
    
    if choice in examples:
        try:
            examples[choice]()
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice")


