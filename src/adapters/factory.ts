import { STTAdapter, TTSAdapter, AdapterConfig } from './types';
import { WhisperApiSTT } from './stt/whisperApi';
import { VoskLocalSTT } from './stt/voskLocal';
import { OpenAITTS } from './tts/openaiTTS';
import { EdgeTTS } from './tts/edgeTTS';
import { SystemTTS } from './tts/systemTTS';

export class AdapterFactory {
  private static instance: AdapterFactory;
  private sttCache = new Map<string, STTAdapter>();
  private ttsCache = new Map<string, TTSAdapter>();

  private constructor() {}

  static getInstance(): AdapterFactory {
    if (!AdapterFactory.instance) {
      AdapterFactory.instance = new AdapterFactory();
    }
    return AdapterFactory.instance;
  }

  async getSTT(config: AdapterConfig): Promise<STTAdapter | null> {
    if (config.sttProvider === 'none') {
      return null;
    }

    const cacheKey = `${config.sttProvider}-${JSON.stringify(config.apiKeys)}`;
    
    if (this.sttCache.has(cacheKey)) {
      return this.sttCache.get(cacheKey)!;
    }

    let adapter: STTAdapter;

    switch (config.sttProvider) {
      case 'whisper':
        if (!config.apiKeys?.whisper && !config.apiKeys?.openai) {
          throw new Error('Whisper API key is required for Whisper STT');
        }
        adapter = new WhisperApiSTT(config.apiKeys.whisper || config.apiKeys.openai!);
        break;

      case 'vosk':
        adapter = new VoskLocalSTT();
        break;

      default:
        throw new Error(`Unknown STT provider: ${config.sttProvider}`);
    }

    // Check if adapter is available
    const isAvailable = await adapter.isAvailable();
    if (!isAvailable) {
      throw new Error(`STT adapter ${config.sttProvider} is not available`);
    }

    this.sttCache.set(cacheKey, adapter);
    return adapter;
  }

  async getTTS(config: AdapterConfig): Promise<TTSAdapter | null> {
    if (config.ttsProvider === 'none') {
      return null;
    }

    const cacheKey = `${config.ttsProvider}-${JSON.stringify(config.apiKeys)}-${JSON.stringify(config.voiceSettings)}`;
    
    if (this.ttsCache.has(cacheKey)) {
      return this.ttsCache.get(cacheKey)!;
    }

    let adapter: TTSAdapter;

    switch (config.ttsProvider) {
      case 'openai':
        if (!config.apiKeys?.openai) {
          throw new Error('OpenAI API key is required for OpenAI TTS');
        }
        adapter = new OpenAITTS(config.apiKeys.openai);
        break;

      case 'edge':
        adapter = new EdgeTTS();
        break;

      case 'system':
        adapter = new SystemTTS();
        break;

      default:
        throw new Error(`Unknown TTS provider: ${config.ttsProvider}`);
    }

    // Check if adapter is available
    const isAvailable = await adapter.isAvailable();
    if (!isAvailable) {
      throw new Error(`TTS adapter ${config.ttsProvider} is not available`);
    }

    this.ttsCache.set(cacheKey, adapter);
    return adapter;
  }

  // Utility methods for testing adapter availability
  async testSTTAvailability(provider: 'whisper' | 'vosk', apiKey?: string): Promise<boolean> {
    try {
      const config: AdapterConfig = {
        sttProvider: provider,
        ttsProvider: 'none',
        ...(apiKey ? { apiKeys: { [provider === 'whisper' ? 'whisper' : 'vosk']: apiKey } } : {}),
      };
      
      const adapter = await this.getSTT(config);
      return adapter !== null;
    } catch {
      return false;
    }
  }

  async testTTSAvailability(provider: 'openai' | 'edge' | 'system', apiKey?: string): Promise<boolean> {
    try {
      const config: AdapterConfig = {
        sttProvider: 'none',
        ttsProvider: provider,
        ...(apiKey ? { apiKeys: { openai: apiKey } } : {}),
      };
      
      const adapter = await this.getTTS(config);
      return adapter !== null;
    } catch {
      return false;
    }
  }

  // Clear cache (useful for testing or when API keys change)
  clearCache(): void {
    // Clean up existing adapters
    this.sttCache.forEach(adapter => adapter.cleanup?.());
    this.ttsCache.forEach(adapter => adapter.stop?.());
    
    this.sttCache.clear();
    this.ttsCache.clear();
  }

  // Get available providers
  async getAvailableProviders(): Promise<{
    stt: Array<{ provider: 'whisper' | 'vosk'; available: boolean; requiresApiKey: boolean }>;
    tts: Array<{ provider: 'openai' | 'edge' | 'system'; available: boolean; requiresApiKey: boolean }>;
  }> {
    const sttProviders = [
      { provider: 'whisper' as const, requiresApiKey: true },
      { provider: 'vosk' as const, requiresApiKey: false },
    ];

    const ttsProviders = [
      { provider: 'openai' as const, requiresApiKey: true },
      { provider: 'edge' as const, requiresApiKey: false },
      { provider: 'system' as const, requiresApiKey: false },
    ];

    const sttResults = await Promise.all(
      sttProviders.map(async ({ provider, requiresApiKey }) => ({
        provider,
        available: await this.testSTTAvailability(provider),
        requiresApiKey,
      }))
    );

    const ttsResults = await Promise.all(
      ttsProviders.map(async ({ provider, requiresApiKey }) => ({
        provider,
        available: await this.testTTSAvailability(provider),
        requiresApiKey,
      }))
    );

    return {
      stt: sttResults,
      tts: ttsResults,
    };
  }
}

// Convenience functions
export const getSTT = (config: AdapterConfig) => AdapterFactory.getInstance().getSTT(config);
export const getTTS = (config: AdapterConfig) => AdapterFactory.getInstance().getTTS(config);
export const clearAdapterCache = () => AdapterFactory.getInstance().clearCache();
export const getAvailableProviders = () => AdapterFactory.getInstance().getAvailableProviders();