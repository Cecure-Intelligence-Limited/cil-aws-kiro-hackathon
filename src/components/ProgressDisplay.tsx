import React from 'react';
import { ActionProgress } from '../types';

interface ProgressDisplayProps {
  progress: ActionProgress;
  className?: string;
}

export const ProgressDisplay: React.FC<ProgressDisplayProps> = ({ progress, className = '' }) => {
  const getPhaseColor = (phase: ActionProgress['phase']) => {
    switch (phase) {
      case 'starting':
        return 'text-blue-400';
      case 'processing':
        return 'text-yellow-400';
      case 'completing':
        return 'text-green-400';
      case 'complete':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getPhaseIcon = (phase: ActionProgress['phase']) => {
    switch (phase) {
      case 'starting':
        return '🚀';
      case 'processing':
        return '⚙️';
      case 'completing':
        return '✨';
      case 'complete':
        return '✅';
      case 'error':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getProgressBarColor = (phase: ActionProgress['phase']) => {
    switch (phase) {
      case 'starting':
        return 'bg-blue-500';
      case 'processing':
        return 'bg-yellow-500';
      case 'completing':
        return 'bg-green-500';
      case 'complete':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-center space-x-3 mb-3">
        <span className="text-lg">{getPhaseIcon(progress.phase)}</span>
        <div className="flex-1">
          <div className={`text-sm font-medium ${getPhaseColor(progress.phase)}`}>
            {progress.message}
          </div>
          {progress.details && (
            <div className="text-xs text-gray-400 mt-1">
              {typeof progress.details === 'string' 
                ? progress.details 
                : JSON.stringify(progress.details, null, 2)}
            </div>
          )}
        </div>
        <div className="text-xs text-gray-400 font-mono">
          {Math.round(progress.progress)}%
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(progress.phase)}`}
          style={{ width: `${Math.max(0, Math.min(100, progress.progress))}%` }}
        />
      </div>
      
      {/* Phase Indicator */}
      <div className="flex justify-between text-xs text-gray-500 mt-2">
        <span className={progress.phase === 'starting' ? getPhaseColor('starting') : ''}>
          Start
        </span>
        <span className={progress.phase === 'processing' ? getPhaseColor('processing') : ''}>
          Process
        </span>
        <span className={progress.phase === 'completing' ? getPhaseColor('completing') : ''}>
          Complete
        </span>
      </div>
    </div>
  );
};

interface StreamingProgressProps {
  isVisible: boolean;
  progress?: ActionProgress | undefined;
  onCancel?: (() => void) | undefined;
}

export const StreamingProgress: React.FC<StreamingProgressProps> = ({ 
  isVisible, 
  progress, 
  onCancel 
}) => {
  if (!isVisible || !progress) return null;

  return (
    <div className="animate-slide-up">
      <ProgressDisplay progress={progress} />
      
      {/* Cancel Button */}
      {progress.phase === 'processing' && onCancel && (
        <div className="mt-3 flex justify-end">
          <button
            onClick={onCancel}
            className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm transition-colors"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
};

interface ProgressHistoryProps {
  progressHistory: ActionProgress[];
  maxItems?: number;
  className?: string;
}

export const ProgressHistory: React.FC<ProgressHistoryProps> = ({ 
  progressHistory, 
  maxItems = 5, 
  className = '' 
}) => {
  const recentProgress = progressHistory.slice(-maxItems);

  if (recentProgress.length === 0) return null;

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="text-xs text-gray-400 font-semibold">Progress History</div>
      {recentProgress.map((progress, index) => (
        <div key={index} className="bg-gray-900 rounded p-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-300">{progress.message}</span>
            <span className="text-xs text-gray-500">{Math.round(progress.progress)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1 mt-1">
            <div 
              className="h-1 rounded-full bg-gray-500"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};