/**
 * API Client for Aura Desktop Assistant Backend
 * Provides robust HTTP client with error handling, timeouts, and retry logic
 */

export interface APIError {
  code: string;
  message: string;
  status: number | undefined;
  details?: any;
}

export interface APIResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
}

export interface CustomProgressEvent {
  progress: number;
  message: string;
  phase?: string;
}

export interface RequestConfig {
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  signal?: AbortSignal;
  onProgress?: (progress: CustomProgressEvent) => void;
}

export interface ProgressInfo {
  phase: 'connecting' | 'uploading' | 'processing' | 'downloading' | 'complete' | 'error';
  progress: number; // 0-100
  message: string;
  details?: any;
}

class APIClient {
  private baseURL: string;
  private defaultTimeout: number;
  private defaultRetries: number;
  private defaultRetryDelay: number;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL.replace(/\/$/, ''); // Remove trailing slash
    this.defaultTimeout = 30000; // 30 seconds
    this.defaultRetries = 3;
    this.defaultRetryDelay = 1000; // 1 second
  }

  /**
   * Make a POST request with JSON body
   */
  async postJSON<T = any>(
    path: string, 
    body: Record<string, any>, 
    config: RequestConfig = {}
  ): Promise<T> {
    const {
      timeout = this.defaultTimeout,
      retries = this.defaultRetries,
      retryDelay = this.defaultRetryDelay,
      signal,
      onProgress
    } = config;

    const url = `${this.baseURL}${path.startsWith('/') ? path : `/${path}`}`;
    
    // Report initial progress
    onProgress?.({
      phase: 'connecting',
      progress: 0,
      message: 'Connecting to server...'
    });

    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        // Combine signals if provided
        const combinedSignal = signal ? this.combineSignals([signal, controller.signal]) : controller.signal;

        onProgress?.({
          phase: 'uploading',
          progress: 10,
          message: `Sending request (attempt ${attempt}/${retries})...`
        });

        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(body),
          signal: combinedSignal,
        });

        clearTimeout(timeoutId);

        onProgress?.({
          phase: 'processing',
          progress: 50,
          message: 'Processing request...'
        });

        // Handle different response statuses
        if (!response.ok) {
          const errorData = await this.parseErrorResponse(response);
          throw new APIError(
            errorData.code || `HTTP_${response.status}`,
            errorData.message || response.statusText,
            response.status,
            errorData.details
          );
        }

        onProgress?.({
          phase: 'downloading',
          progress: 80,
          message: 'Receiving response...'
        });

        const data = await response.json();

        onProgress?.({
          phase: 'complete',
          progress: 100,
          message: 'Request completed successfully'
        });

        return data;

      } catch (error) {
        lastError = error as Error;

        // Don't retry on certain errors
        if (error instanceof APIError) {
          if (error.status && error.status >= 400 && error.status < 500) {
            // Client errors (4xx) shouldn't be retried
            throw error;
          }
        }

        if (error instanceof DOMException && error.name === 'AbortError') {
          throw new APIError(
            'REQUEST_ABORTED',
            'Request was aborted',
            0,
            { attempt, totalAttempts: retries }
          );
        }

        // If this is the last attempt, throw the error
        if (attempt === retries) {
          break;
        }

        // Wait before retrying
        onProgress?.({
          phase: 'connecting',
          progress: 0,
          message: `Retrying in ${retryDelay}ms... (attempt ${attempt + 1}/${retries})`
        });

        await this.delay(retryDelay * attempt); // Exponential backoff
      }
    }

    // If we get here, all retries failed
    onProgress?.({
      phase: 'error',
      progress: 0,
      message: 'Request failed after all retries'
    });

    if (lastError instanceof APIError) {
      throw lastError;
    }

    throw new APIError(
      'REQUEST_FAILED',
      lastError?.message || 'Request failed after all retries',
      0,
      { attempts: retries, lastError: lastError?.message }
    );
  }

  /**
   * Parse error response from the server
   */
  private async parseErrorResponse(response: Response): Promise<any> {
    try {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        const text = await response.text();
        return {
          code: `HTTP_${response.status}`,
          message: text || response.statusText,
        };
      }
    } catch {
      return {
        code: `HTTP_${response.status}`,
        message: response.statusText,
      };
    }
  }

  /**
   * Combine multiple AbortSignals
   */
  private combineSignals(signals: AbortSignal[]): AbortSignal {
    const controller = new AbortController();
    
    for (const signal of signals) {
      if (signal.aborted) {
        controller.abort();
        break;
      }
      signal.addEventListener('abort', () => controller.abort());
    }
    
    return controller.signal;
  }

  /**
   * Delay utility for retries
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Check if the API server is reachable
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.postJSON('/health', {}, { 
        timeout: 5000, 
        retries: 1 
      });
      return response.status === 'healthy';
    } catch {
      return false;
    }
  }

  /**
   * Get server status and configuration
   */
  async getServerInfo(): Promise<any> {
    return this.postJSON('/health', {}, { timeout: 5000 });
  }
}

// Custom error class for API errors
export class APIError extends Error {
  public code: string;
  public status: number | undefined;
  public details?: any;

  constructor(code: string, message: string, status?: number, details?: any) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.status = status;
    this.details = details;
  }

  /**
   * Check if this is a network error
   */
  isNetworkError(): boolean {
    return this.code === 'REQUEST_FAILED' || this.code === 'REQUEST_ABORTED' || !this.status;
  }

  /**
   * Check if this is a client error (4xx)
   */
  isClientError(): boolean {
    return this.status ? this.status >= 400 && this.status < 500 : false;
  }

  /**
   * Check if this is a server error (5xx)
   */
  isServerError(): boolean {
    return this.status ? this.status >= 500 : false;
  }

  /**
   * Get user-friendly error message
   */
  getUserMessage(): string {
    if (this.isNetworkError()) {
      return 'Unable to connect to the server. Please check your connection and try again.';
    }
    
    if (this.isClientError()) {
      return this.message || 'Invalid request. Please check your input and try again.';
    }
    
    if (this.isServerError()) {
      return 'Server error occurred. Please try again later.';
    }
    
    return this.message || 'An unexpected error occurred.';
  }
}

// Global API client instance
export const apiClient = new APIClient();

// Convenience function for the postJSON method
export const postJSON = (path: string, body: Record<string, any>, config?: RequestConfig) => {
  return apiClient.postJSON(path, body, config);
};