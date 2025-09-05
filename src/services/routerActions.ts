/**
 * Router Actions for Intent Execution
 * Maps parsed intents to API calls with progress tracking
 */

import { ParsedIntent, ActionProgress } from '../types';
import { apiClient, APIError, CustomProgressEvent } from './apiClient';

export interface ActionResult {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
  requiresVerification?: boolean;
}

export type ProgressCallback = (progress: ActionProgress) => void;

export class RouterActions {
  constructor(_baseURL: string = 'http://localhost:8000') {
    // Configure API client with base URL
    // Note: apiClient.baseURL is configured internally
  }

  /**
   * Execute an intent by routing to the appropriate action
   */
  async executeIntent(
    intent: ParsedIntent, 
    onProgress?: ProgressCallback
  ): Promise<ActionResult> {
    try {
      onProgress?.({
        phase: 'starting',
        progress: 0,
        message: `Starting ${intent.intent} operation...`
      });

      switch (intent.intent) {
        case 'CreateFile':
          return await this.createFile(intent.parameters, onProgress);
        
        case 'OpenItem':
          return await this.openItem(intent.parameters, onProgress);
        
        case 'AnalyzeSpreadsheet':
          return await this.analyzeSpreadsheet(intent.parameters, onProgress);
        
        case 'SummarizeDoc':
          return await this.summarizeDocument(intent.parameters, onProgress);
        
        default:
          throw new Error(`Unsupported intent: ${intent.intent}`);
      }
    } catch (error) {
      const errorMessage = error instanceof APIError 
        ? error.getUserMessage() 
        : error instanceof Error 
          ? error.message 
          : 'Unknown error occurred';

      onProgress?.({
        phase: 'error',
        progress: 0,
        message: `Failed: ${errorMessage}`,
        details: error
      });

      return {
        success: false,
        message: errorMessage,
        error: errorMessage
      };
    }
  }

  /**
   * Create a file
   */
  private async createFile(
    parameters: any, 
    onProgress?: ProgressCallback
  ): Promise<ActionResult> {
    const { title, path, content } = parameters;

    onProgress?.({
      phase: 'processing',
      progress: 25,
      message: `Creating file "${title}"...`
    });

    try {
      const response = await apiClient.postJSON('/create_file', {
        title,
        path,
        content: content || ''
      }, {
        onProgress: (apiProgress: CustomProgressEvent) => {
          onProgress?.({
            phase: 'processing',
            progress: 25 + (apiProgress.progress * 0.5), // Scale to 25-75%
            message: apiProgress.message
          });
        }
      });

      onProgress?.({
        phase: 'complete',
        progress: 100,
        message: `File "${title}" created successfully`
      });

      return {
        success: true,
        message: `File "${title}" created at ${response.data?.file_path}`,
        data: response.data,
        requiresVerification: false
      };

    } catch (error) {
      if (error instanceof APIError && error.status === 409) {
        return {
          success: false,
          message: `File "${title}" already exists`,
          error: 'File already exists',
          requiresVerification: false
        };
      }
      throw error;
    }
  }

  /**
   * Open an item (file, application, folder)
   */
  private async openItem(
    parameters: any, 
    onProgress?: ProgressCallback
  ): Promise<ActionResult> {
    const { query, type = 'auto' } = parameters;

    onProgress?.({
      phase: 'processing',
      progress: 25,
      message: `Searching for "${query}"...`
    });

    try {
      const response = await apiClient.postJSON('/open_item', {
        query,
        type
      }, {
        onProgress: (apiProgress: CustomProgressEvent) => {
          onProgress?.({
            phase: 'processing',
            progress: 25 + (apiProgress.progress * 0.5),
            message: apiProgress.message
          });
        }
      });

      onProgress?.({
        phase: 'complete',
        progress: 100,
        message: `Opened "${query}" successfully`
      });

      return {
        success: true,
        message: `Opened "${query}" (${response.data?.type})`,
        data: response.data,
        requiresVerification: false
      };

    } catch (error) {
      if (error instanceof APIError && error.status === 404) {
        return {
          success: false,
          message: `Could not find "${query}"`,
          error: 'Item not found',
          requiresVerification: false
        };
      }
      throw error;
    }
  }

