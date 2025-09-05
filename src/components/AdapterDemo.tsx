import React, { useState } from 'react';
import { useAdapters } from '../adapters/hooks';
import { AdapterConfig } from '../adapters/types';

export const AdapterDemo: React.FC = () => {
  const [config, setConfig] = useState<AdapterConfig>({
    sttProvider: 'vosk',
    ttsProvider: 'system',
    apiKeys: {
      openai: process.env.REACT_APP_OPENAI_API_KEY,
    },
  });

  const adapters = useAdapters(config);
  const [testText, setTestText] = useState('Hello, this is a test of the text-to-speech system.');

  const handleSTTProviderChange = (provider: 'whisper' | 'vosk' | 'none') => {
    setConfig(prev => ({ ...prev, sttProvider: provider }));
  };

  const handleTTSProviderChange = (provider: 'openai' | 'edge' | 'system' | 'none') => {
    setConfig(prev => ({ ...prev, ttsProvider: provider }));
  };

  return (
    <div className="fixed top-4 left-4 bg-gray-800 text-white p-4 rounded-lg shadow-lg max-w-sm">
      <div className="text-sm font-semibold mb-3">Adapter Demo</div>
      
      {/* STT Section */}
      <div className="mb-4">
        <div className="text-xs font-semibold mb-2">Speech-to-Text</div>
        <select
          value={config.sttProvider}
          onChange={(e) => handleSTTProviderChange(e.target.value as any)}
          className="w-full p-1 text-xs bg-gray-700 rounded mb-2"
        >
          <option value="none">Disabled</option>
          <option value="vosk">Vosk (Local)</option>
          <option value="whisper">Whisper (API)</option>
        </select>
        
        <div className="text-xs mb-2">
          Status: {adapters.stt.isLoading ? 'Loading...' : 
                   adapters.stt.isAvailable ? '✓ Available' : '✗ Unavailable'}
        </div>
        
        {adapters.stt.error && (
          <div className="text-xs text-red-400 mb-2">Error: {adapters.stt.error}</div>
        )}
        
        <div className="flex space-x-1 mb-2">
          <button
            onClick={adapters.stt.startRecording}
            disabled={!adapters.stt.isAvailable || adapters.stt.isRecording}
            className="flex-1 px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-xs"
          >
            {adapters.stt.isRecording ? 'Recording...' : 'Start'}
          </button>
          <button
            onClick={adapters.stt.stopRecording}
            disabled={!adapters.stt.isRecording}
            className="flex-1 px-2 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-xs"
          >
            Stop
          </button>
        </div>
        
        {adapters.stt.lastResult && (
          <div className="text-xs bg-gray-700 p-2 rounded">
            <div className="text-green-400">
              {adapters.stt.lastResult.isFinal ? 'Final:' : 'Partial:'}
            </div>
            <div>{adapters.stt.lastResult.text}</div>
          </div>
        )}
      </div>

      {/* TTS Section */}
      <div className="mb-4">
        <div className="text-xs font-semibold mb-2">Text-to-Speech</div>
        <select
          value={config.ttsProvider}
          onChange={(e) => handleTTSProviderChange(e.target.value as any)}
          className="w-full p-1 text-xs bg-gray-700 rounded mb-2"
        >
          <option value="none">Disabled</option>
          <option value="system">System TTS</option>
          <option value="edge">Edge TTS</option>
          <option value="openai">OpenAI TTS</option>
        </select>
        
        <div className="text-xs mb-2">
          Status: {adapters.tts.isLoading ? 'Loading...' : 
                   adapters.tts.isAvailable ? '✓ Available' : '✗ Unavailable'}
        </div>
        
        {adapters.tts.error && (
          <div className="text-xs text-red-400 mb-2">Error: {adapters.tts.error}</div>
        )}
        
        <textarea
          value={testText}
          onChange={(e) => setTestText(e.target.value)}
          className="w-full p-2 text-xs bg-gray-700 rounded mb-2"
          rows={3}
          placeholder="Enter text to speak..."
        />
        
        <div className="flex space-x-1 mb-2">
          <button
            onClick={() => adapters.tts.speak(testText)}
            disabled={!adapters.tts.isAvailable || adapters.tts.isPlaying}
            className="flex-1 px-2 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-xs"
          >
            Speak
          </button>
          <button
            onClick={adapters.tts.stop}
            disabled={!adapters.tts.isPlaying}
            className="flex-1 px-2 py-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-xs"
          >
            Stop
          </button>
        </div>
        
        {adapters.tts.isPlaying && (
          <div className="text-xs text-green-400">
            Playing: {adapters.tts.currentText}
          </div>
        )}
      </div>

      {/* Overall Status */}
      <div className="text-xs border-t border-gray-600 pt-2">
        <div>Loading: {adapters.isLoading ? 'Yes' : 'No'}</div>
        <div>Errors: {adapters.hasError ? adapters.errors.join(', ') : 'None'}</div>
        <div>Ready: {adapters.isReady ? 'Yes' : 'No'}</div>
      </div>
    </div>
  );
};