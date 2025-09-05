import React, { useState } from 'react';
import { parseIntent } from '../services/intentParser';
import { ParsedIntent, ParseError } from '../types';

export const IntentParserDemo: React.FC = () => {
  const [input, setInput] = useState('');
  const [result, setResult] = useState<ParsedIntent | ParseError | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testInputs = [
    'Create a file called meeting-notes.txt',
    'Open the budget spreadsheet',
    'Sum the salary column in employees.csv',
    'Summarize the quarterly report in bullet points',
    'Launch VS Code',
    'Calculate average revenue in sales_data.xlsx',
    'Create report.pdf with quarterly data',
    'do something with the thing', // Should fail
  ];

  const handleParse = async () => {
    if (!input.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const parsed = await parseIntent(input.trim());
      setResult(parsed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTestInput = (testInput: string) => {
    setInput(testInput);
    setResult(null);
    setError(null);
  };

  const isParseError = (result: ParsedIntent | ParseError): result is ParseError => {
    return 'error' in result;
  };

  return (
    <div className="fixed top-4 right-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-md max-h-96 overflow-y-auto">
      <div className="text-sm font-semibold mb-3">Intent Parser Demo</div>
      
      {/* Input Section */}
      <div className="mb-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Enter a command to parse..."
          className="w-full p-2 text-xs bg-gray-700 rounded mb-2"
          rows={3}
        />
        
        <button
          onClick={handleParse}
          disabled={!input.trim() || isLoading}
          className="w-full px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-xs"
        >
          {isLoading ? 'Parsing...' : 'Parse Intent'}
        </button>
      </div>

      {/* Test Inputs */}
      <div className="mb-4">
        <div className="text-xs font-semibold mb-2">Test Examples:</div>
        <div className="space-y-1">
          {testInputs.map((testInput, index) => (
            <button
              key={index}
              onClick={() => handleTestInput(testInput)}
              className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs"
            >
              {testInput}
            </button>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-2 bg-red-900 bg-opacity-50 rounded border border-red-600">
          <div className="text-xs text-red-400 font-semibold">Error:</div>
          <div className="text-xs text-white">{error}</div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div className="bg-gray-700 rounded p-3">
          {isParseError(result) ? (
            // Parse Error Display
            <div>
              <div className="text-xs font-semibold text-red-400 mb-2">Parse Error</div>
              <div className="text-xs mb-2">
                <span className="text-red-300">Code:</span> {result.error.code}
              </div>
              <div className="text-xs mb-2">
                <span className="text-red-300">Message:</span> {result.error.message}
              </div>
              
              {result.error.details && (
                <div className="text-xs mb-2">
                  <span className="text-red-300">Details:</span>
                  {result.error.details.confidence && (
                    <div className="ml-2">Confidence: {result.error.details.confidence}</div>
                  )}
                  {result.error.details.missingFields && (
                    <div className="ml-2">Missing: {result.error.details.missingFields.join(', ')}</div>
                  )}
                  {result.error.details.invalidFields && (
                    <div className="ml-2">
                      Invalid: {result.error.details.invalidFields.map(f => f.field).join(', ')}
                    </div>
                  )}
                </div>
              )}
              
              {result.suggestions.length > 0 && (
                <div className="text-xs">
                  <span className="text-yellow-300">Suggestions:</span>
                  {result.suggestions.map((suggestion, index) => (
                    <div key={index} className="ml-2 mt-1">
                      <div className="text-yellow-200">{suggestion.message}</div>
                      {suggestion.example && (
                        <div className="text-gray-300 italic">{suggestion.example}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            // Successful Parse Display
            <div>
              <div className="text-xs font-semibold text-green-400 mb-2">Parsed Intent</div>
              <div className="text-xs mb-1">
                <span className="text-green-300">Intent:</span> {result.intent}
              </div>
              <div className="text-xs mb-1">
                <span className="text-green-300">Confidence:</span> {(result.confidence * 100).toFixed(1)}%
              </div>
              <div className="text-xs mb-2">
                <span className="text-green-300">Parameters:</span>
                <pre className="text-xs bg-gray-800 p-2 rounded mt-1 overflow-x-auto">
                  {JSON.stringify(result.parameters, null, 2)}
                </pre>
              </div>
              {result.context && (
                <div className="text-xs">
                  <span className="text-blue-300">Context:</span>
                  <div className="ml-2">
                    <div>Session: {result.context.sessionId}</div>
                    <div>Time: {new Date(result.context.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* API Key Status */}
      <div className="mt-4 pt-2 border-t border-gray-600 text-xs">
        <div className="text-gray-400">
          API Key: {process.env.REACT_APP_OPENAI_API_KEY ? '✓ Configured' : '✗ Missing'}
        </div>
        {!process.env.REACT_APP_OPENAI_API_KEY && (
          <div className="text-yellow-400 text-xs mt-1">
            Set REACT_APP_OPENAI_API_KEY to test with GPT-4o
          </div>
        )}
      </div>
    </div>
  );
};