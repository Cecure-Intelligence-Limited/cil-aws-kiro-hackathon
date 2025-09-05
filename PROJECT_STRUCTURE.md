# Aura Desktop Assistant - Project Structure

## Overview
This document outlines the professional project structure for Aura, following industry best practices for cross-platform desktop applications with Tauri + React frontend and FastAPI backend.

## Directory Structure

```
aura-desktop-assistant/
├── .github/                          # GitHub workflows and templates
│   ├── workflows/                    # CI/CD pipeline definitions
│   │   ├── ci.yml                   # Continuous integration
│   │   ├── cd.yml                   # Continuous deployment
│   │   ├── release.yml              # Release automation
│   │   └── security.yml             # Security scanning
│   ├── ISSUE_TEMPLATE/              # Issue templates
│   │   └── bug_report.yml           # Bug report template
│   ├── PULL_REQUEST_TEMPLATE.md     # PR template
│   └── dependabot.yml               # Dependency updates
├── .kiro/                           # Kiro IDE configuration
│   └── specs/                       # Project specifications
│       └── aura-desktop-assistant/  # Spec documents
├── src-tauri/                       # Tauri backend (Rust)
│   ├── src/
│   │   └── main.rs                  # Main app with global shortcut (Ctrl+')
│   ├── Cargo.toml                   # Rust dependencies with global-shortcut
│   └── tauri.conf.json             # Transparent overlay window config
├── src/                             # React frontend with TypeScript
│   ├── components/                  # React components
│   │   ├── StepBadge.tsx           # Progress indicator for assistant states
│   │   └── SettingsModal.tsx        # Configuration modal (STT/TTS providers)
│   ├── machines/                    # XState state machines
│   │   └── assistantMachine.ts      # Main workflow (Capture/Parse/Execute/Respond)
│   ├── App.tsx                      # Main overlay application component
│   ├── main.tsx                     # React entry point
│   ├── types.ts                     # TypeScript definitions (Settings, States)
│   └── styles.css                   # Global styles with Tailwind imports
├── index.html                       # HTML entry point
├── package.json                     # Node.js dependencies (React, XState, Tailwind)
├── tsconfig.json                    # TypeScript configuration
├── tsconfig.node.json               # TypeScript config for Node.js
├── vite.config.ts                   # Vite build configuration for Tauri
├── tailwind.config.js               # Tailwind CSS with custom animations
├── postcss.config.js                # PostCSS configuration
├── PROJECT_STRUCTURE.md             # This file
└── README.md                        # Project documentation
```

## Naming Conventions

### Files and Directories
- **Directories**: `kebab-case` (e.g., `user-interface`, `api-services`)
- **React Components**: `PascalCase` (e.g., `VoiceInput.tsx`, `IntentParser.tsx`)
- **Hooks**: `camelCase` with `use` prefix (e.g., `useVoiceRecognition.ts`)
- **Services**: `camelCase` (e.g., `speechService.ts`, `fileOperations.ts`)
- **Types**: `PascalCase` (e.g., `ParsedIntent.ts`, `VoiceConfig.ts`)
- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `API_ENDPOINTS.ts`)
- **Configuration**: `kebab-case` (e.g., `app-config.json`)

### Code Conventions
- **Variables**: `camelCase`
- **Functions**: `camelCase`
- **Classes**: `PascalCase`
- **Interfaces**: `PascalCase` with `I` prefix (e.g., `IVoiceService`)
- **Types**: `PascalCase` with `T` prefix (e.g., `TIntentType`)
- **Enums**: `PascalCase`
- **Constants**: `SCREAMING_SNAKE_CASE`

### Git Conventions
- **Branches**: `feature/`, `bugfix/`, `hotfix/`, `release/`
- **Commits**: Conventional Commits format
- **Tags**: Semantic versioning (e.g., `v1.0.0`)

## Implementation Details

### Current Architecture
- **Frontend**: React 18 + TypeScript with Tailwind CSS
- **State Management**: XState for complex assistant workflow states
- **Backend**: Tauri (Rust) for native desktop integration
- **Global Shortcuts**: Ctrl+' toggles semi-transparent overlay
- **Window Management**: Always-on-top, transparent, frameless window

