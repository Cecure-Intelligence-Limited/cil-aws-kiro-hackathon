// Common types for all adapters

export interface STTResult {
  text: string;
  isFinal: boolean;
  confidence: number;
  timestamp: number;
}

export interface STTAdapter {
  name: string;
  isAvailable(): Promise<boolean>;
  startRecording(): Promise<void>;
  stopRecording(): Promise<void>;
  onResult(callback: (result: STTResult) => void): void;
  onError(callback: (error: Error) => void): void;
  cleanup(): void;
}

export interface TTSVoice {
  id: string;
  name: string;
  lang: string;
  gender: 'male' | 'female' | 'neutral';
}

export interface TTSOptions {
  voice?: string;
  rate?: number;    // 0.1 to 10
  pitch?: number;   // 0 to 2
  volume?: number;  // 0 to 1
}

export interface TTSAdapter {
  name: string;
  isAvailable(): Promise<boolean>;
  speak(text: string, options?: TTSOptions): Promise<void>;
  stop(): void;
  pause(): void;
  resume(): void;
  getVoices(): Promise<TTSVoice[]>;
  onStart(callback: () => void): void;
  onEnd(callback: () => void): void;
  onError(callback: (error: Error) => void): void;
}

export interface AdapterConfig {
  sttProvider: 'vosk' | 'whisper' | 'none';
  ttsProvider: 'system' | 'openai' | 'edge' | 'none';
  apiKeys?: {
    whisper?: string | undefined;
    openai?: string | undefined;
  };
  voiceSettings?: {
    voice?: string;
    rate?: number;
    pitch?: number;
    volume?: number;
  };
  stt?: {
    provider: 'vosk' | 'whisper';
    options?: Record<string, any>;
  };
  tts?: {
    provider: 'system' | 'openai' | 'edge';
    options?: Record<string, any>;
  };
}

export interface AdapterError extends Error {
  code: string;
  provider: string;
  details?: any;
}