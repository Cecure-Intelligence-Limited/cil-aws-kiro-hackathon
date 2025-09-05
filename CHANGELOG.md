# Changelog

All notable changes to the Aura Desktop Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Voice input/output integration with STT/TTS providers
- Intent recognition and command parsing
- File operations (create, open, write)
- Spreadsheet data analysis capabilities
- Document AI processing for PDFs

## [0.1.0] - 2025-01-XX

### Added
- Initial Tauri + React + TypeScript application foundation
- Global hotkey system with Ctrl+' toggle functionality
- Semi-transparent overlay interface with rounded corners and backdrop blur
- Always-on-top, frameless window management
- XState-based state machine for workflow orchestration
- Step badges showing progress through Capture/Parse/Execute/Respond states
- Settings modal with configurable AI providers:
  - STT provider selection (Vosk offline vs Whisper cloud)
  - Cloud NLP toggle option
  - TTS provider selection (System/ElevenLabs/OpenAI)
- Modern UI components built with React and Tailwind CSS:
  - Input field supporting both text and voice input
  - Microphone button with recording state indication
  - Result panel for displaying assistant responses
  - Gear icon for accessing settings
- Custom Tailwind configuration with animations and transitions
- TypeScript definitions for Settings, AssistantState, and Context
- Vite build configuration optimized for Tauri development
- NPM scripts for development and production builds
- Comprehensive project documentation:
  - README.md with setup and usage instructions
  - PROJECT_STRUCTURE.md with detailed architecture overview
  - Updated requirements document with implementation status

### Technical Details
- **Frontend**: React 18.2 + TypeScript 5.2 + Tailwind CSS 3.4
- **Backend**: Tauri 1.6.1 with Rust for native desktop integration
- **State Management**: XState 5.8 for complex workflow orchestration
- **Build Tool**: Vite 5.1 for fast development and optimized builds
- **Window Configuration**: Transparent, resizable: false, 600x400px
- **Security**: Tauri allowlist configured for global shortcuts only

### Development Infrastructure
- PostCSS configuration for Tailwind CSS processing
- TypeScript strict mode configuration
- Separate tsconfig for Node.js compatibility
- Tauri configuration with security-focused allowlist
- Package.json with all necessary dependencies and scripts

### Known Limitations
- Voice input/output not yet implemented (UI ready)
- Intent recognition system not connected (state machine ready)
- File operations not implemented (workflow structure ready)
- Settings persistence not implemented (UI and state management ready)

## Project Initialization

### [0.0.0] - Project Setup
- Repository initialization
- GitHub workflows and templates setup
- Kiro AI assistant specifications and documentation
- Technology assessment and architecture planning