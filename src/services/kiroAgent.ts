/**
 * Kiro Agent Integration for Aura Desktop Assistant
 * Provides intelligent tool routing and execution with structured responses
 */

import { routerActions } from './routerActions';
import { ActionProgress } from '../types';
import { ParsedIntent } from '../types';

export interface KiroToolCall {
  tool: string;
  parameters: Record<string, any>;
  confidence?: number;
}

export interface KiroResponse {
  success: boolean;
  tool?: string;
  message: string;
  data?: any;
  error?: string;
  error_code?: string;
  execution_time?: number;
  metadata?: {
    confidence?: number;
    matched_patterns?: string[];
    alternative_tools?: string[];
    attempted_tool?: string;
    error_details?: any;
  };
  suggestions?: Array<{
    type: 'rephrase' | 'clarify' | 'example' | 'alternative';
    message: string;
    example?: string;
  }> | undefined;
}

export interface ToolDefinition {
  name: string;
  description: string;
  schema: any;
  examples: any[];
}

export interface RoutingRule {
  tool: string;
  triggers: string[];
  patterns: string[];
  priority: number;
}

export class KiroAgent {
  private tools: Map<string, ToolDefinition> = new Map();
  private routingRules: RoutingRule[] = [];
  private fallbackTool: string = 'create_file';

  constructor() {
    this.initializeTools();
    this.initializeRouting();
  }

