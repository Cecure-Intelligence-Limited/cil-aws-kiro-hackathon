// Export all adapter types and interfaces
export * from './types';

// Export individual adapters
export { WhisperApiSTT } from './stt/whisperApi';
export { VoskLocalSTT } from './stt/voskLocal';
export { OpenAITTS } from './tts/openaiTTS';
export { EdgeTTS } from './tts/edgeTTS';
export { SystemTTS } from './tts/systemTTS';

// Export factory
export { AdapterFactory, getSTT, getTTS, clearAdapterCache, getAvailableProviders } from './factory';

// Export utility hooks
export { useSTT, useTTS, useAdapters } from './hooks';