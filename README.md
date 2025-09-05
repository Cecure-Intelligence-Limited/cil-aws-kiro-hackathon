# Aura Desktop Assistant

[![CI](https://github.com/your-username/aura-desktop-assistant/workflows/Continuous%20Integration/badge.svg)](https://github.com/your-username/aura-desktop-assistant/actions/workflows/ci.yml)
[![CD](https://github.com/your-username/aura-desktop-assistant/workflows/Continuous%20Deployment/badge.svg)](https://github.com/your-username/aura-desktop-assistant/actions/workflows/cd.yml)
[![Security](https://github.com/your-username/aura-desktop-assistant/workflows/Security%20Scanning/badge.svg)](https://github.com/your-username/aura-desktop-assistant/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/your-username/aura-desktop-assistant/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/aura-desktop-assistant)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A privacy-focused, voice-first desktop assistant built with Electron, React, and FastAPI. Aura provides intelligent file operations, spreadsheet analysis, document AI capabilities, and seamless voice interaction with text fallback options.

## ✨ Features

- **Global Hotkey**: Press `Ctrl+'` to toggle the assistant overlay
- **Voice Interface**: Click the microphone button for voice input
- **Visual Workflow**: Step badges showing Capture → Parse → Execute → Respond states
- **Configurable Providers**: Choose between Vosk (offline) or Whisper for STT, multiple TTS options
- **Modern UI**: Semi-transparent overlay with rounded corners and backdrop blur
- **Always Available**: Stays on top and accessible from any application

## 🚀 Quick Start

### 🎯 One-Command Desktop Demo (Recommended for Judges!)

**Complete desktop application setup and demo:**

```bash
# Windows - Full Desktop Experience
SETUP-FOR-JUDGES.bat

# Alternative: Direct demo launch
local-test\desktop-demo-complete.bat
```

This launches a **complete desktop application** with voice activation, AI file management, and professional UX.

### 🌐 Cloud Testing (No Installation Required!)

**For hackathon judges and remote evaluation:**

[![Open in Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/your-username/aura-desktop-assistant/codespaces)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/your-username/aura-desktop-assistant)

**Or try the live demo:** [https://aura-demo.your-domain.com](https://aura-demo.your-domain.com)

See [CLOUD-TESTING.md](CLOUD-TESTING.md) for comprehensive cloud testing options.

### 📋 Manual Setup

**Prerequisites:**
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://python.org/) (3.9+)
- [Rust](https://rustup.rs/) (for native desktop app)

**Installation:**
1. **Clone and setup**
   ```bash
   git clone https://github.com/your-username/aura-desktop-assistant.git
   cd aura-desktop-assistant
   npm install
   ```

2. **Quick test**
   ```bash
   # Run comprehensive test suite
   ./local-test/run-all-tests.sh  # macOS/Linux
   local-test\run-all-tests.bat   # Windows
   ```

3. **Start development**
   ```bash
   # Backend
   cd backend && python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt && python main.py

   # Frontend (new terminal)
   npm run tauri:dev  # Native app
   # OR
   npm run dev        # Web version
   ```

## 🎯 Usage

1. **Activate**: Press `Ctrl+'` to show/hide the assistant overlay
2. **Voice Input**: Click the microphone button to start voice recording
3. **Text Input**: Type directly in the input field
4. **Settings**: Click the gear icon to configure STT/TTS providers
5. **Monitor Progress**: Watch the step badges for real-time workflow status

## ⚙️ Configuration

### Speech-to-Text Providers
- **Whisper** (Cloud): OpenAI's Whisper API for high accuracy
- **Vosk** (Offline): Local speech recognition for privacy

### Text-to-Speech Providers
- **System TTS**: Built-in operating system voice
- **ElevenLabs**: High-quality AI voice synthesis
- **OpenAI TTS**: OpenAI's text-to-speech API

### Settings Access
Click the gear icon (⚙️) in the overlay to open the settings modal.

## 🏗️ Architecture

### Frontend (React + TypeScript)
- **Components**: Modular React components with TypeScript
- **State Management**: XState for complex workflow orchestration
- **Styling**: Tailwind CSS with custom animations
- **Build Tool**: Vite for fast development and optimized builds

### Backend (Tauri + Rust)
- **Global Shortcuts**: System-wide hotkey registration
- **Window Management**: Transparent, always-on-top overlay
- **Native Integration**: Access to system APIs and resources

### State Machine (XState)
```
idle → capture → parse → execute → respond → idle
```

## 📁 Project Structure

```
├── local-setup/              # 🚀 One-click setup & demo
│   ├── setup-and-demo.bat   # Windows setup script
│   ├── setup-and-demo.sh    # macOS/Linux setup script
│   ├── WOW-TEST.md          # Ultimate demo experience
│   ├── SHOWCASE.md          # Hackathon presentation guide
│   └── troubleshooting/     # Common issues & fixes
├── src/                     # Frontend React application
│   ├── components/          # UI components
│   ├── machines/           # XState state machines
│   ├── services/           # API and business logic
│   └── adapters/           # STT/TTS provider adapters
├── backend/                # Python FastAPI backend
│   ├── services/           # Core business services
│   ├── utils/             # Utilities and helpers
│   └── tests/             # Backend test suite
├── src-tauri/             # Tauri desktop application
│   ├── src/main.rs        # Rust application entry
│   └── tauri.conf.json    # Desktop app configuration
└── scripts/               # Development and testing scripts
```

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start Vite development server
- `npm run build` - Build React app for production
- `npm run tauri:dev` - Run Tauri in development mode
- `npm run tauri:build` - Build Tauri application

### Development Workflow

1. **Frontend Development**: Use `npm run dev` for React-only development
2. **Full Stack Development**: Use `npm run tauri:dev` for complete app testing
3. **Production Build**: Use `npm run tauri:build` to create distributable packages

## 🎨 Customization

### Tailwind Configuration
Modify `tailwind.config.js` to customize:
- Colors and themes
- Animations and transitions
- Responsive breakpoints
- Custom utilities

### Window Behavior
Edit `src-tauri/tauri.conf.json` to adjust:
- Window size and position
- Transparency settings
- Security permissions
- Global shortcut keys

## 🧪 Testing

### Comprehensive Test Suite
```bash
# Run complete test suite (recommended)
./local-test/run-all-tests.sh     # macOS/Linux
local-test\run-all-tests.bat      # Windows

# Individual test categories
python local-test/test-backend.py      # Backend API tests
python local-test/test-integration.py  # End-to-end workflows
python local-test/test-performance.py  # Performance benchmarks
python local-test/test-security.py     # Security validation
npm test                               # Frontend component tests
```

### Cloud Testing
```bash
# No installation required - test in browser
# See CLOUD-TESTING.md for complete guide
```

### Demo Testing
```bash
# Complete setup and demo experience
./local-test/setup-and-test.sh    # macOS/Linux
local-test\setup-and-test.bat     # Windows
```

## 🔒 Security

Aura prioritizes security and privacy:

- **Local-First**: Voice processing happens locally by default
- **Encrypted Storage**: All sensitive data encrypted with AES-256
- **Input Validation**: Comprehensive sanitization and validation
- **Dependency Scanning**: Automated vulnerability detection
- **Security Audits**: Regular penetration testing and code analysis

Report security issues to: security@aura-assistant.com

## 📊 CI/CD Pipeline

Our professional-grade CI/CD pipeline ensures code quality and security:

### Continuous Integration (`ci.yml`)
- **Code Quality**: ESLint, Prettier, TypeScript checking
- **Testing**: Unit, integration, and E2E tests
- **Security**: SAST scanning, dependency auditing
- **Cross-Platform**: Windows and Linux build verification

### Continuous Deployment (`cd.yml`)
- **Multi-Platform Builds**: Automated builds for all supported platforms
- **Release Management**: Automated changelog and GitHub releases
- **Deployment**: Staging and production deployment automation
- **Monitoring**: Post-deployment health checks

### Security Scanning (`security.yml`)
- **Weekly Scans**: Automated vulnerability assessments
- **CodeQL Analysis**: Static code analysis for security issues
- **Secret Scanning**: Detection of exposed credentials
- **Container Security**: Docker image vulnerability scanning

### Release Management (`release.yml`)
- **Version Bumping**: Automated semantic versioning
- **Changelog Generation**: Conventional commits to changelog
- **Release PRs**: Automated release preparation
- **Quality Gates**: Comprehensive validation before release

## 🔧 Troubleshooting

### Common Issues

**Global shortcut not working**
- Ensure no other application is using `Ctrl+'`
- Check system permissions for global shortcuts

**Window not appearing**
- Verify Tauri permissions in system settings
- Check if window is hidden behind other applications

**Voice input not working**
- Ensure microphone permissions are granted
- Check selected STT provider configuration

**CI/CD Issues**
- Check GitHub Actions logs for detailed error information
- Ensure all required secrets are configured in repository settings
- Verify branch protection rules are properly configured

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [Tauri](https://tauri.app/) - Cross-platform desktop app framework
- [XState](https://xstate.js.org/) - State machine library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [React](https://reactjs.org/) - UI library