#!/usr/bin/env node

/**
 * Build script for Kiro MCP Server
 * Compiles TypeScript and creates a standalone Node.js executable
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const srcDir = path.join(__dirname, '../src');
const distDir = path.join(__dirname, '../dist');
const mcpServerPath = path.join(srcDir, 'services/kiroMCPServer.ts');
const outputPath = path.join(distDir, 'kiro-mcp-server.js');

console.log('Building Kiro MCP Server...');

// Ensure dist directory exists
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Create a standalone MCP server file
const mcpServerContent = `
#!/usr/bin/env node

/**
 * Standalone Kiro MCP Server for Aura Desktop Assistant
 * This file is auto-generated. Do not edit directly.
 */

// Mock the imports that would normally come from the React app
const mockRouterActions = {
  executeIntent: async (intent, onProgress) => {
    // In a real implementation, this would make HTTP calls to the backend
    const baseURL = process.env.AURA_API_URL || 'http://localhost:8000';
    
    const intentMap = {
      'CreateFile': '/create_file',
      'OpenItem': '/open_item', 
      'AnalyzeSpreadsheet': '/analyze_sheet',
      'SummarizeDoc': '/summarize_doc'
    };
    
    const endpoint = intentMap[intent.intent];
    if (!endpoint) {
      throw new Error(\`Unknown intent: \${intent.intent}\`);
    }
    
    onProgress?.({
      phase: 'processing',
      progress: 50,
      message: \`Executing \${intent.intent}...\`
    });
    
    try {
      const response = await fetch(\`\${baseURL}\${endpoint}\`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(intent.parameters)
      });
      
      if (!response.ok) {
        throw new Error(\`HTTP \${response.status}: \${response.statusText}\`);
      }
      
      const data = await response.json();
      
      onProgress?.({
        phase: 'complete',
        progress: 100,
        message: 'Completed successfully'
      });
      
      return {
        success: data.success || true,
        message: data.message || 'Operation completed',
        data: data.data || data
      };
    } catch (error) {
      onProgress?.({
        phase: 'error',
        progress: 0,
        message: \`Error: \${error.message}\`
      });
      
      return {
        success: false,
        message: error.message,
        error: error.message
      };
    }
  }
};

// Kiro Agent implementation (simplified for MCP server)
class KiroAgent {
  constructor() {
    this.tools = new Map([
      ['create_file', {
        name: 'create_file',
        description: 'Create a new file with optional content',
        schema: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            path: { type: 'string' },
            content: { type: 'string' }
          },
          required: ['title']
        }
      }],
      ['open_item', {
        name: 'open_item', 
        description: 'Open a file, application, or folder',
        schema: {
          type: 'object',
          properties: {
            query: { type: 'string' },
            type: { type: 'string', enum: ['file', 'application', 'folder', 'auto'] }
          },
          required: ['query']
        }
      }],
      ['analyze_sheet', {
        name: 'analyze_sheet',
        description: 'Analyze spreadsheet data',
        schema: {
          type: 'object',
          properties: {
            path: { type: 'string' },
            op: { type: 'string', enum: ['sum', 'avg', 'count', 'total'] },
            column: { type: 'string' }
          },
          required: ['path', 'op', 'column']
        }
      }],
      ['summarize_doc', {
        name: 'summarize_doc',
        description: 'Summarize PDF documents',
        schema: {
          type: 'object',
          properties: {
            path: { type: 'string' },
            length: { type: 'string', enum: ['short', 'bullets', 'tweet'] }
          },
          required: ['path']
        }
      }]
    ]);
  }
  
  getAvailableTools() {
    return Array.from(this.tools.values());
  }
  
  async executeTool(toolName, parameters, onProgress) {
    const intentMap = {
      'create_file': 'CreateFile',
      'open_item': 'OpenItem', 
      'analyze_sheet': 'AnalyzeSpreadsheet',
      'summarize_doc': 'SummarizeDoc'
    };
    
    const intent = {
      intent: intentMap[toolName],
      confidence: 0.9,
      parameters,
      context: {
        sessionId: 'mcp-server',
        timestamp: new Date().toISOString(),
        userInput: \`\${toolName} execution\`
      }
    };
    
    return mockRouterActions.executeIntent(intent, onProgress);
  }
}

// MCP Server implementation
class KiroMCPServer {
  constructor() {
    this.kiroAgent = new KiroAgent();
    this.tools = this.kiroAgent.getAvailableTools().map(tool => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.schema
    }));
  }
  
  async handleRequest(request) {
    try {
      switch (request.method) {
        case 'initialize':
          return {
            id: request.id,
            result: {
              protocolVersion: "2024-11-05",
              capabilities: { tools: { listChanged: false } },
              serverInfo: {
                name: "aura-desktop-assistant",
                version: "1.0.0"
              }
            }
          };
          
        case 'tools/list':
          return {
            id: request.id,
            result: { tools: this.tools }
          };
          
        case 'tools/call':
          const { name, arguments: args } = request.params || {};
          const response = await this.kiroAgent.executeTool(name, args || {});
          
          return {
            id: request.id,
            result: {
              content: [{
                type: "text",
                text: response.success 
                  ? \`✅ \${response.message}\${response.data ? '\\n\\nData: ' + JSON.stringify(response.data, null, 2) : ''}\`
                  : \`❌ \${response.error || response.message}\`
              }],
              isError: !response.success
            }
          };
          
        default:
          return {
            id: request.id,
            error: { code: -32601, message: \`Method not found: \${request.method}\` }
          };
      }
    } catch (error) {
      return {
        id: request.id,
        error: { code: -32603, message: error.message }
      };
    }
  }
  
  start() {
    process.stdin.on('data', async (data) => {
      try {
        const lines = data.toString().trim().split('\\n');
        for (const line of lines) {
          if (!line.trim()) continue;
          const request = JSON.parse(line);
          const response = await this.handleRequest(request);
          console.log(JSON.stringify(response));
        }
      } catch (error) {
        console.error(JSON.stringify({
          error: { code: -32700, message: 'Parse error' }
        }));
      }
    });
    process.stdin.resume();
  }
}

// Start the server
const server = new KiroMCPServer();
server.start();
`;

// Write the standalone server file
fs.writeFileSync(outputPath, mcpServerContent);

// Make it executable
try {
  execSync(`chmod +x "${outputPath}"`);
} catch (error) {
  console.warn('Could not make file executable:', error.message);
}

console.log(`✅ MCP Server built successfully: ${outputPath}`);
console.log('');
console.log('To use with Kiro IDE:');
console.log('1. Add the server to your .kiro/settings/mcp.json');
console.log('2. Start your Aura backend server (npm run tauri:dev)');
console.log('3. The MCP server will be available for Kiro to use');