import { useState, useCallback, useRef } from 'react';
import { ActionProgress } from '../types';

export interface ProgressState {
  isActive: boolean;
  current?: ActionProgress | undefined;
  history: ActionProgress[];
  canCancel: boolean;
}

export interface ProgressControls {
  startProgress: () => void;
  updateProgress: (progress: ActionProgress) => void;
  completeProgress: () => void;
  cancelProgress: () => void;
  clearHistory: () => void;
}

export const useProgressTracking = (maxHistoryItems: number = 10) => {
  const [progressState, setProgressState] = useState<ProgressState>({
    isActive: false,
    current: undefined,
    history: [],
    canCancel: false,
  });

  const cancelRef = useRef<(() => void) | null>(null);

  const startProgress = useCallback(() => {
    setProgressState(prev => ({
      ...prev,
      isActive: true,
      current: undefined,
      canCancel: true,
    }));
  }, []);

  const updateProgress = useCallback((progress: ActionProgress) => {
    setProgressState(prev => {
      const newHistory = [...prev.history];
      
      // Add to history if it's a significant update
      if (progress.phase === 'complete' || progress.phase === 'error' || 
          progress.progress === 100 || progress.progress === 0) {
        newHistory.push(progress);
        
        // Limit history size
        if (newHistory.length > maxHistoryItems) {
          newHistory.shift();
        }
      }

      return {
        ...prev,
        current: progress,
        history: newHistory,
        canCancel: progress.phase === 'processing' || progress.phase === 'starting',
      };
    });
  }, [maxHistoryItems]);

  const completeProgress = useCallback(() => {
    setProgressState(prev => ({
      ...prev,
      isActive: false,
      canCancel: false,
    }));
    cancelRef.current = null;
  }, []);

  const cancelProgress = useCallback(() => {
    if (cancelRef.current) {
      cancelRef.current();
    }
    
    setProgressState(prev => ({
      ...prev,
      isActive: false,
      canCancel: false,
      current: prev.current ? {
        ...prev.current,
        phase: 'error',
        message: 'Operation cancelled by user',
        progress: 0
      } : undefined,
    }));
    
    cancelRef.current = null;
  }, []);

  const clearHistory = useCallback(() => {
    setProgressState(prev => ({
      ...prev,
      history: [],
    }));
  }, []);

  const setCancelHandler = useCallback((handler: () => void) => {
    cancelRef.current = handler;
  }, []);

  const controls: ProgressControls = {
    startProgress,
    updateProgress,
    completeProgress,
    cancelProgress,
    clearHistory,
  };

  return {
    progressState,
    controls,
    setCancelHandler,
  };
};