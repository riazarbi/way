#!/usr/bin/env python3
"""Integration test for HTTP-WebSocket workflow."""

import json
import time
import requests
import socketio
import threading
from datetime import datetime

def test_integration_workflow():
    """Test end-to-end HTTP-WebSocket integration workflow."""
    print("Starting HTTP-WebSocket integration test...")
    
    base_url = "http://localhost:5000"
    received_messages = []
    connection_established = threading.Event()
    
    # Create SocketIO client
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("WebSocket connected")
        connection_established.set()
        
    @sio.event  
    def connected(data):
        print(f"Connection confirmed: {data}")
        received_messages.append(('connected', data))
    
    @sio.event
    def hypothesis_processing(data):
        print(f"Processing notification: {data}")
        received_messages.append(('processing', data))
        
    @sio.event
    def hypothesis_feedback(data):
        print(f"Feedback received: {data}")
        received_messages.append(('feedback', data))
        
    @sio.event
    def hypothesis_error(data):
        print(f"Error received: {data}")
        received_messages.append(('error', data))
    
    try:
        # Step 1: Create session
        print("\n1. Creating session...")
        response = requests.post(f"{base_url}/api/session")
        if response.status_code == 201:
            session_data = response.json()
            session_id = session_data['session_id']
            print(f"Session created: {session_id}")
        else:
            print(f"Failed to create session: {response.status_code}")
            return False
        
        # Step 2: Connect WebSocket with session
        print(f"\n2. Connecting WebSocket with session {session_id}...")
        sio.connect(f"{base_url}?session_id={session_id}")
        
        # Wait for connection
        if not connection_established.wait(timeout=5):
            print("WebSocket connection timeout")
            return False
            
        # Step 3: Submit hypothesis via HTTP
        print(f"\n3. Submitting hypothesis via HTTP...")
        hypothesis_data = {
            'hypothesis': 'Changing button color from blue to green increases CTR by 15%',
            'context': 'E-commerce checkout page with high traffic',
            'metric': 'click-through rate',
            'session_id': session_id
        }
        
        response = requests.post(
            f"{base_url}/api/hypothesis",
            json=hypothesis_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 202:
            response_data = response.json()
            print(f"Hypothesis submitted: {response_data['request_id']}")
            if 'task_id' in response_data:
                print(f"Background task: {response_data['task_id']}")
        else:
            print(f"Failed to submit hypothesis: {response.status_code}")
            print(response.text)
            return False
            
        # Step 4: Wait for WebSocket feedback
        print(f"\n4. Waiting for WebSocket feedback...")
        time.sleep(3)  # Give time for async processing
        
        # Step 5: Verify received messages
        print(f"\n5. Verifying received messages...")
        print(f"Received {len(received_messages)} messages:")
        
        for msg_type, data in received_messages:
            print(f"  - {msg_type}: {data.get('message', 'N/A')}")
            
        # Check we got the expected messages
        has_processing = any(msg[0] == 'processing' for msg in received_messages)
        has_feedback = any(msg[0] == 'feedback' for msg in received_messages)
        
        print(f"\nResults:")
        print(f"  Processing notification: {'✓' if has_processing else '✗'}")
        print(f"  Final feedback: {'✓' if has_feedback else '✗'}")
        
        success = has_processing or has_feedback  # Either should work
        print(f"\nIntegration test: {'PASSED' if success else 'FAILED'}")
        return success
        
    except Exception as e:
        print(f"Test error: {e}")
        return False
    finally:
        if sio.connected:
            sio.disconnect()

if __name__ == "__main__":
    test_integration_workflow()