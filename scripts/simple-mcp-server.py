#!/usr/bin/env python3
"""
Simple MCP Server for Aura Desktop Assistant
Python-based alternative that doesn't require Node.js
"""

import json
import sys
import requests
import os
from typing import Dict, Any, Optional

class SimpleMCPServer:
    def __init__(self):
        self.base_url = os.getenv('AURA_API_URL', 'http://localhost:8000')
        self.tools = [
            {
                "name": "create_file",
                "description": "Create a new file with optional content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "open_item",
                "description": "Open a file, application, or folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "type": {"type": "string", "enum": ["file", "application", "folder", "auto"]}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "analyze_sheet",
                "description": "Analyze spreadsheet data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "op": {"type": "string", "enum": ["sum", "avg", "count", "total"]},
                        "column": {"type": "string"}
                    },
                    "required": ["path", "op", "column"]
                }
            },
            {
                "name": "summarize_doc",
                "description": "Summarize PDF documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "length": {"type": "string", "enum": ["short", "bullets", "tweet"]}
                    },
                    "required": ["path"]
                }
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        request_id = request.get('id')
        
        try:
            if method == 'initialize':
                return {
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {
                            "name": "aura-desktop-assistant",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == 'tools/list':
                return {
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            
            elif method == 'tools/call':
                params = request.get('params', {})
                tool_name = params.get('name')
                arguments = params.get('arguments', {})
                
                result = self.call_tool(tool_name, arguments)
                
                return {
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": result
                        }],
                        "isError": "❌" in result
                    }
                }
            
            elif method == 'ping':
                return {"id": request_id, "result": {"status": "ok"}}
            
            else:
                return {
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        endpoint_map = {
            'create_file': '/create_file',
            'open_item': '/open_item',
            'analyze_sheet': '/analyze_sheet',
            'summarize_doc': '/summarize_doc'
        }
        
        endpoint = endpoint_map.get(tool_name)
        if not endpoint:
            return f"❌ Unknown tool: {tool_name}"
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=arguments,
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                if tool_name == 'analyze_sheet':
                    return f"✅ Analysis complete: {data.get('result', 'N/A')} ({data.get('matched_column', 'N/A')} column, {data.get('cells_count', 0)} cells)"
                elif tool_name == 'summarize_doc':
                    return f"✅ Summary generated ({data.get('word_count', 0)} words):\n\n{data.get('summary', 'No summary available')}"
                else:
                    return f"✅ {data.get('message', 'Operation completed successfully')}"
            else:
                return f"❌ HTTP {response.status_code}: {response.text}"
        
        except requests.exceptions.ConnectionError:
            return f"❌ Cannot connect to Aura backend at {self.base_url}. Make sure the server is running."
        except requests.exceptions.Timeout:
            return f"❌ Request timed out. The operation took too long."
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def start(self):
        print("Aura Desktop Assistant MCP Server (Python) starting...", file=sys.stderr)
        print(f"Backend URL: {self.base_url}", file=sys.stderr)
        print("Ready for requests", file=sys.stderr)
        
        try:
            while True:
                try:
                    line = sys.stdin.readline()
                    if not line:  # EOF
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    print(f"Received: {line}", file=sys.stderr)
                    
                    request = json.loads(line)
                    response = self.handle_request(request)
                    
                    response_json = json.dumps(response)
                    print(f"Sending: {response_json}", file=sys.stderr)
                    
                    print(response_json)
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    error_response = json.dumps({
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    })
                    print(f"Parse error, sending: {error_response}", file=sys.stderr)
                    print(error_response)
                    sys.stdout.flush()
                    
                except Exception as e:
                    error_response = json.dumps({
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    })
                    print(f"Internal error, sending: {error_response}", file=sys.stderr)
                    print(error_response)
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            print("MCP Server shutting down...", file=sys.stderr)
        except Exception as e:
            print(f"Fatal error: {str(e)}", file=sys.stderr)

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.start()