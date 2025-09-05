import { useState, useEffect, useCallback, useRef } from 'react';
import { STTAdapter, TTSAdapter, STTResult, AdapterConfig, TTSOptions } from './types';
import { getSTT, getTTS } from './factory';

// Hook for STT functionality
export const useSTT = (config: AdapterConfig) => {
  const [adapter, setAdapter] = useState<STTAdapter | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<STTResult | null>(null);
  const [partialResults, setPartialResults] = useState<STTResult[]>([]);

  const resultCallbackRef = useRef<((result: STTResult) => void) | null>(null);
  const errorCallbackRef = useRef<((error: Error) => void) | null>(null);

  // Initialize adapter when config changes
  useEffect(() => {
    let mounted = true;

    const initializeAdapter = async () => {
      if (config.sttProvider === 'none') {
        setAdapter(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const newAdapter = await getSTT(config);
        
        if (!mounted) return;

        if (newAdapter) {
          // Set up callbacks
          newAdapter.onResult((result) => {
            if (!mounted) return;
            
            setLastResult(result);
            
            if (result.isFinal) {
              setPartialResults([]);
            } else {
              setPartialResults(prev => [...prev.slice(-4), result]); // Keep last 5 partial results
            }
            
            resultCallbackRef.current?.(result);
          });

          newAdapter.onError((error) => {
            if (!mounted) return;
            
            setError(error.message);
            setIsRecording(false);
            errorCallbackRef.current?.(error);
          });
        }

        setAdapter(newAdapter);
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to initialize STT adapter');
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    initializeAdapter();

    return () => {
      mounted = false;
      adapter?.cleanup();
    };
  }, [config.sttProvider, config.apiKeys?.whisper, config.apiKeys?.openai]);

  const startRecording = useCallback(async () => {
    if (!adapter || isRecording) return;

    try {
      setError(null);
      setPartialResults([]);
      await adapter.startRecording();
      setIsRecording(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start recording');
    }
  }, [adapter, isRecording]);

  const stopRecording = useCallback(async () => {
    if (!adapter || !isRecording) return;

    try {
      await adapter.stopRecording();
      setIsRecording(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop recording');
      setIsRecording(false);
    }
  }, [adapter, isRecording]);

  const onResult = useCallback((callback: (result: STTResult) => void) => {
    resultCallbackRef.current = callback;
  }, []);

  const onError = useCallback((callback: (error: Error) => void) => {
    errorCallbackRef.current = callback;
  }, []);

  return {
    adapter,
    isRecording,
    isLoading,
    error,
    lastResult,
    partialResults,
    startRecording,
    stopRecording,
    onResult,
    onError,
    isAvailable: !!adapter,
  };
};

// Hook for TTS functionality
export const useTTS = (config: AdapterConfig) => {
  const [adapter, setAdapter] = useState<TTSAdapter | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentText, setCurrentText] = useState<string | null>(null);

  const startCallbackRef = useRef<(() => void) | null>(null);
  const endCallbackRef = useRef<(() => void) | null>(null);
  const errorCallbackRef = useRef<((error: Error) => void) | null>(null);

  // Initialize adapter when config changes
  useEffect(() => {
    let mounted = true;

    const initializeAdapter = async () => {
      if (config.ttsProvider === 'none') {
        setAdapter(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const newAdapter = await getTTS(config);
        
        if (!mounted) return;

        if (newAdapter) {
          // Set up callbacks
          newAdapter.onStart?.(() => {
            if (!mounted) return;
            setIsPlaying(true);
            setIsPaused(false);
            startCallbackRef.current?.();
          });

          newAdapter.onEnd?.(() => {
            if (!mounted) return;
            setIsPlaying(false);
            setIsPaused(false);
            setCurrentText(null);
            endCallbackRef.current?.();
          });

          newAdapter.onError?.((error) => {
            if (!mounted) return;
            setError(error.message);
            setIsPlaying(false);
            setIsPaused(false);
            setCurrentText(null);
            errorCallbackRef.current?.(error);
          });
        }

        setAdapter(newAdapter);
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to initialize TTS adapter');
        }
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    initializeAdapter();

    return () => {
      mounted = false;
      adapter?.stop();
    };
  }, [config.ttsProvider, config.apiKeys?.openai, config.voiceSettings]);

  const speak = useCallback(async (text: string, options?: TTSOptions) => {
    if (!adapter) return;

    try {
      setError(null);
      setCurrentText(text);
      await adapter.speak(text, { ...config.voiceSettings, ...options });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to speak text');
      setCurrentText(null);
    }
  }, [adapter, config.voiceSettings]);

  const stop = useCallback(() => {
    if (!adapter) return;
    adapter.stop();
    setIsPlaying(false);
    setIsPaused(false);
    setCurrentText(null);
  }, [adapter]);

  const pause = useCallback(() => {
    if (!adapter || !isPlaying) return;
    adapter.pause();
    setIsPaused(true);
  }, [adapter, isPlaying]);

  const resume = useCallback(() => {
    if (!adapter || !isPaused) return;
    adapter.resume();
    setIsPaused(false);
  }, [adapter, isPaused]);

  const onStart = useCallback((callback: () => void) => {
    startCallbackRef.current = callback;
  }, []);

  const onEnd = useCallback((callback: () => void) => {
    endCallbackRef.current = callback;
  }, []);

  const onError = useCallback((callback: (error: Error) => void) => {
    errorCallbackRef.current = callback;
  }, []);

  return {
    adapter,
    isPlaying,
    isPaused,
    isLoading,
    error,
    currentText,
    speak,
    stop,
    pause,
    resume,
    onStart,
    onEnd,
    onError,
    isAvailable: !!adapter,
  };
};

// Combined hook for both STT and TTS
export const useAdapters = (config: AdapterConfig) => {
  const stt = useSTT(config);
  const tts = useTTS(config);

  const isLoading = stt.isLoading || tts.isLoading;
  const hasError = !!stt.error || !!tts.error;
  const errors = [stt.error, tts.error].filter(Boolean);

  return {
    stt,
    tts,
    isLoading,
    hasError,
    errors,
    isReady: stt.isAvailable || tts.isAvailable,
  };
};