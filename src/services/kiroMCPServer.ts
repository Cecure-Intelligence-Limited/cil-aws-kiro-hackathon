/**
 * Kiro MCP Server for Aura Desktop Assistant
 * Provides Model Context Protocol integration for Kiro IDE
 */

import { ActionProgress } from '../types';
import type { MCPTool, MCPRequest, MCPResponse } from '../types';

// For standalone execution, we need to mock the dependencies
let kiroAgent: any;

try {
  // Try to import from the main app
  const kiroModule = require('./kiroAgent');
  kiroAgent = kiroModule.kiroAgent;
} catch (error) {
  // Fallback for standalone execution
  console.error('Running in standalone mode, using mock implementations');
  
  // Mock kiroAgent for standalone execution
  kiroAgent = {
    getAvailableTools: () => [
      {
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
      },
      {
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
      },
      {
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
      },
      {
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
      }
    ],
    
    async executeTool(toolName: string, parameters: any, onProgress?: any) {
      // Mock execution for standalone mode
      const baseURL = process.env.AURA_API_URL || 'http://localhost:8000';
      
      const endpointMap: Record<string, string> = {
        'create_file': '/create_file',
        'open_item': '/open_item',
        'analyze_sheet': '/analyze_sheet',
        'summarize_doc': '/summarize_doc'
      };
      
      const endpoint = endpointMap[toolName];
      if (!endpoint) {
        return {
          success: false,
          error: `Unknown tool: ${toolName}`,
          error_code: 'UNKNOWN_TOOL'
        };
      }
      
      onProgress?.({
        phase: 'processing',
        progress: 50,
        message: `Executing ${toolName}...`
      });
      
      try {
        // Use dynamic import for fetch in Node.js
        const fetch = (await import('node-fetch')).default;
        
        const response = await fetch(`${baseURL}${endpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(parameters)
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          return {
            success: false,
            error: `HTTP ${response.status}: ${errorText}`,
            error_code: 'HTTP_ERROR'
          };
        }
        
        const data = await response.json();
        
        onProgress?.({
          phase: 'complete',
          progress: 100,
          message: 'Completed successfully'
        });
        
        return {
          success: (data as any).success !== false,
          message: (data as any).message || 'Operation completed',
          data: (data as any).data || data,
          tool: toolName
        };
        
      } catch (error: any) {
        onProgress?.({
          phase: 'error',
          progress: 0,
          message: `Error: ${error.message}`
        });
        
        return {
          success: false,
          error: error.message,
          error_code: 'EXECUTION_ERROR',
          tool: toolName
        };
      }
    }
  };
}

// MCP types are imported from ../types

interface KiroResponse {
  success: boolean;
  tool?: string;
  message: string;
  data?: any;
  error?: string;
  error_code?: string;
  execution_time?: number;
  metadata?: any;
  suggestions?: Array<{
    type: 'rephrase' | 'clarify' | 'example' | 'alternative';
    message: string;
    example?: string;
  }>;
}

export class KiroMCPServer {
  private tools: MCPTool[] = [];
  private progressCallbacks: Map<string, (progress: ActionProgress) => void> = new Map();

  constructor() {
    this.initializeTools();
  }

  private initializeTools(): void {
    const availableTools = kiroAgent.getAvailableTools();
    
    this.tools = availableTools.map((tool: any) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.schema
    }));
  }

  /**
   * Handle MCP requests
   */
  async handleRequest(request: MCPRequest): Promise<MCPResponse> {
    try {
      switch (request.method) {
        case 'tools/list':
          return this.handleListTools(request);
        
        case 'tools/call':
          return await this.handleToolCall(request);
        
        case 'initialize':
          return this.handleInitialize(request);
        
        case 'ping':
          return { id: request.id ?? 'unknown', result: { status: 'ok' } };
        
        default:
          return {
            id: request.id ?? 'unknown',
            error: {
              code: -32601,
              message: `Method not found: ${request.method}`
            }
          };
      }
    } catch (error) {
      return {
        id: request.id ?? 'unknown',
        error: {
          code: -32603,
          message: error instanceof Error ? error.message : 'Internal error',
          data: { error: error instanceof Error ? error.stack : error }
        }
      };
    }
  }

  private handleInitialize(request: MCPRequest): MCPResponse {
    return {
      id: request.id ?? 'unknown',
      result: {
        protocolVersion: "2024-11-05",
        capabilities: {
          tools: {
            listChanged: false
          }
        },
        serverInfo: {
          name: "aura-desktop-assistant",
          version: "1.0.0",
          description: "Desktop assistant tools for file operations, spreadsheet analysis, and document processing"
        }
      }
    };
  }

  private handleListTools(request: MCPRequest): MCPResponse {
    return {
      id: request.id ?? 'unknown',
      result: {
        tools: this.tools
      }
    };
  }

  private async handleToolCall(request: MCPRequest): Promise<MCPResponse> {
    const { name, arguments: args } = request.params || {};
    
    if (!name) {
      return {
        id: request.id ?? 'unknown',
        error: {
          code: -32602,
          message: 'Missing tool name'
        }
      };
    }

    // Set up progress tracking
    const requestId = String(request.id || Date.now());
    // let lastProgress: ActionProgress | null = null;
    
    this.progressCallbacks.set(requestId, (_progress) => {
      // lastProgress = progress;
      // In a real MCP server, you might send progress notifications here
    });

    try {
      const response = await kiroAgent.executeTool(
        name, 
        args || {}, 
        this.progressCallbacks.get(requestId)
      );

      // Clean up progress callback
      this.progressCallbacks.delete(requestId);

      // Convert KiroResponse to MCP format
      if (response.success) {
        return {
          id: request.id ?? 'unknown',
          result: {
            content: [
              {
                type: "text",
                text: this.formatSuccessResponse(response)
              }
            ],
            isError: false
          }
        };
      } else {
        return {
          id: request.id ?? 'unknown',
          result: {
            content: [
              {
                type: "text",
                text: this.formatErrorResponse(response)
              }
            ],
            isError: true
          }
        };
      }

    } catch (error) {
      this.progressCallbacks.delete(requestId);
      
      return {
        id: request.id ?? 'unknown',
        error: {
          code: -32603,
          message: error instanceof Error ? error.message : 'Tool execution failed',
          data: { tool: name, arguments: args }
        }
      };
    }
  }

  private formatSuccessResponse(response: KiroResponse): string {
    let output = `✅ **${response.tool}** completed successfully\n\n`;
    output += `**Message:** ${response.message}\n\n`;
    
    if (response.data) {
      output += `**Results:**\n`;
      
      // Format different types of data
      if (response.tool === 'analyze_sheet') {
        const data = response.data;
        output += `- Operation: ${data.operation}\n`;
        output += `- Column: ${data.matchedColumn}\n`;
        output += `- Result: ${data.result}\n`;
        output += `- Cells processed: ${data.cellsCount}\n`;
      } else if (response.tool === 'summarize_doc') {
        const data = response.data;
        output += `- Summary type: ${data.lengthType}\n`;
        output += `- Word count: ${data.wordCount}\n`;
        output += `\n**Summary:**\n${data.summary}\n`;
      } else if (response.tool === 'create_file') {
        output += `- File path: ${response.data.file_path || 'N/A'}\n`;
        output += `- Size: ${response.data.size || 0} bytes\n`;
      } else if (response.tool === 'open_item') {
        output += `- Path: ${response.data.path || 'N/A'}\n`;
        output += `- Type: ${response.data.type || 'unknown'}\n`;
        output += `- Method: ${response.data.method || 'system'}\n`;
      } else {
        output += `\`\`\`json\n${JSON.stringify(response.data, null, 2)}\n\`\`\`\n`;
      }
    }
    
    if (response.execution_time) {
      output += `\n*Execution time: ${response.execution_time}ms*`;
    }
    
    return output;
  }

  private formatErrorResponse(response: KiroResponse): string {
    let output = `❌ **${response.tool || 'Tool'}** failed\n\n`;
    output += `**Error:** ${response.error}\n`;
    
    if (response.error_code) {
      output += `**Error Code:** ${response.error_code}\n`;
    }
    
    if (response.suggestions && response.suggestions.length > 0) {
      output += `\n**Suggestions:**\n`;
      response.suggestions.forEach((suggestion, index) => {
        output += `${index + 1}. ${suggestion.message}\n`;
        if (suggestion.example) {
          output += `   *Example: ${suggestion.example}*\n`;
        }
      });
    }
    
    if (response.metadata?.alternative_tools && response.metadata.alternative_tools.length > 0) {
      output += `\n**Alternative tools:** ${response.metadata.alternative_tools.join(', ')}\n`;
    }
    
    return output;
  }

  /**
   * Start the MCP server (for standalone usage)
   */
  start(): void {
    console.error('Aura Desktop Assistant MCP Server starting...');
    console.error(`Available tools: ${this.tools.map(t => t.name).join(', ')}`);
    console.error(`Backend URL: ${process.env.AURA_API_URL || 'http://localhost:8000'}`);
    
    // Handle stdin/stdout communication for MCP
    process.stdin.on('data', async (data) => {
      try {
        const lines = data.toString().trim().split('\n');
        
        for (const line of lines) {
          if (!line.trim()) continue;
          
          const request = JSON.parse(line);
          console.error(`Received request: ${request.method}`);
          
          const response = await this.handleRequest(request);
          
          console.log(JSON.stringify(response));
        }
      } catch (error) {
        console.error(`Parse error: ${error instanceof Error ? error.message : error}`);
        console.log(JSON.stringify({
          error: {
            code: -32700,
            message: 'Parse error',
            data: { error: error instanceof Error ? error.message : error }
          }
        }));
      }
    });

    process.stdin.on('end', () => {
      console.error('MCP Server stdin closed');
      process.exit(0);
    });

    process.stdin.resume();
    console.error('MCP Server ready for requests');
  }
}

// Export for standalone server usage
if (require.main === module) {
  const server = new KiroMCPServer();
  server.start();
}

export const mcpServer = new KiroMCPServer();