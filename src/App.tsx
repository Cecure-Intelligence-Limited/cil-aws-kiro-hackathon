import React, { useState } from 'react';
import { useOrchestrator, useEffectHandlers } from './hooks/useOrchestrator';
import { useProgressTracking } from './hooks/useProgressTracking';
import { StepBadges } from './components/StepBadge';
import { SettingsModal } from './components/SettingsModal';
import { StreamingProgress, ProgressHistory } from './components/ProgressDisplay';
import { OrchestratorDemo } from './components/OrchestratorDemo';
import { AdapterDemo } from './components/AdapterDemo';
import { IntentParserDemo } from './components/IntentParserDemo';
import { RouterActionsDemo } from './components/RouterActionsDemo';
import { KiroAgentDemo } from './components/KiroAgentDemo';

const App: React.FC = () => {
  const effectHandlers = useEffectHandlers();
  const { selectors, actions } = useOrchestrator(effectHandlers);
  const { progressState, controls, setCancelHandler: _setCancelHandler } = useProgressTracking();
  
  const [showSettings, setShowSettings] = useState(false);
  const [inputText, setInputText] = useState('');
  const [showProgressHistory, setShowProgressHistory] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim()) {
      actions.submitText(inputText.trim());
      setInputText('');
    }
  };

  const handleMicClick = () => {
    if (selectors.isRecording) {
      actions.cancel();
    } else {
      actions.startCapture();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      actions.cancel();
    }
  };

  // Don't render if not visible
  if (!selectors.isVisible) {
    return null;
  }

  return (
    <div className="h-full w-full flex items-center justify-center bg-transparent">
      <div className="bg-black bg-opacity-80 backdrop-blur-sm rounded-2xl p-6 w-full max-w-lg mx-4 shadow-2xl animate-fade-in">
        {/* Header with step badges */}
        <StepBadges 
          currentState={selectors.currentState} 
          showStepBadges={selectors.showStepBadges} 
        />

        {/* Input section */}
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="flex items-center space-x-3">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your command or use voice..."
              disabled={selectors.isProcessing}
              className="flex-1 px-4 py-3 bg-gray-800 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none disabled:opacity-50"
            />
            <button
              type="button"
              onClick={handleMicClick}
              disabled={!selectors.canStartVoice && !selectors.isRecording}
              className={`p-3 rounded-lg transition-all duration-200 ${
                selectors.isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : selectors.canStartVoice
                  ? 'bg-blue-500 hover:bg-blue-600'
                  : 'bg-gray-500 cursor-not-allowed'
              } text-white disabled:opacity-50`}
            >
              🎤
            </button>
            <button
              type="button"
              onClick={() => setShowSettings(true)}
              className="p-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              ⚙️
            </button>
          </div>
        </form>

        {/* Status display */}
        {selectors.isProcessing && (
          <div className="mb-4 p-3 bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">Status:</div>
            <div className="text-white">
              {selectors.currentState === 'capture' && 'Listening...'}
              {selectors.currentState === 'parseIntent' && 'Understanding your request...'}
              {selectors.currentState === 'route' && 'Determining action...'}
              {selectors.currentState === 'execute' && 'Executing command...'}
              {selectors.currentState === 'verify' && 'Waiting for confirmation...'}
              {selectors.currentState === 'respond' && 'Generating response...'}
              {selectors.currentState === 'recover' && 'Handling error...'}
            </div>
          </div>
        )}

        {/* Verification panel */}
        {selectors.currentState === 'verify' && selectors.executionResult && (
          <div className="mb-4 p-4 bg-yellow-900 bg-opacity-50 rounded-lg border border-yellow-600">
            <div className="text-sm text-yellow-400 mb-2">Confirmation Required:</div>
            <div className="text-white text-sm mb-3">{selectors.executionResult.message}</div>
            <div className="flex space-x-2">
              <button
                onClick={actions.confirmExecution}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm"
              >
                Confirm
              </button>
              <button
                onClick={actions.cancelExecution}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md text-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Error display */}
        {selectors.error && (
          <div className="mb-4 p-3 bg-red-900 bg-opacity-50 rounded-lg border border-red-600">
            <div className="text-sm text-red-400 mb-1">Error:</div>
            <div className="text-white text-sm">{selectors.error}</div>
          </div>
        )}

        {/* Progress Display */}
        <StreamingProgress
          isVisible={progressState.isActive}
          progress={progressState.current}
          onCancel={progressState.canCancel ? controls.cancelProgress : undefined}
        />

        {/* Result panel */}
        {(selectors.input || selectors.result) && !progressState.isActive && (
          <div className="bg-gray-800 rounded-lg p-4 animate-slide-up">
            {selectors.input && (
              <div className="mb-3">
                <div className="text-sm text-blue-400 mb-1">Input:</div>
                <div className="text-white text-sm">{selectors.input}</div>
              </div>
            )}
            {selectors.intent && (
              <div className="mb-3">
                <div className="text-sm text-purple-400 mb-1">Intent:</div>
                <div className="text-white text-sm">
                  {selectors.intent.action} (confidence: {Math.round(selectors.intent.confidence * 100)}%)
                </div>
              </div>
            )}
            {selectors.result && (
              <div>
                <div className="text-sm text-green-400 mb-1">Result:</div>
                <div className="text-white text-sm">{selectors.result}</div>
              </div>
            )}
            
            {/* Progress History Toggle */}
            {progressState.history.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-600">
                <button
                  onClick={() => setShowProgressHistory(!showProgressHistory)}
                  className="text-xs text-gray-400 hover:text-gray-300 transition-colors"
                >
                  {showProgressHistory ? 'Hide' : 'Show'} Progress History ({progressState.history.length})
                </button>
                
                {showProgressHistory && (
                  <div className="mt-2">
                    <ProgressHistory 
                      progressHistory={progressState.history}
                      maxItems={5}
                    />
                    <button
                      onClick={controls.clearHistory}
                      className="text-xs text-red-400 hover:text-red-300 mt-2 transition-colors"
                    >
                      Clear History
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Settings display */}
        <div className="mt-4 text-xs text-gray-400 text-center">
          STT: {selectors.settings.sttProvider} | 
          NLP: {selectors.settings.allowCloudNLP ? 'Cloud' : 'Local'} | 
          TTS: {selectors.settings.ttsProvider}
        </div>

        {/* Debug info (development only) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-2 text-xs text-gray-500 text-center">
            State: {selectors.currentState} | Mode: {selectors.inputMode}
          </div>
        )}
      </div>

      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        settings={selectors.settings}
        onSettingsChange={actions.updateSettings}
      />

      {/* Demo components for development */}
      {process.env.NODE_ENV === 'development' && (
        <>
          <OrchestratorDemo />
          <AdapterDemo />
          <IntentParserDemo />
          <RouterActionsDemo />
          <KiroAgentDemo />
        </>
      )}
    </div>
  );
};

export default App;