  /**
   * Analyze spreadsheet data
   */
  private async analyzeSpreadsheet(
    parameters: any, 
    onProgress?: ProgressCallback
  ): Promise<ActionResult> {
    const { path, op, column } = parameters;

    onProgress?.({
      phase: 'processing',
      progress: 20,
      message: `Loading spreadsheet "${path}"...`
    });

    try {
      const response = await apiClient.postJSON('/analyze_sheet', {
        path,
        op,
        column
      }, {
        timeout: 60000, // Longer timeout for large files
        onProgress: (apiProgress: CustomProgressEvent) => {
          let message = apiProgress.message;
          if (apiProgress.phase === 'processing') {
            message = `Analyzing ${column} column...`;
          }
          
          onProgress?.({
            phase: 'processing',
            progress: 20 + (apiProgress.progress * 0.6),
            message
          });
        }
      });

      onProgress?.({
        phase: 'complete',
        progress: 100,
        message: `Analysis complete: ${response.result}`
      });

      const operationMap: Record<string, string> = {
        sum: 'Sum',
        avg: 'Average',
        count: 'Count',
        total: 'Total'
      };
      const operationName = operationMap[op as string] || op;

      return {
        success: true,
        message: `${operationName} of "${response.matched_column}": ${response.result} (${response.cells_count} cells)`,
        data: {
          result: response.result,
          matchedColumn: response.matched_column,
          cellsCount: response.cells_count,
          operation: op
        },
        requiresVerification: false
      };

    } catch (error) {
      if (error instanceof APIError && error.status === 404) {
        return {
          success: false,
          message: `Spreadsheet file "${path}" not found`,
          error: 'File not found',
          requiresVerification: false
        };
      }
      if (error instanceof APIError && error.status === 400) {
        return {
          success: false,
          message: `Invalid operation: ${error.message}`,
          error: error.message,
          requiresVerification: false
        };
      }
      throw error;
    }
  }

  /**
   * Summarize a document
   */
  private async summarizeDocument(
    parameters: any, 
    onProgress?: ProgressCallback
  ): Promise<ActionResult> {
    const { path, length = 'short' } = parameters;

    onProgress?.({
      phase: 'processing',
      progress: 15,
      message: `Loading document "${path}"...`
    });

    try {
      const response = await apiClient.postJSON('/summarize_doc', {
        path,
        length
      }, {
        timeout: 120000, // 2 minutes for document processing
        onProgress: (apiProgress: CustomProgressEvent) => {
          let message = apiProgress.message;
          if (apiProgress.phase === 'processing') {
            if (apiProgress.progress < 30) {
              message = 'Extracting text from PDF...';
            } else if (apiProgress.progress < 70) {
              message = 'Generating summary...';
            } else {
              message = 'Finalizing summary...';
            }
          }
          
          onProgress?.({
            phase: 'processing',
            progress: 15 + (apiProgress.progress * 0.7),
            message
          });
        }
      });

      onProgress?.({
        phase: 'complete',
        progress: 100,
        message: `Document summarized (${response.word_count} words)`
      });

      const lengthMap: Record<string, string> = {
        short: 'Short summary',
        bullets: 'Bullet points',
        tweet: 'Tweet-length summary'
      };
      const lengthDescription = lengthMap[length as string] || 'Summary';

      return {
        success: true,
        message: `${lengthDescription} generated (${response.word_count} words)`,
        data: {
          summary: response.summary,
          lengthType: response.length_type,
          wordCount: response.word_count
        },
        requiresVerification: false
      };

    } catch (error) {
      if (error instanceof APIError && error.status === 404) {
        return {
          success: false,
          message: `PDF file "${path}" not found`,
          error: 'File not found',
          requiresVerification: false
        };
      }
      throw error;
    }
  }

  /**
   * Test connection to the backend API
   */
  async testConnection(): Promise<boolean> {
    try {
      return await apiClient.healthCheck();
    } catch {
      return false;
    }
  }

  /**
   * Get server information
   */
  async getServerInfo(): Promise<any> {
    try {
      return await apiClient.getServerInfo();
    } catch (error) {
      throw error;
    }
  }
}

// Global router actions instance
export const routerActions = new RouterActions();

// Convenience function for executing intents
export const executeIntent = (intent: ParsedIntent, onProgress?: ProgressCallback) => {
  return routerActions.executeIntent(intent, onProgress);
};