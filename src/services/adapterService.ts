import { getSTT, getTTS } from '../adapters/factory';
import { AdapterConfig, STTAdapter, TTSAdapter, STTResult } from '../adapters/types';
import { Settings } from '../types';

export class AdapterService {
  private static instance: AdapterService;
  private sttAdapter: STTAdapter | null = null;
  private ttsAdapter: TTSAdapter | null = null;
  private currentConfig: AdapterConfig | null = null;

  private constructor() {}

  static getInstance(): AdapterService {
    if (!AdapterService.instance) {
      AdapterService.instance = new AdapterService();
    }
    return AdapterService.instance;
  }

  private settingsToConfig(settings: Settings): AdapterConfig {
    return {
      sttProvider: settings.sttProvider === 'whisper' ? 'whisper' : 
                   settings.sttProvider === 'vosk' ? 'vosk' : 'none',
      ttsProvider: settings.ttsProvider === 'system' ? 'system' : 
                   settings.ttsProvider === 'elevenlabs' ? 'edge' : 
                   settings.ttsProvider === 'openai' ? 'openai' : 'none',
      apiKeys: {
        openai: process.env.REACT_APP_OPENAI_API_KEY,
        whisper: process.env.REACT_APP_OPENAI_API_KEY,
      },
      voiceSettings: {
        rate: 1.0,
        pitch: 1.0,
        volume: 1.0,
      },
    };
  }

  async initialize(settings: Settings): Promise<void> {
    const config = this.settingsToConfig(settings);
    
    // Only reinitialize if config changed
    if (this.currentConfig && JSON.stringify(this.currentConfig) === JSON.stringify(config)) {
      return;
    }

    // Clean up existing adapters
    this.cleanup();

    try {
      // Initialize STT
      if (config.sttProvider !== 'none') {
        this.sttAdapter = await getSTT(config);
      }

      // Initialize TTS
      if (config.ttsProvider !== 'none') {
        this.ttsAdapter = await getTTS(config);
      }

      this.currentConfig = config;
    } catch (error) {
      console.error('Failed to initialize adapters:', error);
      throw error;
    }
  }

  async startSTT(onResult: (result: STTResult) => void, onError: (error: Error) => void): Promise<void> {
    if (!this.sttAdapter) {
      throw new Error('STT adapter not available');
    }

    this.sttAdapter.onResult(onResult);
    this.sttAdapter.onError(onError);
    await this.sttAdapter.startRecording();
  }

  async stopSTT(): Promise<void> {
    if (this.sttAdapter) {
      await this.sttAdapter.stopRecording();
    }
  }

  async speak(text: string): Promise<void> {
    if (!this.ttsAdapter) {
      // Fallback to console log
      console.log('TTS not available, would speak:', text);
      return;
    }

    await this.ttsAdapter.speak(text);
  }

  stopTTS(): void {
    if (this.ttsAdapter) {
      this.ttsAdapter.stop();
    }
  }

  isSTTAvailable(): boolean {
    return !!this.sttAdapter;
  }

  isTTSAvailable(): boolean {
    return !!this.ttsAdapter;
  }

  getTTSAdapter(): TTSAdapter | null {
    return this.ttsAdapter;
  }

  getSTTAdapter(): STTAdapter | null {
    return this.sttAdapter;
  }

  cleanup(): void {
    if (this.sttAdapter) {
      this.sttAdapter.cleanup();
      this.sttAdapter = null;
    }

    if (this.ttsAdapter) {
      this.ttsAdapter.stop();
      this.ttsAdapter = null;
    }

    this.currentConfig = null;
  }
}

// Singleton instance
export const adapterService = AdapterService.getInstance();