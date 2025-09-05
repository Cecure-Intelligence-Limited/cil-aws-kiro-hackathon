/**
 * Effect handlers for the orchestrator machine
 * Provides concrete implementations for side effects
 */

import { EffectHandlers } from '../types';
import { adapterService } from './adapterService';
import { apiClient } from './apiClient';

export class EffectHandlersImpl implements EffectHandlers {
  
  /**
   * Speak text using configured TTS provider
   */
  async speak(text: string): Promise<void> {
    try {
      const ttsAdapter = adapterService.getTTSAdapter();
      if (ttsAdapter && await ttsAdapter.isAvailable()) {
        await ttsAdapter.speak(text);
      } else {
        console.warn('TTS adapter not available, skipping speech');
      }
    } catch (error) {
      console.error('Failed to speak text:', error);
      // Don't throw - speech is not critical
    }
  }

  /**
   * Make HTTP POST request with JSON body
   */
  async postJSON(path: string, body: Record<string, any>): Promise<any> {
    try {
      return await apiClient.postJSON(path, body);
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Show error message to user
   */
  showError(message: string): void {
    console.error('User Error:', message);
    
    // In a real implementation, this could:
    // - Show a toast notification
    // - Update UI error state
    // - Log to error tracking service
    
    // For now, we'll emit a custom event that the UI can listen to
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('aura-error', {
        detail: { message }
      }));
    }
  }

  /**
   * Start voice recording
   */
  async startRecording(): Promise<void> {
    try {
      const sttAdapter = adapterService.getSTTAdapter();
      if (sttAdapter && await sttAdapter.isAvailable()) {
        await sttAdapter.startRecording();
      } else {
        throw new Error('STT adapter not available');
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
      throw error;
    }
  }

  /**
   * Stop voice recording
   */
  async stopRecording(): Promise<void> {
    try {
      const sttAdapter = adapterService.getSTTAdapter();
      if (sttAdapter) {
        await sttAdapter.stopRecording();
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      throw error;
    }
  }

  /**
   * Check if voice recording is available
   */
  async isRecordingAvailable(): Promise<boolean> {
    try {
      const sttAdapter = adapterService.getSTTAdapter();
      return sttAdapter ? await sttAdapter.isAvailable() : false;
    } catch (error) {
      console.error('Failed to check recording availability:', error);
      return false;
    }
  }

  /**
   * Check if text-to-speech is available
   */
  async isSpeechAvailable(): Promise<boolean> {
    try {
      const ttsAdapter = adapterService.getTTSAdapter();
      return ttsAdapter ? await ttsAdapter.isAvailable() : false;
    } catch (error) {
      console.error('Failed to check speech availability:', error);
      return false;
    }
  }

  /**
   * Get system information
   */
  async getSystemInfo(): Promise<any> {
    try {
      // Try to get Tauri system info if available
      if (typeof window !== 'undefined' && (window as any).__TAURI__) {
        const { invoke } = (window as any).__TAURI__.tauri;
        return await invoke('get_system_info');
      }
      
      // Fallback to browser info
      return {
        platform: navigator.platform,
        userAgent: navigator.userAgent,
        language: navigator.language,
        online: navigator.onLine,
      };
    } catch (error) {
      console.error('Failed to get system info:', error);
      return {};
    }
  }

  /**
   * Check if backend API is available
   */
  async isBackendAvailable(): Promise<boolean> {
    try {
      return await apiClient.healthCheck();
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  }

  /**
   * Show notification to user
   */
  showNotification(title: string, message: string): void {
    try {
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
          body: message,
          icon: '/aura-icon.png',
          tag: 'aura-notification',
        });
      } else {
        // Fallback to console or custom UI notification
        console.log(`Notification: ${title} - ${message}`);
        
        // Emit custom event for UI to handle
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('aura-notification', {
            detail: { title, message }
          }));
        }
      }
    } catch (error) {
      console.error('Failed to show notification:', error);
    }
  }

  /**
   * Request notification permission
   */
  async requestNotificationPermission(): Promise<boolean> {
    try {
      if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
      }
      return false;
    } catch (error) {
      console.error('Failed to request notification permission:', error);
      return false;
    }
  }
}

// Global instance
export const effectHandlers = new EffectHandlersImpl();