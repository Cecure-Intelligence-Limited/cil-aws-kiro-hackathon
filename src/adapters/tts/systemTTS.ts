import { TTSAdapter, TTSOptions, TTSVoice } from '../types';

export class SystemTTS implements TTSAdapter {
  name = 'system-tts';
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private isPlaying = false;
  private isPaused = false;
  private startCallback: (() => void) | null = null;
  private endCallback: (() => void) | null = null;
  private errorCallback: ((error: Error) => void) | null = null;

  async isAvailable(): Promise<boolean> {
    return 'speechSynthesis' in window;
  }

  async speak(text: string, options?: TTSOptions): Promise<void> {
    if (!('speechSynthesis' in window)) {
      throw new Error('Speech synthesis not supported in this browser');
    }

    if (this.isPlaying) {
      this.stop();
    }

    return new Promise((resolve, reject) => {
      this.currentUtterance = new SpeechSynthesisUtterance(text);
      
      // Apply options
      if (options?.voice) {
        const voices = speechSynthesis.getVoices();
        const voice = voices.find(v => 
          v.name.toLowerCase().includes(options.voice!.toLowerCase()) ||
          v.voiceURI.toLowerCase().includes(options.voice!.toLowerCase())
        );
        if (voice) {
          this.currentUtterance.voice = voice;
        }
      }
      
      if (options?.rate !== undefined) {
        this.currentUtterance.rate = Math.max(0.1, Math.min(10, options.rate));
      }
      
      if (options?.pitch !== undefined) {
        this.currentUtterance.pitch = Math.max(0, Math.min(2, options.pitch));
      }
      
      if (options?.volume !== undefined) {
        this.currentUtterance.volume = Math.max(0, Math.min(1, options.volume));
      }

      // Set up event handlers
      this.currentUtterance.onstart = () => {
        this.isPlaying = true;
        this.isPaused = false;
        this.startCallback?.();
      };

      this.currentUtterance.onend = () => {
        this.isPlaying = false;
        this.isPaused = false;
        this.currentUtterance = null;
        this.endCallback?.();
        resolve();
      };

      this.currentUtterance.onerror = (event) => {
        this.isPlaying = false;
        this.isPaused = false;
        this.currentUtterance = null;
        const error = new Error(`Speech synthesis error: ${event.error}`);
        this.errorCallback?.(error);
        reject(error);
      };

      this.currentUtterance.onpause = () => {
        this.isPaused = true;
      };

      this.currentUtterance.onresume = () => {
        this.isPaused = false;
      };

      // Start speaking
      try {
        speechSynthesis.speak(this.currentUtterance);
      } catch (error) {
        this.currentUtterance = null;
        reject(error);
      }
    });
  }

  stop(): void {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
    }
    this.isPlaying = false;
    this.isPaused = false;
    this.currentUtterance = null;
  }

  pause(): void {
    if ('speechSynthesis' in window && this.isPlaying && !this.isPaused) {
      speechSynthesis.pause();
      this.isPaused = true;
    }
  }

  resume(): void {
    if ('speechSynthesis' in window && this.isPaused) {
      speechSynthesis.resume();
      this.isPaused = false;
    }
  }

  async getVoices(): Promise<TTSVoice[]> {
    if (!('speechSynthesis' in window)) {
      return [];
    }

    return new Promise((resolve) => {
      let voices = speechSynthesis.getVoices();
      
      if (voices.length === 0) {
        // Voices might not be loaded yet
        speechSynthesis.onvoiceschanged = () => {
          voices = speechSynthesis.getVoices();
          resolve(this.mapSystemVoices(voices));
        };
      } else {
        resolve(this.mapSystemVoices(voices));
      }
    });
  }

  private mapSystemVoices(systemVoices: SpeechSynthesisVoice[]): TTSVoice[] {
    return systemVoices.map(voice => ({
      id: voice.voiceURI,
      name: voice.name,
      lang: voice.lang,
      gender: this.inferGender(voice.name),
    }));
  }

  private inferGender(voiceName: string): 'male' | 'female' | 'neutral' {
    const name = voiceName.toLowerCase();
    
    // Common patterns for inferring gender from voice names
    const femalePatterns = ['female', 'woman', 'girl', 'aria', 'zira', 'hazel', 'susan', 'karen', 'samantha'];
    const malePatterns = ['male', 'man', 'boy', 'david', 'mark', 'daniel', 'alex', 'tom'];
    
    if (femalePatterns.some(pattern => name.includes(pattern))) {
      return 'female';
    }
    
    if (malePatterns.some(pattern => name.includes(pattern))) {
      return 'male';
    }
    
    return 'neutral';
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