  /**
   * Initialize tool definitions
   */
  private initializeTools(): void {
    const toolDefinitions: ToolDefinition[] = [
      {
        name: 'create_file',
        description: 'Create a new file with optional content in a specified location',
        schema: {
          type: 'object',
          properties: {
            title: { type: 'string', description: 'Name of the file to create' },
            path: { type: 'string', description: 'Optional directory path' },
            content: { type: 'string', description: 'Optional initial content' }
          },
          required: ['title']
        },
        examples: [
          { title: 'notes.txt', content: 'Meeting notes...' },
          { title: 'config.json', path: './settings', content: '{}' }
        ]
      },
      {
        name: 'open_item',
        description: 'Open a file, application, or folder using the system default handler',
        schema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Search query for the item to open' },
            type: { type: 'string', enum: ['file', 'application', 'folder', 'auto'], default: 'auto' }
          },
          required: ['query']
        },
        examples: [
          { query: 'budget.xlsx', type: 'file' },
          { query: 'Visual Studio Code', type: 'application' }
        ]
      },
      {
        name: 'analyze_sheet',
        description: 'Perform mathematical operations on spreadsheet data',
        schema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'Path to spreadsheet file' },
            op: { type: 'string', enum: ['sum', 'avg', 'count', 'total'] },
            column: { type: 'string', description: 'Column name to analyze' }
          },
          required: ['path', 'op', 'column']
        },
        examples: [
          { path: 'data.csv', op: 'sum', column: 'amount' },
          { path: 'sales.xlsx', op: 'avg', column: 'revenue' }
        ]
      },
      {
        name: 'summarize_doc',
        description: 'Extract text from PDF documents and generate summaries',
        schema: {
          type: 'object',
          properties: {
            path: { type: 'string', description: 'Path to PDF document' },
            length: { type: 'string', enum: ['short', 'bullets', 'tweet'], default: 'short' }
          },
          required: ['path']
        },
        examples: [
          { path: 'report.pdf', length: 'bullets' },
          { path: 'paper.pdf', length: 'short' }
        ]
      }
    ];

    toolDefinitions.forEach(tool => {
      this.tools.set(tool.name, tool);
    });
  }

  /**
   * Initialize routing rules
   */
  private initializeRouting(): void {
    this.routingRules = [
      {
        tool: 'analyze_sheet',
        triggers: ['sum', 'total', 'average', 'avg', 'count', 'calculate', 'add up', 'spreadsheet', 'csv', 'excel'],
        patterns: [
          '.*\\b(sum|total|average|avg|count|calculate)\\b.*\\b(column|data|spreadsheet|csv|excel)\\b.*',
          '.*\\b(add up|total up)\\b.*',
          '.*\\.(csv|xlsx|xls|ods)\\b.*\\b(sum|total|average|count)\\b.*'
        ],
        priority: 90
      },
      {
        tool: 'summarize_doc',
        triggers: ['summarize', 'summary', 'explain', 'find in pdf', 'pdf', 'document', 'bullet points'],
        patterns: [
          '.*\\b(summarize|summary)\\b.*\\b(pdf|document)\\b.*',
          '.*\\b(explain|describe)\\b.*\\b(pdf|document)\\b.*',
          '.*\\b(find|search)\\b.*\\b(in|pdf)\\b.*',
          '.*\\.(pdf)\\b.*\\b(summarize|summary|explain|bullet)\\b.*'
        ],
        priority: 85
      },
      {
        tool: 'open_item',
        triggers: ['open', 'launch', 'start', 'run', 'execute', 'show'],
        patterns: [
          '.*\\b(open|launch|start|run|execute)\\b.*',
          '.*\\b(show|display)\\b.*\\b(file|folder|application|app)\\b.*'
        ],
        priority: 80
      },
      {
        tool: 'create_file',
        triggers: ['create', 'make', 'write', 'new file', 'generate'],
        patterns: [
          '.*\\b(create|make|write|generate)\\b.*\\b(file|document)\\b.*',
          '.*\\b(new)\\b.*\\b(file|document|text)\\b.*'
        ],
        priority: 75
      }
    ];
  }

  /**
   * Analyze user input and determine the best tool to use
   */
  analyzeInput(input: string): { tool: string; confidence: number; matchedPatterns: string[] } {
    const lowerInput = input.toLowerCase();
    const matches: Array<{ tool: string; priority: number; patterns: string[] }> = [];

    // Check each routing rule
    for (const rule of this.routingRules) {
      const matchedPatterns: string[] = [];
      let hasMatch = false;

      // Check trigger words
      for (const trigger of rule.triggers) {
        if (lowerInput.includes(trigger.toLowerCase())) {
          hasMatch = true;
          matchedPatterns.push(`trigger:${trigger}`);
        }
      }

      // Check regex patterns
      for (const pattern of rule.patterns) {
        try {
          const regex = new RegExp(pattern, 'i');
          if (regex.test(input)) {
            hasMatch = true;
            matchedPatterns.push(`pattern:${pattern}`);
          }
        } catch (e) {
          console.warn('Invalid regex pattern:', pattern);
        }
      }

      if (hasMatch) {
        matches.push({
          tool: rule.tool,
          priority: rule.priority,
          patterns: matchedPatterns
        });
      }
    }

    // Sort by priority and return the best match
    if (matches.length > 0) {
      matches.sort((a, b) => b.priority - a.priority);
      const bestMatch = matches[0]!;
      
      // Calculate confidence based on number of matches and priority
      const confidence = Math.min(0.95, (bestMatch.priority / 100) + (bestMatch.patterns.length * 0.1));
      
      return {
        tool: bestMatch.tool,
        confidence,
        matchedPatterns: bestMatch.patterns
      };
    }

    // Fallback
    return {
      tool: this.fallbackTool,
      confidence: 0.3,
      matchedPatterns: ['fallback']
    };
  }

  /**
   * Execute a tool with the given parameters
   */
  async executeTool(
    toolName: string, 
    parameters: Record<string, any>,
    onProgress?: (progress: ActionProgress) => void
  ): Promise<KiroResponse> {
    const startTime = Date.now();
    
    try {
      // Validate tool exists
      const tool = this.tools.get(toolName);
      if (!tool) {
        return {
          success: false,
          message: `Unknown tool: ${toolName}`,
          error: `Unknown tool: ${toolName}`,
          error_code: 'UNKNOWN_TOOL',
          suggestions: [
            {
              type: 'alternative',
              message: `Available tools: ${Array.from(this.tools.keys()).join(', ')}`,
              example: 'Try using one of the available tools'
            }
          ]
        };
      }

      // Convert to ParsedIntent format for router actions
      const intentMap: Record<string, 'CreateFile' | 'OpenItem' | 'AnalyzeSpreadsheet' | 'SummarizeDoc'> = {
        'create_file': 'CreateFile',
        'open_item': 'OpenItem',
        'analyze_sheet': 'AnalyzeSpreadsheet',
        'summarize_doc': 'SummarizeDoc'
      };

      const intent: ParsedIntent = {
        intent: intentMap[toolName] || 'CreateFile',
        confidence: 0.9,
        parameters,
        context: {
          sessionId: 'kiro-agent',
          timestamp: new Date().toISOString(),
          userInput: `${toolName} execution`
        }
      };

      // Execute through router actions
      const result = await routerActions.executeIntent(intent, onProgress);
      const executionTime = Date.now() - startTime;

      if (result.success) {
        return {
          success: true,
          tool: toolName,
          message: result.message,
          data: result.data,
          execution_time: executionTime,
          metadata: {
            confidence: 0.9,
            matched_patterns: ['direct_execution']
          }
        };
      } else {
        return {
          success: false,
          message: result.error || result.message || 'Tool execution failed',
          tool: toolName,
          error: result.error || result.message,
          error_code: 'EXECUTION_FAILED',
          execution_time: executionTime,
          metadata: {
            attempted_tool: toolName,
            error_details: result
          },
          suggestions: this.generateErrorSuggestions(toolName, result.error || result.message)
        };
      }

    } catch (error) {
      const executionTime = Date.now() - startTime;
      
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        tool: toolName,
        error: error instanceof Error ? error.message : 'Unknown error',
        error_code: 'EXECUTION_ERROR',
        execution_time: executionTime,
        metadata: {
          attempted_tool: toolName,
          error_details: { error: error instanceof Error ? error.message : error }
        },
        suggestions: this.generateErrorSuggestions(toolName, error instanceof Error ? error.message : 'Unknown error')
      };
    }
  }

  /**
   * Process user input and execute the appropriate tool
   */
  async processInput(
    input: string,
    onProgress?: (progress: ActionProgress) => void
  ): Promise<KiroResponse> {
    // Analyze input to determine tool
    const analysis = this.analyzeInput(input);
    
    // Extract parameters based on the tool and input
    const parameters = this.extractParameters(analysis.tool, input);
    
    // Execute the tool
    const response = await this.executeTool(analysis.tool, parameters, onProgress);
    
    // Add analysis metadata to response
    if (response.metadata) {
      response.metadata.confidence = analysis.confidence;
      response.metadata.matched_patterns = analysis.matchedPatterns;
      response.metadata.alternative_tools = this.getAlternativeTools(analysis.tool);
    }
    
    return response;
  }

  /**
   * Extract parameters from user input based on the selected tool
   */
  private extractParameters(toolName: string, input: string): Record<string, any> {
    // const _lowerInput = input.toLowerCase();
    
    switch (toolName) {
      case 'create_file':
        return this.extractCreateFileParams(input);
      
      case 'open_item':
        return this.extractOpenItemParams(input);
      
      case 'analyze_sheet':
        return this.extractAnalyzeSheetParams(input);
      
      case 'summarize_doc':
        return this.extractSummarizeDocParams(input);
      
      default:
        return {};
    }
  }

  private extractCreateFileParams(input: string): Record<string, any> {
    const params: Record<string, any> = {};
    
    // Extract filename
    const fileMatch = input.match(/(?:create|make|write|new)\s+(?:file\s+)?(?:called\s+|named\s+)?[\"']?([^\s\"']+\.[a-zA-Z0-9]+)[\"']?/i);
    if (fileMatch) {
      params.title = fileMatch[1];
    } else {
      params.title = 'untitled.txt';
    }
    
    // Extract path
    const pathMatch = input.match(/(?:in|at|to)\s+[\"']?([^\s\"']+)[\"']?/i);
    if (pathMatch) {
      params.path = pathMatch[1];
    }
    
    // Extract content
    const contentMatch = input.match(/(?:with|containing)\s+[\"']([^\"']+)[\"']/i);
    if (contentMatch) {
      params.content = contentMatch[1];
    }
    
    return params;
  }

  private extractOpenItemParams(input: string): Record<string, any> {
    const params: Record<string, any> = {};
    
    // Extract query
    const queryMatch = input.match(/(?:open|launch|start|run|show)\s+[\"']?([^\"']+)[\"']?/i);
    if (queryMatch) {
      params.query = queryMatch?.[1]?.trim() || '';
    } else {
      params.query = input.replace(/^(open|launch|start|run|show)\s+/i, '').trim();
    }
    
    // Determine type
    if (input.match(/\.(exe|app|dmg)$/i) || input.match(/\b(application|app|program)\b/i)) {
      params.type = 'application';
    } else if (input.match(/\b(folder|directory)\b/i)) {
      params.type = 'folder';
    } else if (input.match(/\.(txt|pdf|xlsx|csv|docx|jpg|png|gif)$/i)) {
      params.type = 'file';
    } else {
      params.type = 'auto';
    }
    
    return params;
  }

  private extractAnalyzeSheetParams(input: string): Record<string, any> {
    const params: Record<string, any> = {};
    
    // Extract file path
    const pathMatch = input.match(/[\"']?([^\s\"']+\.(csv|xlsx|xls|ods))[\"']?/i);
    if (pathMatch) {
      params.path = pathMatch[1];
    } else {
      params.path = 'data.csv'; // Default
    }
    
    // Extract operation
    if (input.match(/\b(sum|total|add up)\b/i)) {
      params.op = 'sum';
    } else if (input.match(/\b(average|avg|mean)\b/i)) {
      params.op = 'avg';
    } else if (input.match(/\bcount\b/i)) {
      params.op = 'count';
    } else {
      params.op = 'sum'; // Default
    }
    
    // Extract column
    const columnMatch = input.match(/(?:column|field)\s+[\"']?([^\s\"']+)[\"']?/i) ||
                       input.match(/\b(salary|revenue|amount|price|cost|value|quantity|total)\b/i);
    if (columnMatch) {
      params.column = columnMatch[1];
    } else {
      params.column = 'value'; // Default
    }
    
    return params;
  }

  private extractSummarizeDocParams(input: string): Record<string, any> {
    const params: Record<string, any> = {};
    
    // Extract file path
    const pathMatch = input.match(/[\"']?([^\s\"']+\.pdf)[\"']?/i);
    if (pathMatch) {
      params.path = pathMatch[1];
    } else {
      params.path = 'document.pdf'; // Default
    }
    
    // Extract length type
    if (input.match(/\b(bullet|bullets|bullet points|key points)\b/i)) {
      params.length = 'bullets';
    } else if (input.match(/\b(tweet|short|brief|concise)\b/i)) {
      params.length = 'tweet';
    } else {
      params.length = 'short'; // Default
    }
    
    return params;
  }

  private generateErrorSuggestions(toolName: string, error: string): KiroResponse['suggestions'] {
    const suggestions: KiroResponse['suggestions'] = [];
    
    if (error.includes('not found')) {
      suggestions.push({
        type: 'clarify',
        message: 'The file or item could not be found. Please check the path and try again.',
        example: 'Make sure the file exists and the path is correct'
      });
    }
    
    if (error.includes('permission')) {
      suggestions.push({
        type: 'alternative',
        message: 'Permission denied. Try running with appropriate permissions.',
        example: 'Check file permissions or try a different location'
      });
    }
    
    if (toolName === 'analyze_sheet' && error.includes('column')) {
      suggestions.push({
        type: 'rephrase',
        message: 'Column not found. Try using a different column name.',
        example: 'Use exact column names like "Amount" or "Revenue"'
      });
    }
    
    return suggestions;
  }

  private getAlternativeTools(currentTool: string): string[] {
    const alternatives: Record<string, string[]> = {
      'create_file': ['open_item'],
      'open_item': ['create_file'],
      'analyze_sheet': ['summarize_doc'],
      'summarize_doc': ['analyze_sheet']
    };
    
    return alternatives[currentTool] || [];
  }

  /**
   * Get available tools and their descriptions
   */
  getAvailableTools(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  /**
   * Get tool schema for validation
   */
  getToolSchema(toolName: string): any {
    return this.tools.get(toolName)?.schema;
  }
}

// Global Kiro agent instance
export const kiroAgent = new KiroAgent();

// Convenience function for processing user input
export const processUserInput = (input: string, onProgress?: (progress: ActionProgress) => void) => {
  return kiroAgent.processInput(input, onProgress);
};