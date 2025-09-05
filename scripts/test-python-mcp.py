#!/usr/bin/env python3
"""
Test script for the Python MCP Server
"""

import subprocess
import json
import time
import sys
import os

def test_mcp_server():
    print("Testing Python MCP Server...")
    
    # Start the MCP server
    server_path = os.path.join(os.path.dirname(__file__), 'simple-mcp-server.py')
    
    try:
        process = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        print("Server started, waiting for initialization...")
        time.sleep(1)
        
        # Test 1: Initialize
        print("\n1. Testing initialize...")
        init_request = {
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            },
            "id": 1
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"Initialize response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {response_line}")
        else:
            print("No response received")
        
        # Test 2: List tools
        print("\n2. Testing tools/list...")
        list_request = {
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        process.stdin.write(json.dumps(list_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"Tools list response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {response_line}")
        else:
            print("No response received")
        
        # Test 3: Ping
        print("\n3. Testing ping...")
        ping_request = {
            "method": "ping",
            "params": {},
            "id": 3
        }
        
        process.stdin.write(json.dumps(ping_request) + '\n')
        process.stdin.flush()
        
        response_line = process.stdout.readline()
        if response_line:
            try:
                response = json.loads(response_line.strip())
                print(f"Ping response: {json.dumps(response, indent=2)}")
            except json.JSONDecodeError:
                print(f"Invalid JSON response: {response_line}")
        else:
            print("No response received")
        
        # Clean up
        process.stdin.close()
        process.terminate()
        
        # Check for any stderr output
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"\nServer stderr output:\n{stderr_output}")
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    test_mcp_server()