### Key Features Implemented
- **Voice Interface**: Microphone button for voice input
- **Visual Feedback**: Step badges showing Capture/Parse/Execute/Respond states
- **Settings Management**: Modal for configuring STT/TTS providers
- **Responsive UI**: Semi-transparent overlay with rounded corners and backdrop blur

### Technology Stack
- **Tauri 1.6.1**: Cross-platform desktop app framework
- **React 18.2**: Frontend UI framework
- **XState 5.8**: State machine library for complex workflows
- **Tailwind CSS 3.4**: Utility-first CSS framework
- **TypeScript 5.2**: Type-safe JavaScript
- **Vite 5.1**: Fast build tool and dev server

### Configuration Files
- `tauri.conf.json`: Window transparency, global shortcuts, security settings
- `tailwind.config.js`: Custom animations, colors, and responsive design
- `tsconfig.json`: Strict TypeScript configuration
- `vite.config.ts`: Tauri-optimized build configuration

### NPM Scripts
- `npm run dev`: Start Vite development server
- `npm run build`: Build for production
- `npm run tauri:dev`: Run Tauri in development mode
- `npm run tauri:build`: Build Tauri application for distribution
#
# Best Practices Implementation

### Code Quality
- ESLint + Prettier for consistent formatting
- Husky for pre-commit hooks
- TypeScript strict mode enabled
- 100% type coverage requirement
- Comprehensive unit test coverage (>90%)
- Conventional commits for consistent history
- Automated code review with CodeQL

### Security
- Dependency vulnerability scanning with Dependabot
- SAST (Static Application Security Testing) with Semgrep
- Secret scanning with TruffleHog
- Container security scanning with Trivy
- Security headers validation
- Input sanitization at all boundaries
- Regular security audits and penetration testing

### Performance
- Bundle size monitoring and budgets
- Performance budgets enforcement
- Lighthouse CI integration for web performance
- Memory leak detection in tests
- Load testing automation
- Performance regression detection

### Documentation
- API documentation with OpenAPI/Swagger
- Architecture Decision Records (ADRs)
- Inline code documentation with JSDoc/rustdoc
- User guides and tutorials
- Deployment runbooks and troubleshooting guides
- Automated documentation generation

### CI/CD Pipeline Structure

#### Why Separate Workflow Files?
1. **Separation of Concerns**: Different workflows have different purposes and triggers
2. **Security**: Production deployments need different secrets than testing
3. **Performance**: Avoid running expensive operations during development
4. **Maintainability**: Easier to debug and modify specific workflows
5. **Permissions**: Different workflows require different GitHub permissions

#### Workflow Files Explained:
- **`ci.yml`**: Continuous Integration - runs on every PR/push
  - Code quality checks (linting, formatting, type checking)
  - Unit and integration tests
  - Security scanning
  - Build verification
  - Cross-platform testing

- **`cd.yml`**: Continuous Deployment - runs on releases/tags
  - Multi-platform builds
  - Release artifact creation
  - Deployment to staging/production
  - Post-deployment monitoring

- **`security.yml`**: Security-focused scans - runs weekly and on main branch
  - Dependency vulnerability scanning
  - CodeQL analysis
  - Secret scanning
  - Container security scanning

- **`release.yml`**: Release management - manual workflow for version bumps
  - Automated version bumping
  - Changelog generation
  - Release PR creation
  - Version consistency validation

- **`dependabot-auto-merge.yml`**: Automated dependency updates
  - Auto-approves and merges patch/minor updates
  - Requires manual review for major updates
  - Waits for CI to pass before merging

### Automation Features
- **Dependabot**: Automated dependency updates with smart merging
- **Auto-merge**: Safe automation for low-risk changes
- **Release Management**: Streamlined version bumping and changelog generation
- **Security Monitoring**: Continuous security scanning and alerting
- **Performance Tracking**: Automated performance regression detection

### Professional Standards Compliance
- **Industry Best Practices**: Following established patterns from major tech companies
- **Security First**: Comprehensive security scanning and vulnerability management
- **Quality Gates**: Multiple checkpoints ensure code quality before deployment
- **Automated Testing**: Extensive test coverage with multiple testing strategies
- **Documentation**: Complete documentation for developers and users
- **Monitoring**: Comprehensive monitoring and alerting for production systems