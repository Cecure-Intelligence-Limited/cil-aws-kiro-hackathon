import React, { useState } from 'react';
import { routerActions } from '../services/routerActions';
import { ActionProgress } from '../types';
import { ParsedIntent } from '../types';
import { ProgressDisplay } from './ProgressDisplay';

export const RouterActionsDemo: React.FC = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [currentProgress, setCurrentProgress] = useState<ActionProgress | null>(null);
  const [lastResult, setLastResult] = useState<any>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const testIntents: ParsedIntent[] = [
    {
      intent: 'CreateFile',
      confidence: 0.95,
      parameters: {
        title: 'test-file.txt',
        content: 'Hello from Aura Desktop Assistant!'
      }
    },
    {
      intent: 'OpenItem',
      confidence: 0.9,
      parameters: {
        query: 'test-file.txt',
        type: 'file'
      }
    },
    {
      intent: 'AnalyzeSpreadsheet',
      confidence: 0.85,
      parameters: {
        path: 'sample-data.csv',
        op: 'sum',
        column: 'amount'
      }
    },
    {
      intent: 'SummarizeDoc',
      confidence: 0.8,
      parameters: {
        path: 'sample-document.pdf',
        length: 'bullets'
      }
    }
  ];

  const checkConnection = async () => {
    try {
      const connected = await routerActions.testConnection();
      setIsConnected(connected);
      
      if (connected) {
        const serverInfo = await routerActions.getServerInfo();
        console.log('Server info:', serverInfo);
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      setIsConnected(false);
    }
  };

  const executeIntent = async (intent: ParsedIntent) => {
    if (isExecuting) return;
    
    setIsExecuting(true);
    setCurrentProgress(null);
    setLastResult(null);

    try {
      const result = await routerActions.executeIntent(intent, (progress) => {
        setCurrentProgress(progress);
      });
      
      setLastResult(result);
      
      // Clear progress after a delay
      setTimeout(() => {
        setCurrentProgress(null);
      }, 2000);
      
    } catch (error) {
      console.error('Intent execution failed:', error);
      setLastResult({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
        error: 'Execution failed'
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const getConnectionStatus = () => {
    if (isConnected === null) return { text: 'Unknown', color: 'text-gray-400' };
    if (isConnected) return { text: 'Connected', color: 'text-green-400' };
    return { text: 'Disconnected', color: 'text-red-400' };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="fixed bottom-4 left-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-md max-h-96 overflow-y-auto">
      <div className="text-sm font-semibold mb-3">Router Actions Demo</div>
      
      {/* Connection Status */}
      <div className="mb-4 p-3 bg-gray-900 rounded">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-400">Backend Status:</span>
          <span className={`text-xs font-medium ${connectionStatus.color}`}>
            {connectionStatus.text}
          </span>
        </div>
        <button
          onClick={checkConnection}
          className="w-full px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
        >
          Test Connection
        </button>
      </div>

      {/* Progress Display */}
      {currentProgress && (
        <div className="mb-4">
          <ProgressDisplay progress={currentProgress} />
        </div>
      )}

      {/* Last Result */}
      {lastResult && !currentProgress && (
        <div className="mb-4 p-3 bg-gray-900 rounded">
          <div className="text-xs font-semibold mb-2">
            Last Result: {lastResult.success ? '✅' : '❌'}
          </div>
          <div className="text-xs text-gray-300 mb-1">{lastResult.message}</div>
          {lastResult.data && (
            <pre className="text-xs text-gray-400 bg-gray-800 p-2 rounded mt-2 overflow-x-auto">
              {JSON.stringify(lastResult.data, null, 2)}
            </pre>
          )}
          {lastResult.error && (
            <div className="text-xs text-red-400 mt-1">Error: {lastResult.error}</div>
          )}
        </div>
      )}

      {/* Test Intents */}
      <div className="space-y-2">
        <div className="text-xs font-semibold text-gray-400">Test Actions:</div>
        {testIntents.map((intent, index) => (
          <button
            key={index}
            onClick={() => executeIntent(intent)}
            disabled={isExecuting || !isConnected}
            className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 rounded text-xs transition-colors"
          >
            <div className="font-medium">{intent.intent}</div>
            <div className="text-gray-400 text-xs mt-1">
              {Object.entries(intent.parameters).map(([key, value]) => (
                <span key={key} className="mr-2">
                  {key}: {typeof value === 'string' ? value : JSON.stringify(value)}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>

      {/* API Configuration */}
      <div className="mt-4 pt-3 border-t border-gray-600 text-xs">
        <div className="text-gray-400 mb-1">
          API Base URL: {(routerActions as any)['baseURL'] || 'http://localhost:8000'}
        </div>
        <div className="text-gray-400">
          Status: {isExecuting ? 'Executing...' : 'Ready'}
        </div>
      </div>
    </div>
  );
};