# Aura Desktop Assistant - Operations Runbook

## Quick Start Guide

### Prerequisites
- **Node.js**: v18+ with npm/yarn
- **Python**: 3.9+ with pip
- **Rust**: Latest stable (for Tauri)
- **Git**: For version control

### Environment Setup

#### 1. Backend Configuration (.env)

Copy the example environment file and configure:

```bash
# In the backend directory
cp .env.example .env
```

Edit `.env` with your specific values:

```bash
# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=false

# API Configuration  
ENABLE_DOCS=true
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:1420", "tauri://localhost"]

# File System Configuration
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_EXTENSIONS=[".txt", ".md", ".json", ".csv", ".xlsx", ".xls", ".pdf"]
SAFE_DIRECTORIES=["./documents", "./data", "./temp"]

# Hugging Face Configuration (Required)
HF_API_TOKEN=hf_your_actual_token_here
HF_API_URL=https://api-inference.huggingface.co/models
HF_SUMMARIZATION_MODEL=facebook/bart-large-cnn
HF_QA_MODEL=deepset/roberta-base-squad2

# Request Configuration
REQUEST_TIMEOUT=30
MAX_RETRIES=3
RETRY_DELAY=1.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Security Configuration
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

**Important Environment Variables:**

- `HF_API_TOKEN`: Get from [Hugging Face](https://huggingface.co/settings/tokens)
- `SAFE_DIRECTORIES`: Directories where file operations are allowed
- `ALLOWED_ORIGINS`: Frontend URLs that can access the API
- `MAX_FILE_SIZE`: Maximum file size for processing (bytes)

#### 2. Frontend Configuration

Create `.env.local` in the root directory:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Feature Flags
VITE_ENABLE_VOICE=true
VITE_ENABLE_CLOUD_STT=false
VITE_ENABLE_CLOUD_NLP=false

# Development
VITE_DEBUG_MODE=true
VITE_LOG_LEVEL=debug
```

### Starting the Application

#### Method 1: Development Mode (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

**Terminal 3 - Tauri (Desktop App):**
```bash
npm run tauri dev
```

#### Method 2: Production Build

```bash
# Build frontend
npm run build

# Build and run Tauri app
npm run tauri build
```

#### Method 3: Docker (Backend Only)

```bash
cd backend
docker build -t aura-backend .
docker run -p 8000:8000 --env-file .env aura-backend
```

### Verification Steps

#### 1. Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

#### 2. API Documentation
Visit: http://localhost:8000/docs

#### 3. Frontend Access
- **Web**: http://localhost:3000
- **Tauri**: Desktop application window should open

#### 4. Feature Testing
```bash
# Test file creation
curl -X POST http://localhost:8000/api/files/create \
  -H "Content-Type: application/json" \
  -d '{"title": "test.txt", "content": "Hello World"}'

# Test document summarization (requires HF token)
curl -X POST http://localhost:8000/api/documents/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a long document that needs summarization..."}'
```

## Common Issues and Solutions

### Backend Issues

#### Issue: "ModuleNotFoundError" when starting backend
**Symptoms:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
1. Ensure virtual environment is activated:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. If still failing, try upgrading pip:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

#### Issue: "Port already in use" error
**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
1. Check what's using port 8000:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. Kill the process or change port in `.env`:
   ```bash
   PORT=8001
   ```

#### Issue: Hugging Face API errors
**Symptoms:**
```
401 Unauthorized: Invalid API token
```

