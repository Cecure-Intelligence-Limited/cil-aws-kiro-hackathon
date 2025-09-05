#!/usr/bin/env node

/**
 * Test script for the Aura MCP Server
 * Sends test requests to verify the server is working correctly
 */

const { spawn } = require('child_process');
const path = require('path');

async function testMCPServer() {
  console.log('Testing Aura Desktop Assistant MCP Server...\n');
  
  // Determine the correct script to run based on platform
  const isWindows = process.platform === 'win32';
  const scriptPath = isWindows 
    ? path.join(__dirname, 'mcp-server.bat')
    : path.join(__dirname, 'mcp-server.sh');
  
  console.log(`Starting MCP server: ${scriptPath}`);
  
  // Start the MCP server
  const server = spawn(scriptPath, [], {
    stdio: ['pipe', 'pipe', 'inherit'],
    cwd: path.join(__dirname, '..'),
    shell: isWindows
  });
  
  let responses = [];
  let responseCount = 0;
  
  // Collect responses
  server.stdout.on('data', (data) => {
    const lines = data.toString().trim().split('\n');
    for (const line of lines) {
      if (line.trim()) {
        try {
          const response = JSON.parse(line);
          responses.push(response);
          responseCount++;
          console.log(`Response ${responseCount}:`, JSON.stringify(response, null, 2));
        } catch (e) {
          console.log('Non-JSON output:', line);
        }
      }
    }
  });
  
  // Wait for server to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  console.log('\n--- Sending test requests ---\n');
  
  // Test 1: Initialize
  console.log('1. Testing initialize...');
  server.stdin.write(JSON.stringify({
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'test-client', version: '1.0.0' }
    },
    id: 1
  }) + '\n');
  
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Test 2: List tools
  console.log('2. Testing tools/list...');
  server.stdin.write(JSON.stringify({
    method: 'tools/list',
    params: {},
    id: 2
  }) + '\n');
  
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Test 3: Call create_file tool
  console.log('3. Testing tools/call (create_file)...');
  server.stdin.write(JSON.stringify({
    method: 'tools/call',
    params: {
      name: 'create_file',
      arguments: {
        title: 'test-mcp.txt',
        content: 'Hello from MCP server test!'
      }
    },
    id: 3
  }) + '\n');
  
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Test 4: Ping
  console.log('4. Testing ping...');
  server.stdin.write(JSON.stringify({
    method: 'ping',
    params: {},
    id: 4
  }) + '\n');
  
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Close the server
  server.stdin.end();
  server.kill();
  
  console.log(`\n--- Test completed ---`);
  console.log(`Total responses received: ${responseCount}`);
  
  if (responseCount >= 4) {
    console.log('✅ MCP Server test PASSED - All requests received responses');
  } else {
    console.log('❌ MCP Server test FAILED - Missing responses');
  }
  
  return responseCount >= 4;
}

// Run the test
testMCPServer().catch(console.error);