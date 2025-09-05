export interface Settings {
  sttProvider: 'vosk' | 'whisper' | 'none';
  allowCloudNLP: boolean;
  ttsProvider: 'system' | 'elevenlabs' | 'openai' | 'none';
}

export type AssistantState = 
  | 'idle'
  | 'capture'
  | 'parseIntent'
  | 'route'
  | 'execute'
  | 'verify'
  | 'respond'
  | 'recover';

export interface Intent {
  action: string;
  parameters: Record<string, any>;
  confidence: number;
}

// New structured intent types based on INTENTS.md
export interface ParsedIntent {
  intent: 'CreateFile' | 'OpenItem' | 'AnalyzeSpreadsheet' | 'SummarizeDoc';
  confidence: number;
  parameters: Record<string, any>;
  context?: {
    sessionId: string;
    timestamp: string;
    userInput: string;
  };
}

export interface ParseError {
  error: {
    code: 'INTENT_PARSE_FAILED' | 'AMBIGUOUS_INTENT' | 'MISSING_PARAMETERS' | 
          'INVALID_PARAMETERS' | 'LOW_CONFIDENCE' | 'UNSUPPORTED_OPERATION' | 'CONTEXT_REQUIRED';
    message: string;
    details?: {
      userInput: string;
      confidence?: number | undefined;
      missingFields?: string[] | undefined;
      invalidFields?: Array<{
        field: string;
        value: any;
        reason: string;
      }> | undefined;
    };
  };
  suggestions: Array<{
    type: 'rephrase' | 'clarify' | 'example' | 'alternative';
    message: string;
    example?: string;
  }>;
  context?: {
    sessionId: string;
    timestamp: string;
    userInput: string;
  };
}

export interface ExecutionResult {
  success: boolean;
  message: string;
  requiresVerification: boolean;
  data?: any;
}

export interface AssistantContext {
  input: string;
  result: string;
  isRecording: boolean;
  settings: Settings;
  intent: Intent | null;
  error: string | null;
  isVisible: boolean;
  inputMode: 'text' | 'voice';
  executionResult: ExecutionResult | null;
}

// Event types for XState
export type OrchestratorEvent =
  | { type: 'HOTKEY_TOGGLE' }
  | { type: 'STT_RESULT'; text: string }
  | { type: 'TEXT_SUBMIT'; text: string }
  | { type: 'INTENT_PARSED'; intent: Intent }
  | { type: 'EXEC_OK'; result: ExecutionResult }
  | { type: 'EXEC_ERR'; message: string }
  | { type: 'VERIFY_OK' }
  | { type: 'VERIFY_ERR' }
  | { type: 'START_CAPTURE' }
  | { type: 'CANCEL' }
  | { type: 'UPDATE_SETTINGS'; settings: Settings };

// Utility functions for API calls
export interface APICall {
  path: string;
  body: Record<string, any>;
}

export interface EffectHandlers {
  speak: (text: string) => Promise<void>;
  postJSON: (path: string, body: Record<string, any>) => Promise<any>;
  showError: (message: string) => void;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<void>;
  isRecordingAvailable: () => Promise<boolean>;
  isSpeechAvailable: () => Promise<boolean>;
  getSystemInfo: () => Promise<any>;
  isBackendAvailable: () => Promise<boolean>;
  showNotification: (title: string, message: string) => void;
  requestNotificationPermission: () => Promise<boolean>;
}

// Progress tracking types
export interface ProgressInfo {
  progress: number;
  message: string;
  phase?: string;
}

// Action progress for MCP
export interface ActionProgress {
  progress: number;
  message: string;
  phase?: string;
  data?: any;
  details?: any;
}

// MCP Server types
export interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface MCPRequest {
  id: string | number;
  method: string;
  params?: any;
}

export interface MCPResponse {
  id?: string | number | undefined;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

// Test result types
export interface TestResult {
  testCase: any;
  result: ParseError | ParsedIntent;
  passed: boolean;
  reason: string | undefined;
}