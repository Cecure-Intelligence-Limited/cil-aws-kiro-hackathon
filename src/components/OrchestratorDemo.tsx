import React from 'react';
import { useOrchestrator, useEffectHandlers } from '../hooks/useOrchestrator';
import { Intent, ExecutionResult } from '../types';

export const OrchestratorDemo: React.FC = () => {
  const effectHandlers = useEffectHandlers();
  const { selectors, actions } = useOrchestrator(effectHandlers);

  const testIntents: Intent[] = [
    {
      action: 'file_create',
      parameters: { filename: 'test.txt', content: 'Hello World' },
      confidence: 0.95,
    },
    {
      action: 'echo',
      parameters: { message: 'This is a test message' },
      confidence: 0.8,
    },
    {
      action: 'unknown',
      parameters: {},
      confidence: 0.3,
    },
  ];

  const testResults: ExecutionResult[] = [
    {
      success: true,
      message: 'File created successfully',
      requiresVerification: true,
    },
    {
      success: true,
      message: 'Echo completed',
      requiresVerification: false,
    },
    {
      success: false,
      message: 'Operation failed',
      requiresVerification: false,
    },
  ];

  if (!selectors.isVisible) {
    return (
      <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg">
        <div className="text-sm mb-2">Press Ctrl+' to show assistant</div>
        <button
          onClick={actions.toggleVisibility}
          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
        >
          Show Assistant
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-sm">
      <div className="text-sm font-semibold mb-3">Orchestrator Demo</div>
      
      <div className="space-y-2 text-xs">
        <div>State: <span className="text-blue-400">{selectors.currentState}</span></div>
        <div>Mode: <span className="text-green-400">{selectors.inputMode}</span></div>
        <div>Recording: <span className="text-yellow-400">{selectors.isRecording ? 'Yes' : 'No'}</span></div>
        <div>Processing: <span className="text-purple-400">{selectors.isProcessing ? 'Yes' : 'No'}</span></div>
      </div>

      <div className="mt-4 space-y-2">
        <div className="text-xs font-semibold">Test Actions:</div>
        
        <div className="grid grid-cols-2 gap-1">
          <button
            onClick={() => actions.triggerSTTResult('Create a new file')}
            disabled={selectors.currentState !== 'capture'}
            className="px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-xs"
          >
            STT Result
          </button>
          
          <button
            onClick={() => testIntents[0] && actions.triggerIntentParsed(testIntents[0])}
            disabled={selectors.currentState !== 'parseIntent'}
            className="px-2 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded text-xs"
          >
            Intent Parsed
          </button>
          
          <button
            onClick={() => testResults[0] && actions.triggerExecutionResult(testResults[0])}
            disabled={selectors.currentState !== 'execute'}
            className="px-2 py-1 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 rounded text-xs"
          >
            Exec Success
          </button>
          
          <button
            onClick={() => testResults[2] && actions.triggerExecutionResult(testResults[2])}
            disabled={selectors.currentState !== 'execute'}
            className="px-2 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-xs"
          >
            Exec Error
          </button>
        </div>

        <div className="flex space-x-1">
          <button
            onClick={actions.confirmExecution}
            disabled={selectors.currentState !== 'verify'}
            className="flex-1 px-2 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-xs"
          >
            Verify OK
          </button>
          
          <button
            onClick={actions.cancelExecution}
            disabled={selectors.currentState !== 'verify'}
            className="flex-1 px-2 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-xs"
          >
            Verify Err
          </button>
        </div>

        <button
          onClick={actions.cancel}
          className="w-full px-2 py-1 bg-gray-600 hover:bg-gray-700 rounded text-xs"
        >
          Cancel
        </button>
      </div>

      <div className="mt-3 pt-2 border-t border-gray-600">
        <div className="text-xs">
          <div>Can Submit Text: {selectors.canSubmitText ? '✓' : '✗'}</div>
          <div>Can Start Voice: {selectors.canStartVoice ? '✓' : '✗'}</div>
          <div>Current Step: {selectors.currentStep}</div>
        </div>
      </div>
    </div>
  );
};