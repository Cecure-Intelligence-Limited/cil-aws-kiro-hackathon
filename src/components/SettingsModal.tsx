import React from 'react';
import { Settings } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: Settings;
  onSettingsChange: (settings: Settings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSettingsChange,
}) => {
  if (!isOpen) return null;

  const handleToggle = (key: keyof Settings, value: any) => {
    onSettingsChange({ ...settings, [key]: value });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96 max-w-md mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Settings</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Speech-to-Text Provider
            </label>
            <select
              value={settings.sttProvider}
              onChange={(e) => handleToggle('sttProvider', e.target.value)}
              className="w-full p-2 border rounded-md"
            >
              <option value="whisper">Whisper (Cloud)</option>
              <option value="vosk">Vosk (Offline)</option>
              <option value="none">Disabled</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Allow Cloud NLP</label>
            <input
              type="checkbox"
              checked={settings.allowCloudNLP}
              onChange={(e) => handleToggle('allowCloudNLP', e.target.checked)}
              className="w-4 h-4"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Text-to-Speech Provider
            </label>
            <select
              value={settings.ttsProvider}
              onChange={(e) => handleToggle('ttsProvider', e.target.value)}
              className="w-full p-2 border rounded-md"
            >
              <option value="system">System TTS</option>
              <option value="elevenlabs">ElevenLabs</option>
              <option value="openai">OpenAI TTS</option>
              <option value="none">Disabled</option>
            </select>
          </div>
        </div>

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};