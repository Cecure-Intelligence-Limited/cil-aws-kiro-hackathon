# Contributing to Aura Desktop Assistant

Thank you for your interest in contributing to Aura! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Security Guidelines](#security-guidelines)

## 📜 Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🚀 Getting Started

### Prerequisites

- Node.js 20+ and npm
- Python 3.12+ with pip
- Rust 1.70+ with Cargo
- Git for version control

### Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/aura-desktop-assistant.git
   cd aura-desktop-assistant
   ```

2. **Install Dependencies**
   ```bash
   npm install
   cd backend && pip install -r requirements/development.txt
   ```

3. **Setup Pre-commit Hooks**
   ```bash
   npm run prepare
   ```

4. **Run Tests**
   ```bash
   npm test
   ```

## 🛠️ Development Setup

### Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Configure your API keys and settings in `.env`

### Running the Application

```bash
# Start backend services
cd backend && python -m uvicorn app.main:app --reload --port 8000 &

# Start frontend in development mode
npm run tauri dev
```

### Available Scripts

- `npm run dev` - Start Vite development server
- `npm run build` - Build React app for production
- `npm run tauri:dev` - Run Tauri in development mode
- `npm run tauri:build` - Build Tauri application
- `npm run lint` - Run ESLint
- `npm run format` - Run Prettier
- `npm run type-check` - Run TypeScript compiler
- `npm test` - Run all tests

## 🤝 Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 📚 **Documentation**: Improve or add documentation
- 🧪 **Tests**: Add or improve test coverage
- 🔧 **Code**: Fix bugs or implement features
- 🎨 **UI/UX**: Improve user interface and experience

### Before You Start

1. **Check Existing Issues**: Search for existing issues or discussions
2. **Create an Issue**: For significant changes, create an issue first
3. **Discuss**: Engage with maintainers and community
4. **Plan**: Outline your approach before coding

## 🔄 Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Your Changes

- Follow our [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

We use [Conventional Commits](https://conventionalcommits.org/):

```bash
git commit -m "feat(voice): add new voice command for file operations"
git commit -m "fix(ui): resolve overlay positioning issue"
git commit -m "docs(api): update API documentation"
```

**Commit Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes
- `refactor` - Code refactoring
- `test` - Test additions or modifications
- `chore` - Maintenance tasks

### 4. Push and Create PR

```bash
git push origin your-branch-name
```

Create a pull request using our [PR template](.github/PULL_REQUEST_TEMPLATE.md).

### 5. PR Review Process

1. **Automated Checks**: CI pipeline runs automatically
2. **Code Review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: PR approved by maintainers
5. **Merge**: PR merged into main branch

## 📏 Coding Standards

### TypeScript/JavaScript

- Use TypeScript for all new code
- Follow ESLint and Prettier configurations
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Prefer functional programming patterns

```typescript
// Good
const processVoiceInput = async (audioData: AudioBuffer): Promise<ParsedIntent> => {
  // Implementation
};

// Bad
const process = (data: any) => {
  // Implementation
};
```

### React Components

- Use functional components with hooks
- Follow component naming conventions (PascalCase)
- Use TypeScript interfaces for props
- Implement proper error boundaries

```tsx
interface VoiceInputProps {
  onVoiceData: (data: AudioBuffer) => void;
  isRecording: boolean;
}

export const VoiceInput: React.FC<VoiceInputProps> = ({ onVoiceData, isRecording }) => {
  // Component implementation
};
```

### Python

- Follow PEP 8 style guide
- Use type hints for all functions
- Add docstrings for modules, classes, and functions
- Use Black for code formatting
- Use isort for import sorting

```python
def process_spreadsheet_data(
    file_path: str, 
    operation: str, 
    column: str
) -> Dict[str, Any]:
    """
    Process spreadsheet data with specified operation.
    
    Args:
        file_path: Path to the spreadsheet file
        operation: Operation to perform (sum, avg, count)
        column: Column name to analyze
        
    Returns:
        Dictionary containing operation results
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If operation is not supported
    """
    # Implementation
```

### Rust

- Follow Rust style guidelines
- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Add comprehensive documentation
- Handle errors properly with Result types

```rust
/// Process voice input and return transcribed text
pub async fn process_voice_input(audio_data: Vec<u8>) -> Result<String, VoiceError> {
    // Implementation
}
```

## 🧪 Testing Requirements

### Test Coverage

- Maintain >90% test coverage
- Write tests for all new features
- Include edge cases and error scenarios
- Test both happy path and failure cases

### Testing Types

1. **Unit Tests**: Test individual functions/components
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user workflows
4. **Security Tests**: Test security vulnerabilities

### Writing Tests

```typescript
// Frontend tests with Jest and React Testing Library
describe('VoiceInput Component', () => {
  it('should start recording when microphone button is clicked', async () => {
    const onVoiceData = jest.fn();
    render(<VoiceInput onVoiceData={onVoiceData} isRecording={false} />);
    
    const micButton = screen.getByRole('button', { name: /microphone/i });
    fireEvent.click(micButton);
    
    expect(onVoiceData).toHaveBeenCalled();
  });
});
```

```python
# Backend tests with pytest
def test_process_spreadsheet_sum():
    """Test spreadsheet sum operation."""
    result = process_spreadsheet_data(
        file_path="test_data.csv",
        operation="sum",
        column="salary"
    )
    
    assert result["value"] == 150000
    assert result["count"] == 10
```

## 🔒 Security Guidelines

### Security Best Practices

1. **Input Validation**: Validate all user inputs
2. **Sanitization**: Sanitize data before processing
3. **Authentication**: Secure API endpoints
4. **Encryption**: Encrypt sensitive data
5. **Dependencies**: Keep dependencies updated

### Security Review Process

- All PRs undergo security review
- Use security scanning tools
- Follow OWASP guidelines
- Report security issues privately

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Email security issues to: security@aura-assistant.com

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## 📚 Documentation

### Documentation Requirements

- Update README.md for user-facing changes
- Add API documentation for new endpoints
- Include inline code comments
- Update architecture documentation

### Documentation Style

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up-to-date

## 🎯 Issue Guidelines

### Bug Reports

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml):

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Screenshots/logs if applicable

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml):

- Problem statement
- Proposed solution
- Use cases
- Implementation considerations

## 🏷️ Labels and Milestones

### Labels

- `bug` - Bug reports
- `enhancement` - Feature requests
- `documentation` - Documentation updates
- `good first issue` - Good for newcomers
- `help wanted` - Community help needed
- `priority: high` - High priority items
- `security` - Security-related issues

### Milestones

- Version-based milestones (v1.0, v1.1, etc.)
- Feature-based milestones
- Bug fix releases

## 🎉 Recognition

Contributors are recognized in:

- GitHub contributors list
- Release notes
- Project documentation
- Annual contributor highlights

## 📞 Getting Help

- **GitHub Discussions**: For questions and discussions
- **Issues**: For bug reports and feature requests
- **Discord**: Real-time chat with community
- **Email**: maintainers@aura-assistant.com

## 📄 License

By contributing to Aura, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Aura Desktop Assistant! 🚀