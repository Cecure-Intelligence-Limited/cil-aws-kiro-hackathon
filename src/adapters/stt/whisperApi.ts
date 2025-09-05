import { STTAdapter, STTResult } from '../types';

export class WhisperApiSTT implements STTAdapter {
  name = 'whisper-api';
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private resultCallback: ((result: STTResult) => void) | null = null;
  private errorCallback: ((error: Error) => void) | null = null;
  private apiKey: string;
  private isRecording = false;

  constructor(apiKey: string) {
    this.apiKey = apiKey;
  }

  async isAvailable(): Promise<boolean> {
    try {
      // Check if we have microphone access and API key
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return !!this.apiKey;
    } catch {
      return false;
    }
  }

  async startRecording(): Promise<void> {
    if (this.isRecording) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });

      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.audioChunks = [];
      this.isRecording = true;

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.onstop = async () => {
        await this.processAudio();
        this.cleanup();
      };

      this.mediaRecorder.onerror = (event) => {
        this.errorCallback?.(new Error(`Recording error: ${event.error}`));
      };

      // Start recording with 1-second chunks for partial results
      this.mediaRecorder.start(1000);

      // Send partial results every few seconds
      this.startPartialProcessing();

    } catch (error) {
      this.errorCallback?.(error as Error);
    }
  }

  async stopRecording(): Promise<void> {
    if (!this.isRecording || !this.mediaRecorder) return;

    this.isRecording = false;
    this.mediaRecorder.stop();
    
    // Stop all tracks
    this.mediaRecorder.stream?.getTracks().forEach(track => track.stop());
  }

  private startPartialProcessing() {
    // For Whisper API, we'll send chunks every 3 seconds for partial results
    const partialInterval = setInterval(async () => {
      if (!this.isRecording) {
        clearInterval(partialInterval);
        return;
      }

      if (this.audioChunks.length > 0) {
        const partialBlob = new Blob(this.audioChunks.slice(-3), { type: 'audio/webm' });
        await this.sendToWhisper(partialBlob, false);
      }
    }, 3000);
  }

  private async processAudio(): Promise<void> {
    if (this.audioChunks.length === 0) return;

    const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
    await this.sendToWhisper(audioBlob, true);
  }

  private async sendToWhisper(audioBlob: Blob, isFinal: boolean): Promise<void> {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.webm');
      formData.append('model', 'whisper-1');
      formData.append('language', 'en');
      formData.append('response_format', 'json');

      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Whisper API error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      
      if (result.text && result.text.trim()) {
        this.resultCallback?.({
          text: result.text.trim(),
          isFinal,
          confidence: 0.9, // Whisper doesn't provide confidence, assume high
          timestamp: Date.now(),
        });
      }
    } catch (error) {
      this.errorCallback?.(error as Error);
    }
  }

  onResult(callback: (result: STTResult) => void): void {
    this.resultCallback = callback;
  }

  onError(callback: (error: Error) => void): void {
    this.errorCallback = callback;
  }

  cleanup(): void {
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.resultCallback = null;
    this.errorCallback = null;
  }
}