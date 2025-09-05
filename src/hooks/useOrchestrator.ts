import { useMachine } from '@xstate/react';
import { useCallback, useEffect } from 'react';
import { orchestratorMachine } from '../machines/assistantMachine';
import { AssistantState, Settings, Intent, ExecutionResult, EffectHandlers } from '../types';
import { useAdapters } from '../adapters/hooks';
import { AdapterConfig } from '../adapters/types';

export interface OrchestratorSelectors {
  // State selectors
  currentState: AssistantState;
  isVisible: boolean;
  isRecording: boolean;
  isProcessing: boolean;
  
  // Data selectors
  input: string;
  result: string;
  error: string | null;
  intent: Intent | null;
  settings: Settings;
  inputMode: 'text' | 'voice';
  executionResult: ExecutionResult | null;
  
  // Computed selectors
  canSubmitText: boolean;
  canStartVoice: boolean;
  showStepBadges: boolean;
  currentStep: number;
  
  // Adapter status
  sttAvailable: boolean;
  ttsAvailable: boolean;
  sttError: string | null;
  ttsError: string | null;
}

export interface OrchestratorActions {
  // Core actions
  toggleVisibility: () => void;
  submitText: (text: string) => void;
  startCapture: () => void;
  cancel: () => void;
  
  // Settings
  updateSettings: (settings: Settings) => void;
  
  // Verification actions
  confirmExecution: () => void;
  cancelExecution: () => void;
  
  // Manual event triggers (for testing/debugging)
  triggerSTTResult: (text: string) => void;
  triggerIntentParsed: (intent: Intent) => void;
  triggerExecutionResult: (result: ExecutionResult) => void;
}

export interface UseOrchestratorReturn {
  // State and data
  selectors: OrchestratorSelectors;
  
  // Actions
  actions: OrchestratorActions;
  
  // Control
  start: () => void;
  stop: () => void;
  
  // Raw machine access (for advanced use cases)
  state: any;
  send: any;
  
  // Adapters (for advanced use cases)
  adapters: any;
}

const stepOrder: AssistantState[] = ['idle', 'capture', 'parseIntent', 'route', 'execute', 'verify', 'respond', 'recover'];

