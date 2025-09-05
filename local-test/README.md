# 🚀 Aura Desktop Assistant - Local Testing Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/your-username/aura-desktop-assistant)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org/)

## 📋 Overview

This folder contains everything needed to test Aura Desktop Assistant locally. Aura is a **privacy-first, voice-enabled desktop assistant** that combines cutting-edge AI with local processing to deliver intelligent automation without compromising user privacy.

### 🎯 Key Features
- **🔒 Privacy-First**: All voice processing happens locally by default
- **⚡ Lightning Fast**: Sub-second response times with no network latency
- **🧠 Intelligent**: Natural language understanding for complex tasks
- **🎨 Professional UI**: Modern desktop interface with smooth animations
- **🔧 Extensible**: Plugin architecture through MCP protocol

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://python.org/))
- **Rust** ([Install](https://rustup.rs/)) - For native desktop app

### One-Command Setup

**Windows:**
```bash
.\setup-and-test.bat
```

**macOS/Linux:**
```bash
chmod +x setup-and-test.sh && ./setup-and-test.sh
```

### Manual Setup

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd aura-desktop-assistant
   npm install
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

4. **Run Tests**
   ```bash
   .\run-all-tests.bat  # Windows
   ./run-all-tests.sh   # macOS/Linux
   ```

## 🧪 Testing Scenarios

### Scenario 1: Voice-Powered File Creation
1. **Activate**: Press `Ctrl+'` (or `Cmd+'` on macOS)
2. **Command**: *"Create a meeting notes document titled 'Project Planning' and write 'Aura demonstrates the future of privacy-first AI assistants'"*
3. **Expected**: File created in `documents/` folder with exact content

### Scenario 2: Intelligent Spreadsheet Analysis
1. **Command**: *"Analyze my sample budget spreadsheet and calculate the total income"*
2. **Expected**: Accurate calculation from demo spreadsheet data
3. **Verification**: Check console output for detailed analysis

### Scenario 3: Document AI Processing
1. **Command**: *"Summarize the demo document in three bullet points"*
2. **Expected**: Intelligent summary of project documentation
3. **Verification**: Coherent, relevant bullet points displayed

### Scenario 4: Creative Content Generation
1. **Command**: *"Draft a professional email about project completion"*
2. **Expected**: Well-structured email with appropriate tone
3. **Verification**: Professional language and proper formatting

## 📊 Test Results Validation

### ✅ Success Criteria
- [ ] **Performance**: Voice commands process in < 2 seconds
- [ ] **Accuracy**: Files created with exact specified content
- [ ] **Intelligence**: Spreadsheet calculations are mathematically correct
- [ ] **UI/UX**: Smooth animations and responsive interface
- [ ] **Privacy**: All processing indicators show "LOCAL"

### 📈 Performance Benchmarks
- **Voice Recognition**: < 1 second (local processing)
- **Intent Parsing**: < 500ms
- **File Operations**: < 200ms
- **API Responses**: < 100ms
- **UI Rendering**: 60fps smooth animations

## 🔧 Available Test Scripts

### Core Testing
- `setup-and-test.bat/.sh` - Complete setup and demo launch
- `run-all-tests.bat/.sh` - Execute full test suite
- `quick-demo.bat/.sh` - Fast demo for presentations

### Component Testing
- `test-backend.py` - Backend API validation
- `test-frontend.js` - React component testing
- `test-integration.py` - End-to-end workflow testing
- `test-voice.html` - Voice recognition validation

### Development Tools
- `install-build-tools.bat` - Windows build environment setup
- `check-prerequisites.bat/.sh` - Verify system requirements
- `create-demo-data.py` - Generate realistic test data

## 🎪 Demo Presentation Mode

For hackathon judges and stakeholders:

```bash
.\presentation-demo.bat  # Windows
./presentation-demo.sh   # macOS/Linux
```

This launches a guided demo experience with:
- **Automated setup** and dependency installation
- **Pre-loaded demo data** (realistic spreadsheets, documents)
- **Step-by-step instructions** for impressive voice commands
- **Performance monitoring** and success validation
- **Professional presentation** mode with metrics

## 🐛 Troubleshooting

### Common Issues

**Backend Won't Start**
```bash
# Check Python version
python --version  # Should be 3.9+

# Manual backend start
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py
```

**Frontend Build Errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Voice Recognition Issues**
- Grant microphone permissions in browser/system
- Try different browsers (Chrome recommended)
- Check audio input device in system settings
- Use text input as fallback

**Tauri Build Issues (Windows)**
```bash
# Install Visual Studio Build Tools
.\install-build-tools.bat
# Restart terminal after installation
```

### Platform-Specific Notes

**Windows:**
- Requires Visual Studio Build Tools for Tauri compilation
- Use PowerShell or Command Prompt
- Ensure Windows Defender allows the application

**macOS:**
- May require Xcode Command Line Tools: `xcode-select --install`
- Grant microphone permissions in System Preferences
- Use Terminal or iTerm2

**Linux:**
- Install build essentials: `sudo apt install build-essential`
- May need additional audio libraries: `sudo apt install libasound2-dev`
- Ensure proper permissions for audio devices

## 📚 Additional Resources

### Documentation
- [Main README](../README.md) - Project overview and features
- [API Documentation](../backend/README.md) - Backend API reference
- [Architecture Guide](../ARCHITECTURE.md) - Technical implementation details
- [Security Model](../SECURITY.md) - Privacy and security features

### Development
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute
- [Changelog](../CHANGELOG.md) - Version history and updates
- [Issue Templates](../.github/ISSUE_TEMPLATE/) - Bug reports and feature requests

### Deployment
- [Docker Setup](../backend/Dockerfile) - Containerized deployment
- [CI/CD Pipeline](../.github/workflows/) - Automated testing and deployment
- [Release Process](../RELEASE.md) - Version management and distribution

## 🏆 Competition Highlights

### Technical Excellence
- **Modern Architecture**: Tauri + React + FastAPI + XState
- **Comprehensive Testing**: Unit, integration, and E2E test suites
- **Professional CI/CD**: Automated testing, security scanning, deployment
- **Code Quality**: TypeScript, ESLint, Prettier, comprehensive documentation

### Innovation Factor
- **Privacy-First Design**: Local processing addresses growing privacy concerns
- **Desktop-Native Performance**: Superior to web-based solutions
- **Extensible Architecture**: MCP protocol for unlimited capabilities
- **Real Market Need**: Enterprise-ready alternative to cloud assistants

### Execution Quality
- **Professional Polish**: Enterprise-grade UI/UX and code quality
- **Comprehensive Documentation**: Complete guides for users and developers
- **Security Focus**: Threat modeling, input validation, secure architecture
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility

## 🎯 Success Metrics

After running the tests, you should observe:
- ✅ **Sub-2-second voice processing** with local recognition
- ✅ **Accurate file operations** with exact content matching
- ✅ **Intelligent data analysis** with correct calculations
- ✅ **Professional UI experience** with smooth animations
- ✅ **Privacy indicators** showing local processing throughout

## 📞 Support

For issues or questions:
- **GitHub Issues**: [Report bugs or request features](../../issues)
- **Documentation**: Check the comprehensive guides in the repository
- **Community**: Join discussions in the project repository

---

**🎉 Ready to experience the future of privacy-first desktop assistants?**

**Run the setup script and prepare to be impressed by what you've built!**