**Solutions:**
1. Verify HF token is correct in `.env`
2. Check token permissions at https://huggingface.co/settings/tokens
3. Test token manually:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api-inference.huggingface.co/models/facebook/bart-large-cnn
   ```

#### Issue: File operation permissions
**Symptoms:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. Check `SAFE_DIRECTORIES` in `.env`
2. Ensure directories exist and are writable:
   ```bash
   mkdir -p documents data temp
   chmod 755 documents data temp
   ```

3. On Windows, check folder permissions in Properties

### Frontend Issues

#### Issue: "Network Error" when calling API
**Symptoms:**
- API calls failing in browser console
- CORS errors

**Solutions:**
1. Verify backend is running on correct port
2. Check `ALLOWED_ORIGINS` in backend `.env`
3. Update `VITE_API_BASE_URL` in frontend `.env.local`
4. Clear browser cache and restart dev server

#### Issue: Tauri build failures
**Symptoms:**
```
Error: failed to bundle project
```

**Solutions:**
1. Ensure Rust is installed and updated:
   ```bash
   rustup update stable
   ```

2. Clear Tauri cache:
   ```bash
   rm -rf src-tauri/target
   npm run tauri build
   ```

3. Check Tauri configuration in `src-tauri/tauri.conf.json`

#### Issue: Voice features not working
**Symptoms:**
- Microphone access denied
- STT not transcribing

**Solutions:**
1. Check browser permissions for microphone
2. Verify `VITE_ENABLE_VOICE=true` in `.env.local`
3. Test with different browsers (Chrome recommended)
4. For local STT, ensure Vosk models are downloaded

### MCP Server Issues

#### Issue: MCP server not starting
**Symptoms:**
```
Failed to start MCP server
```

**Solutions:**
1. Check if `uvx` is installed:
   ```bash
   uvx --version
   ```

2. Install uv if missing:
   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Test MCP server manually:
   ```bash
   uvx --from aura-mcp-server aura-mcp-server
   ```

#### Issue: MCP tools not recognized
**Symptoms:**
- Tools not appearing in Kiro
- Connection timeouts

**Solutions:**
1. Check `.kiro/settings/mcp.json` configuration
2. Restart Kiro after MCP config changes
3. Verify server logs in MCP Server view

### Performance Issues

#### Issue: Slow file processing
**Symptoms:**
- Long delays when processing documents
- High CPU/memory usage

**Solutions:**
1. Reduce `MAX_FILE_SIZE` in backend `.env`
2. Implement file streaming for large documents
3. Monitor system resources:
   ```bash
   # Windows
   tasklist /fi "imagename eq python.exe"
   
   # macOS/Linux
   ps aux | grep python
   ```

#### Issue: High memory usage
**Solutions:**
1. Restart backend service periodically
2. Check for memory leaks in logs
3. Reduce concurrent operations:
   ```bash
   # In .env
   MAX_CONCURRENT_OPERATIONS=3
   ```

## Monitoring and Maintenance

### Log Locations

**Backend Logs:**
- Console output (development)
- `backend/logs/` directory (production)

**Frontend Logs:**
- Browser Developer Console
- Network tab for API calls

**Tauri Logs:**
- Application console (development)
- OS-specific log directories (production)

### Health Monitoring

#### Automated Health Checks
```bash
#!/bin/bash
# health-check.sh

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend healthy"
else
    echo "❌ Backend unhealthy"
    exit 1
fi

# Check frontend (if running)
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend healthy"
else
    echo "⚠️  Frontend not accessible"
fi

echo "Health check completed"
```

#### Performance Monitoring
```python
# Add to backend for monitoring
import psutil
import logging

def log_system_metrics():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logging.info(f"System metrics - CPU: {cpu_percent}%, "
                f"Memory: {memory.percent}%, "
                f"Disk: {disk.percent}%")

# Call periodically or on high load
```

### Backup and Recovery

#### Configuration Backup
```bash
# Backup all configuration files
tar -czf aura-config-backup-$(date +%Y%m%d).tar.gz \
  backend/.env \
  .env.local \
  .kiro/ \
  src-tauri/tauri.conf.json
```

#### Data Backup
```bash
# Backup user data directories
tar -czf aura-data-backup-$(date +%Y%m%d).tar.gz \
  documents/ \
  data/ \
  backend/logs/
```

### Security Maintenance

#### Regular Security Tasks
1. **Update Dependencies:**
   ```bash
   # Backend
   pip list --outdated
   pip install -r requirements.txt --upgrade
   
   # Frontend
   npm audit
   npm update
   ```

2. **Rotate API Keys:**
   - Update HF_API_TOKEN monthly
   - Update any cloud service credentials

3. **Review Logs:**
   ```bash
   # Check for security events
   grep -i "error\|warning\|security" backend/logs/*.log
   ```

4. **Validate Configurations:**
   ```bash
   # Run security validation
   python scripts/validate-security.py
   ```

## Troubleshooting Checklist

### Before Reporting Issues

1. **Check Prerequisites:**
   - [ ] Node.js v18+ installed
   - [ ] Python 3.9+ installed
   - [ ] Rust installed (for Tauri)
   - [ ] All dependencies installed

2. **Verify Configuration:**
   - [ ] `.env` file exists and configured
   - [ ] API tokens are valid
   - [ ] Ports are available
   - [ ] Directories have correct permissions

3. **Test Components:**
   - [ ] Backend health check passes
   - [ ] Frontend loads without errors
   - [ ] API endpoints respond correctly
   - [ ] File operations work

4. **Check Logs:**
   - [ ] Backend logs for errors
   - [ ] Browser console for frontend errors
   - [ ] System logs for permission issues

### Getting Help

**Documentation:**
- README.md - Project overview
- SECURITY.md - Security guidelines
- PRIVACY.md - Privacy policy
- API documentation at `/docs`

**Issue Reporting:**
Include the following information:
- Operating system and version
- Node.js and Python versions
- Error messages and stack traces
- Steps to reproduce
- Configuration files (redacted)

**Community:**
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Security issues: security@aura-assistant.com