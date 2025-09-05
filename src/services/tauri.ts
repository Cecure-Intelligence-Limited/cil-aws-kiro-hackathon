/**
 * Tauri integration service
 * Provides safe access to Tauri APIs with fallbacks
 */

// Check if we're running in Tauri
export const isTauri = typeof window !== 'undefined' && (window as any).__TAURI__;

// Tauri API imports with error handling
// let _tauriApi: any = null;
let tauriInvoke: any = null;
let tauriWindow: any = null;
let tauriGlobalShortcut: any = null;

if (isTauri) {
  try {
    import('@tauri-apps/api/tauri').then(api => {
      // _tauriApi = api;
      tauriInvoke = api.invoke;
    }).catch(console.warn);
    
    import('@tauri-apps/api/window').then(api => {
      tauriWindow = api;
    }).catch(console.warn);
    
    import('@tauri-apps/plugin-global-shortcut').then(api => {
      tauriGlobalShortcut = api;
    }).catch(console.warn);
  } catch (error) {
    console.warn('Failed to load Tauri APIs:', error);
  }
}

export class TauriService {
  /**
   * Check if running in Tauri environment
   */
  static isTauri(): boolean {
    return isTauri;
  }

  /**
   * Invoke Tauri command safely
   */
  static async invoke<T = any>(command: string, args?: Record<string, any>): Promise<T | null> {
    if (!isTauri || !tauriInvoke) {
      console.warn(`Tauri invoke not available: ${command}`);
      return null;
    }

    try {
      return await tauriInvoke(command, args);
    } catch (error) {
      console.error(`Tauri invoke failed: ${command}`, error);
      throw error;
    }
  }

  /**
   * Toggle window visibility
   */
  static async toggleWindow(): Promise<void> {
    try {
      await this.invoke('toggle_window');
    } catch (error) {
      console.error('Failed to toggle window:', error);
    }
  }

  /**
   * Show window
   */
  static async showWindow(): Promise<void> {
    try {
      await this.invoke('show_window');
    } catch (error) {
      console.error('Failed to show window:', error);
    }
  }

  /**
   * Hide window
   */
  static async hideWindow(): Promise<void> {
    try {
      await this.invoke('hide_window');
    } catch (error) {
      console.error('Failed to hide window:', error);
    }
  }

  /**
   * Get system information
   */
  static async getSystemInfo(): Promise<any> {
    try {
      return await this.invoke('get_system_info') || {
        platform: 'unknown',
        arch: 'unknown',
        version: '1.0.0',
        name: 'aura-desktop-assistant'
      };
    } catch (error) {
      console.error('Failed to get system info:', error);
      return {
        platform: navigator.platform || 'unknown',
        userAgent: navigator.userAgent,
        language: navigator.language,
      };
    }
  }

  /**
   * Check if file exists
   */
  static async fileExists(path: string): Promise<boolean> {
    try {
      return await this.invoke('file_exists', { path }) || false;
    } catch (error) {
      console.error('Failed to check file existence:', error);
      return false;
    }
  }

  /**
   * Get app data directory
   */
  static async getAppDataDir(): Promise<string | null> {
    try {
      return await this.invoke('get_app_data_dir');
    } catch (error) {
      console.error('Failed to get app data dir:', error);
      return null;
    }
  }

  /**
   * Get documents directory
   */
  static async getDocumentsDir(): Promise<string | null> {
    try {
      return await this.invoke('get_documents_dir');
    } catch (error) {
      console.error('Failed to get documents dir:', error);
      return null;
    }
  }

  /**
   * Listen to window events
   */
  static onWindowEvent(event: string, callback: (data: any) => void): () => void {
    if (!isTauri || !tauriWindow) {
      console.warn('Window events not available outside Tauri');
      return () => {};
    }

    try {
      const unlisten = tauriWindow.appWindow.listen(event, callback);
      return unlisten;
    } catch (error) {
      console.error('Failed to listen to window event:', error);
      return () => {};
    }
  }

  /**
   * Emit window event
   */
  static async emitWindowEvent(event: string, data?: any): Promise<void> {
    if (!isTauri || !tauriWindow) {
      console.warn('Window events not available outside Tauri');
      return;
    }

    try {
      await tauriWindow.appWindow.emit(event, data);
    } catch (error) {
      console.error('Failed to emit window event:', error);
    }
  }

  /**
   * Set window always on top
   */
  static async setAlwaysOnTop(alwaysOnTop: boolean): Promise<void> {
    if (!isTauri || !tauriWindow) {
      console.warn('Window management not available outside Tauri');
      return;
    }

    try {
      await tauriWindow.appWindow.setAlwaysOnTop(alwaysOnTop);
    } catch (error) {
      console.error('Failed to set always on top:', error);
    }
  }

  /**
   * Set window focus
   */
  static async setFocus(): Promise<void> {
    if (!isTauri || !tauriWindow) {
      console.warn('Window management not available outside Tauri');
      return;
    }

    try {
      await tauriWindow.appWindow.setFocus();
    } catch (error) {
      console.error('Failed to set focus:', error);
    }
  }

  /**
   * Get current window
   */
  static getCurrentWindow(): any {
    if (!isTauri || !tauriWindow) {
      return null;
    }
    return tauriWindow.appWindow;
  }
}

// Global shortcut handling
export class GlobalShortcutService {
  private static shortcuts: Map<string, () => void> = new Map();

  /**
   * Register global shortcut
   */
  static async register(shortcut: string, callback: () => void): Promise<boolean> {
    if (!isTauri || !tauriGlobalShortcut) {
      console.warn('Global shortcuts not available outside Tauri');
      return false;
    }

    try {
      await tauriGlobalShortcut.register(shortcut, callback);
      this.shortcuts.set(shortcut, callback);
      return true;
    } catch (error) {
      console.error(`Failed to register shortcut ${shortcut}:`, error);
      return false;
    }
  }

  /**
   * Unregister global shortcut
   */
  static async unregister(shortcut: string): Promise<boolean> {
    if (!isTauri || !tauriGlobalShortcut) {
      return false;
    }

    try {
      await tauriGlobalShortcut.unregister(shortcut);
      this.shortcuts.delete(shortcut);
      return true;
    } catch (error) {
      console.error(`Failed to unregister shortcut ${shortcut}:`, error);
      return false;
    }
  }

  /**
   * Unregister all shortcuts
   */
  static async unregisterAll(): Promise<void> {
    if (!isTauri || !tauriGlobalShortcut) {
      return;
    }

    try {
      await tauriGlobalShortcut.unregisterAll();
      this.shortcuts.clear();
    } catch (error) {
      console.error('Failed to unregister all shortcuts:', error);
    }
  }

  /**
   * Get registered shortcuts
   */
  static getRegisteredShortcuts(): string[] {
    return Array.from(this.shortcuts.keys());
  }
}