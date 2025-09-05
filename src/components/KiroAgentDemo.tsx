import React, { useState } from 'react';
import { kiroAgent, KiroResponse, processUserInput } from '../services/kiroAgent';
import { ActionProgress } from '../types';
import { ProgressDisplay } from './ProgressDisplay';

export const KiroAgentDemo: React.FC = () => {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState<KiroResponse | null>(null);
  const [progress, setProgress] = useState<ActionProgress | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const testInputs = [
    'Create a file called test.txt with hello world content',
    'Open Visual Studio Code',
    'Sum the salary column in employees.csv',
    'Summarize the quarterly report in bullet points',
    'Calculate the average revenue in sales.xlsx',
    'Launch Chrome browser',
    'Make a new document called notes.md',
    'Find key points in research-paper.pdf'
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    setResponse(null);
    setProgress(null);

    try {
      const result = await processUserInput(input.trim(), (progressUpdate) => {
        setProgress(progressUpdate);
      });
      
      setResponse(result);
      
      // Clear progress after completion
      setTimeout(() => {
        setProgress(null);
      }, 2000);
      
    } catch (error) {
      setResponse({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        error_code: 'PROCESSING_ERROR',
        message: 'Failed to process input'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTestInput = (testInput: string) => {
    setInput(testInput);
    setResponse(null);
    setProgress(null);
  };

  const analyzeInput = (inputText: string) => {
    if (!inputText.trim()) return null;
    return kiroAgent.analyzeInput(inputText);
  };

  const analysis = analyzeInput(input);
  const availableTools = kiroAgent.getAvailableTools();

  return (
    <div className="fixed top-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-lg max-h-96 overflow-y-auto">
      <div className="text-sm font-semibold mb-3">Kiro Agent Demo</div>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mb-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter a command for the agent..."
          className="w-full p-2 text-xs bg-gray-700 rounded mb-2"
          rows={3}
          disabled={isProcessing}
        />
        
        <button
          type="submit"
          disabled={!input.trim() || isProcessing}
          className="w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-xs"
        >
          {isProcessing ? 'Processing...' : 'Execute Command'}
        </button>
      </form>

      {/* Input Analysis */}
      {analysis && input.trim() && (
        <div className="mb-4 p-2 bg-gray-900 rounded">
          <div className="text-xs font-semibold text-blue-400 mb-1">Analysis:</div>
          <div className="text-xs">
            <div>Tool: <span className="text-green-400">{analysis.tool}</span></div>
            <div>Confidence: <span className="text-yellow-400">{(analysis.confidence * 100).toFixed(1)}%</span></div>
            <div>Patterns: <span className="text-gray-400">{analysis.matchedPatterns.join(', ')}</span></div>
          </div>
        </div>
      )}

      {/* Progress Display */}
      {progress && (
        <div className="mb-4">
          <ProgressDisplay progress={progress} />
        </div>
      )}

      {/* Response Display */}
      {response && !progress && (
        <div className="mb-4 p-3 bg-gray-900 rounded">
          <div className="flex items-center mb-2">
            <span className="text-lg mr-2">{response.success ? '✅' : '❌'}</span>
            <div className="text-xs font-semibold">
              {response.success ? 'Success' : 'Error'}
              {response.tool && <span className="text-gray-400 ml-1">({response.tool})</span>}
            </div>
          </div>
          
          <div className="text-xs text-gray-300 mb-2">{response.message}</div>
          
          {response.data && (
            <div className="mb-2">
              <div className="text-xs text-blue-400 mb-1">Data:</div>
              <pre className="text-xs text-gray-400 bg-gray-800 p-2 rounded overflow-x-auto">
                {JSON.stringify(response.data, null, 2)}
              </pre>
            </div>
          )}
          
          {response.error && (
            <div className="text-xs text-red-400 mb-2">
              Error: {response.error}
              {response.error_code && <span className="text-gray-500"> ({response.error_code})</span>}
            </div>
          )}
          
          {response.suggestions && response.suggestions.length > 0 && (
            <div className="mb-2">
              <div className="text-xs text-yellow-400 mb-1">Suggestions:</div>
              {response.suggestions.map((suggestion, index) => (
                <div key={index} className="text-xs text-gray-300 mb-1">
                  • {suggestion.message}
                  {suggestion.example && (
                    <div className="text-gray-500 ml-2 italic">{suggestion.example}</div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {response.metadata && (
            <div className="text-xs text-gray-500">
              {response.execution_time && <div>Time: {response.execution_time}ms</div>}
              {response.metadata.confidence && (
                <div>Confidence: {(response.metadata.confidence * 100).toFixed(1)}%</div>
              )}
              {response.metadata.alternative_tools && response.metadata.alternative_tools.length > 0 && (
                <div>Alternatives: {response.metadata.alternative_tools.join(', ')}</div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Test Inputs */}
      <div className="mb-4">
        <div className="text-xs font-semibold mb-2 text-gray-400">Test Commands:</div>
        <div className="space-y-1 max-h-32 overflow-y-auto">
          {testInputs.map((testInput, index) => (
            <button
              key={index}
              onClick={() => handleTestInput(testInput)}
              disabled={isProcessing}
              className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 rounded text-xs transition-colors"
            >
              {testInput}
            </button>
          ))}
        </div>
      </div>

      {/* Available Tools */}
      <div className="border-t border-gray-600 pt-3">
        <div className="text-xs font-semibold mb-2 text-gray-400">Available Tools:</div>
        <div className="space-y-1">
          {availableTools.map((tool) => (
            <div key={tool.name} className="text-xs">
              <span className="text-green-400">{tool.name}</span>
              <span className="text-gray-500 ml-1">- {tool.description}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};