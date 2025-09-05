import { TTSAdapter, TTSOptions, TTSVoice } from '../types';

export class OpenAITTS implements TTSAdapter {
  name = 'openai-tts';
  private apiKey: string;
  private currentAudio: HTMLAudioElement | null = null;
  private isPlaying = false;
  private isPaused = false;
  private startCallback: (() => void) | null = null;
  private endCallback: (() => void) | null = null;
  private errorCallback: ((error: Error) => void) | null = null;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async isAvailable(): Promise<boolean> {
    return !!this.apiKey && typeof Audio !== 'undefined';
  }

  async speak(text: string, options?: TTSOptions): Promise<void> {
    if (this.isPlaying) {
      this.stop();
    }

    try {
      const audioUrl = await this.generateAudio(text, options);
      await this.playAudio(audioUrl);
    } catch (error) {
      this.errorCallback?.(error as Error);
      throw error;
    }
  }

  private async generateAudio(text: string, options?: TTSOptions): Promise<string> {
    const response = await fetch('https://api.openai.com/v1/audio/speech', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'tts-1',
        input: text,
        voice: options?.voice || 'alloy',
        response_format: 'mp3',
        speed: options?.rate || 1.0,
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenAI TTS API error: ${response.status} ${response.statusText}`);
    }

    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
  }

  private async playAudio(audioUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.currentAudio = new Audio(audioUrl);
      this.isPlaying = true;
      this.isPaused = false;

      this.currentAudio.onloadstart = () => {
        this.startCallback?.();
      };

      this.currentAudio.onended = () => {
        this.isPlaying = false;
        this.isPaused = false;
        this.endCallback?.();
        URL.revokeObjectURL(audioUrl);
        resolve();
      };

      this.currentAudio.onerror = (error) => {
        this.isPlaying = false;
        this.isPaused = false;
        URL.revokeObjectURL(audioUrl);
        const audioError = new Error(`Audio playback error: ${error}`);
        this.errorCallback?.(audioError);
        reject(audioError);
      };

      this.currentAudio.play().catch(reject);
    });
  }

  stop(): void {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    this.isPlaying = false;
    this.isPaused = false;
  }

  pause(): void {
    if (this.currentAudio && this.isPlaying && !this.isPaused) {
      this.currentAudio.pause();
      this.isPaused = true;
    }
  }

  resume(): void {
    if (this.currentAudio && this.isPaused) {
      this.currentAudio.play();
      this.isPaused = false;
    }
  }

  async getVoices(): Promise<TTSVoice[]> {
    // OpenAI TTS voices
    return [
      { id: 'alloy', name: 'Alloy', lang: 'en-US', gender: 'neutral' },
      { id: 'echo', name: 'Echo', lang: 'en-US', gender: 'male' },
      { id: 'fable', name: 'Fable', lang: 'en-US', gender: 'neutral' },
      { id: 'onyx', name: 'Onyx', lang: 'en-US', gender: 'male' },
      { id: 'nova', name: 'Nova', lang: 'en-US', gender: 'female' },
      { id: 'shimmer', name: 'Shimmer', lang: 'en-US', gender: 'female' },
    ];
  }

  onStart(callback: () => void): void {
    this.startCallback = callback;
  }

  onEnd(callback: () => void): void {
    this.endCallback = callback;
  }

  onError(callback: (error: Error) => void): void {
    this.errorCallback = callback;
  }
}