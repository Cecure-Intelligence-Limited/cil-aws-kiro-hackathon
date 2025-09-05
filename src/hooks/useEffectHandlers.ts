/**
 * Hook for providing effect handlers to the orchestrator
 */

import { useCallback, useMemo } from 'react';
import { EffectHandlers } from '../types';
import { effectHandlers } from '../services/effectHandlers';

export function useEffectHandlers(): EffectHandlers {
  // Wrap effect handlers with useCallback to prevent unnecessary re-renders
  const speak = useCallback(async (text: string) => {
    return effectHandlers.speak(text);
  }, []);

  const postJSON = useCallback(async (path: string, body: Record<string, any>) => {
    return effectHandlers.postJSON(path, body);
  }, []);

  const showError = useCallback((message: string) => {
    effectHandlers.showError(message);
  }, []);

  const startRecording = useCallback(async () => {
    return effectHandlers.startRecording();
  }, []);

  const stopRecording = useCallback(async () => {
    return effectHandlers.stopRecording();
  }, []);

  const isRecordingAvailable = useCallback(async () => {
    return effectHandlers.isRecordingAvailable();
  }, []);

  const isSpeechAvailable = useCallback(async () => {
    return effectHandlers.isSpeechAvailable();
  }, []);

  const getSystemInfo = useCallback(async () => {
    return effectHandlers.getSystemInfo();
  }, []);

  const isBackendAvailable = useCallback(async () => {
    return effectHandlers.isBackendAvailable();
  }, []);

  const showNotification = useCallback((title: string, message: string) => {
    effectHandlers.showNotification(title, message);
  }, []);

  const requestNotificationPermission = useCallback(async () => {
    return effectHandlers.requestNotificationPermission();
  }, []);

  // Memoize the handlers object to prevent unnecessary re-renders
  return useMemo(() => ({
    speak,
    postJSON,
    showError,
    startRecording,
    stopRecording,
    isRecordingAvailable,
    isSpeechAvailable,
    getSystemInfo,
    isBackendAvailable,
    showNotification,
    requestNotificationPermission,
  }), [
    speak,
    postJSON,
    showError,
    startRecording,
    stopRecording,
    isRecordingAvailable,
    isSpeechAvailable,
    getSystemInfo,
    isBackendAvailable,
    showNotification,
    requestNotificationPermission,
  ]);
}