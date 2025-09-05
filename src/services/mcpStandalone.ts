#!/usr/bin/env tsx

/**
 * Standalone MCP Server for Aura Desktop Assistant
 * This version works directly with the TypeScript source files
 */

import { KiroMCPServer } from './kiroMCPServer';

// Start the MCP server
const server = new KiroMCPServer();
server.start();

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error('MCP Server shutting down...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('MCP Server shutting down...');
  process.exit(0);
});