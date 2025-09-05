import { TTSAdapter, TTSOptions, TTSVoice } from '../types';

export class EdgeTTS implements TTSAdapter {
  name = 'edge-tts';
  private currentAudio: HTMLAudioElement | null = null;
  private isPlaying = false;
  private isPaused = false;
  private startCallback: (() => void) | null = null;
  private endCallback: (() => void) | null = null;
  private errorCallback: ((error: Error) => void) | null = null;

  async isAvailable(): Promise<boolean> {
    // Check if we can access the Edge TTS service
    return typeof Audio !== 'undefined' && 'speechSynthesis' in window;
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
    // Edge TTS API endpoint (unofficial)
    const voice = options?.voice || 'en-US-AriaNeural';
    const rate = options?.rate ? `${Math.round((options.rate - 1) * 100)}%` : '0%';
    const pitch = options?.pitch ? `${Math.round((options.pitch - 1) * 50)}Hz` : '0Hz';

    const ssml = `
      <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="${voice}">
          <prosody rate="${rate}" pitch="${pitch}">
            ${this.escapeXml(text)}
          </prosody>
        </voice>
      </speak>
    `;

    try {
      // In a real implementation, this would call the Edge TTS service
      // For now, we'll simulate by creating a blob URL
      const response = await this.callEdgeTTSService(ssml);
      const audioBlob = await response.blob();
      return URL.createObjectURL(audioBlob);
    } catch (error) {
      // Fallback to Web Speech API if Edge TTS is unavailable
      return this.fallbackToWebSpeech(text, options);
    }
  }

  private async callEdgeTTSService(_ssml: string): Promise<Response> {
    // This is a placeholder for the actual Edge TTS service call
    // In a real implementation, you would use the Microsoft Edge TTS API
    
    // For demonstration, we'll simulate the API call
    const mockAudioData = new ArrayBuffer(1024);
    const mockBlob = new Blob([mockAudioData], { type: 'audio/mp3' });
    
    return new Response(mockBlob, {
      status: 200,
      headers: { 'Content-Type': 'audio/mp3' }
    });
  }

  private async fallbackToWebSpeech(text: string, options?: TTSOptions): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!('speechSynthesis' in window)) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      
      if (options?.voice) {
        const voices = speechSynthesis.getVoices();
        const voice = voices.find(v => v.name.includes(options.voice!) || v.lang.includes('en'));
        if (voice) utterance.voice = voice;
      }
      
      if (options?.rate) utterance.rate = options.rate;
      if (options?.pitch) utterance.pitch = options.pitch;
      if (options?.volume) utterance.volume = options.volume;

      utterance.onstart = () => resolve('web-speech-fallback');
      utterance.onerror = (error) => reject(new Error(`Speech synthesis error: ${error.error}`));

      speechSynthesis.speak(utterance);
    });
  }

  private async playAudio(audioUrl: string): Promise<void> {
    if (audioUrl === 'web-speech-fallback') {
      // Web Speech API handles playback internally
      return;
    }

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
    
    // Also stop Web Speech API if it's being used
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    
    this.isPlaying = false;
    this.isPaused = false;
  }

  pause(): void {
    if (this.currentAudio && this.isPlaying && !this.isPaused) {
      this.currentAudio.pause();
      this.isPaused = true;
    }
    
    if ('speechSynthesis' in window && speechSynthesis.speaking) {
      speechSynthesis.pause();
      this.isPaused = true;
    }
  }

  resume(): void {
    if (this.currentAudio && this.isPaused) {
      this.currentAudio.play();
      this.isPaused = false;
    }
    
    if ('speechSynthesis' in window && speechSynthesis.paused) {
      speechSynthesis.resume();
      this.isPaused = false;
    }
  }

  async getVoices(): Promise<TTSVoice[]> {
    // Edge TTS voices (subset)
    return [
      { id: 'en-US-AriaNeural', name: 'Aria (Neural)', lang: 'en-US', gender: 'female' },
      { id: 'en-US-JennyNeural', name: 'Jenny (Neural)', lang: 'en-US', gender: 'female' },
      { id: 'en-US-GuyNeural', name: 'Guy (Neural)', lang: 'en-US', gender: 'male' },
      { id: 'en-US-DavisNeural', name: 'Davis (Neural)', lang: 'en-US', gender: 'male' },
      { id: 'en-GB-SoniaNeural', name: 'Sonia (Neural)', lang: 'en-GB', gender: 'female' },
      { id: 'en-GB-RyanNeural', name: 'Ryan (Neural)', lang: 'en-GB', gender: 'male' },
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

  private escapeXml(text: string): string {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;');
  }
}