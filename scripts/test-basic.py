#!/usr/bin/env python3
"""
Basic test to see if Python is working
"""

import sys
import json

print("Python is working!", file=sys.stderr)
print("Python version:", sys.version, file=sys.stderr)

# Test basic JSON input/output
try:
    test_response = {
        "id": 1,
        "result": {
            "status": "ok",
            "message": "Python MCP test successful"
        }
    }
    
    print(json.dumps(test_response))
    sys.stdout.flush()
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)