export const useOrchestrator = (_effectHandlers?: Partial<EffectHandlers>): UseOrchestratorReturn => {
  // Convert settings to adapter config
  const getAdapterConfig = useCallback((settings: Settings): AdapterConfig => ({
    sttProvider: settings.sttProvider === 'whisper' ? 'whisper' : settings.sttProvider === 'vosk' ? 'vosk' : 'none',
    ttsProvider: settings.ttsProvider === 'system' ? 'system' : 
                 settings.ttsProvider === 'elevenlabs' ? 'edge' : 
                 settings.ttsProvider === 'openai' ? 'openai' : 'none',
    apiKeys: {
      openai: process.env.REACT_APP_OPENAI_API_KEY,
      whisper: process.env.REACT_APP_OPENAI_API_KEY,
    },
  }), []);

  const [state, send, service] = useMachine(orchestratorMachine);

  // Initialize adapters based on current settings
  const adapterConfig = getAdapterConfig(state.context.settings);
  const adapters = useAdapters(adapterConfig);

  const currentState = state.value as AssistantState;
  const context = state.context;

  // Selectors
  const selectors: OrchestratorSelectors = {
    // State selectors
    currentState,
    isVisible: context.isVisible,
    isRecording: context.isRecording,
    isProcessing: ['parseIntent', 'route', 'execute', 'verify', 'respond'].includes(currentState),
    
    // Data selectors
    input: context.input,
    result: context.result,
    error: context.error,
    intent: context.intent,
    settings: context.settings,
    inputMode: context.inputMode,
    executionResult: context.executionResult,
    
    // Computed selectors
    canSubmitText: currentState === 'idle' && context.isVisible,
    canStartVoice: currentState === 'idle' && context.isVisible && context.settings.sttProvider !== 'none',
    showStepBadges: currentState !== 'idle',
    currentStep: stepOrder.indexOf(currentState),
    sttAvailable: adapters.stt.isAvailable,
    ttsAvailable: adapters.tts.isAvailable,
    sttError: null, // TODO: implement proper STT error tracking
    ttsError: null, // TODO: implement proper TTS error tracking
  };

  // Actions
  const actions: OrchestratorActions = {
    // Core actions
    toggleVisibility: useCallback(() => {
      send({ type: 'HOTKEY_TOGGLE' });
    }, [send]),
    
    submitText: useCallback((text: string) => {
      send({ type: 'TEXT_SUBMIT', text });
    }, [send]),
    
    startCapture: useCallback(async () => {
      if (adapters.stt.isAvailable) {
        try {
          await adapters.stt.startRecording();
          send({ type: 'START_CAPTURE' });
        } catch (error) {
          console.error('Failed to start STT recording:', error);
        }
      } else {
        send({ type: 'START_CAPTURE' });
      }
    }, [send, adapters.stt]),
    
    cancel: useCallback(async () => {
      if (adapters.stt.isRecording) {
        await adapters.stt.stopRecording();
      }
      if (adapters.tts.isPlaying) {
        adapters.tts.stop();
      }
      send({ type: 'CANCEL' });
    }, [send, adapters.stt, adapters.tts]),
    
    // Settings
    updateSettings: useCallback((settings: Settings) => {
      send({ type: 'UPDATE_SETTINGS', settings });
    }, [send]),
    
    // Verification actions
    confirmExecution: useCallback(() => {
      send({ type: 'VERIFY_OK' });
    }, [send]),
    
    cancelExecution: useCallback(() => {
      send({ type: 'VERIFY_ERR' });
    }, [send]),
    
    // Manual event triggers
    triggerSTTResult: useCallback((text: string) => {
      send({ type: 'STT_RESULT', text });
    }, [send]),
    
    triggerIntentParsed: useCallback((intent: Intent) => {
      send({ type: 'INTENT_PARSED', intent });
    }, [send]),
    
    triggerExecutionResult: useCallback((result: ExecutionResult) => {
      if (result.success) {
        send({ type: 'EXEC_OK', result });
      } else {
        send({ type: 'EXEC_ERR', message: result.message });
      }
    }, [send]),
  };

  // Control functions
  const start = useCallback(() => {
    service.start();
  }, [service]);

  const stop = useCallback(() => {
    service.stop();
  }, [service]);

  // Set up STT result handling
  useEffect(() => {
    if (adapters.stt.isAvailable) {
      adapters.stt.onResult((result) => {
        if (result.isFinal) {
          send({ type: 'STT_RESULT', text: result.text });
        }
        // Partial results could be handled here for real-time feedback
      });

      adapters.stt.onError((error) => {
        console.error('STT Error:', error);
        send({ type: 'CANCEL' });
      });
    }
  }, [adapters.stt.isAvailable, send]);

  // Set up TTS event handling
  useEffect(() => {
    if (adapters.tts.isAvailable) {
      adapters.tts.onStart(() => {
        console.log('TTS started');
      });

      adapters.tts.onEnd(() => {
        console.log('TTS ended');
      });

      adapters.tts.onError((error) => {
        console.error('TTS Error:', error);
      });
    }
  }, [adapters.tts.isAvailable]);

  // Global hotkey effect (would be handled by Tauri in real implementation)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "'") {
        event.preventDefault();
        actions.toggleVisibility();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [actions.toggleVisibility]);

  // Auto-start the service
  useEffect(() => {
    start();
    return () => stop();
  }, [start, stop]);

  return {
    selectors: {
      ...selectors,
      // Add adapter status to selectors
      sttAvailable: adapters.stt.isAvailable,
      ttsAvailable: adapters.tts.isAvailable,
      sttError: adapters.stt.error,
      ttsError: adapters.tts.error,
    },
    actions,
    start,
    stop,
    state,
    send,
    // Expose adapters for advanced use cases
    adapters,
  };
};

// Utility hook for effect handlers
export const useEffectHandlers = (): EffectHandlers => {
  const speak = useCallback(async (text: string) => {
    // This will be handled by the TTS adapter in the orchestrator
    console.log('TTS request:', text);
  }, []);

  const postJSON = useCallback(async (path: string, body: Record<string, any>) => {
    const { postJSON: apiPostJSON } = await import('../services/apiClient');
    return apiPostJSON(path, body);
  }, []);

  const showError = useCallback((message: string) => {
    // In a real app, this would show a toast or modal
    console.error('Assistant Error:', message);
    
    // For now, we'll use a simple alert in development
    if (process.env.NODE_ENV === 'development') {
      alert(`Assistant Error: ${message}`);
    }
  }, []);

  return {
    speak,
    postJSON,
    showError,
    startRecording: async () => {
      console.log('Start recording requested');
    },
    stopRecording: async () => {
      console.log('Stop recording requested');
    },
    isRecordingAvailable: async () => false,
    isSpeechAvailable: async () => false,
    getSystemInfo: async () => ({}),
    isBackendAvailable: async () => false,
    showNotification: (title: string, message: string) => {
      console.log(`Notification: ${title} - ${message}`);
    },
    requestNotificationPermission: async () => false,
  };
};