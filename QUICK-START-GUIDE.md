# 🚀 Quick Start Guide - Aura Desktop Assistant

## 🔥 **FASTEST WAY TO GET STARTED**

### Option 1: Minimal Server (Recommended for Demo)
```bash
START-MINIMAL-SERVER.bat
```
- Installs only essential dependencies
- Starts server quickly
- Perfect for hackathon demo

### Option 2: Server Only (If dependencies already installed)
```bash
START-SERVER-ONLY.bat
```
- Skips dependency installation
- Starts server immediately
- Use if you already have Python packages

### Option 3: Full Installation (Complete features)
```bash
START-AUTOMATION-SERVER.bat
```
- Installs all dependencies
- May have permission issues on some systems
- Provides full functionality

## 🧪 **Testing Your Server**

### Quick Test (No pandas required)
```bash
python test-server-only.py
```

### Basic Test (Minimal dependencies)
```bash
python test-basic-endpoints.py
```

### Full Test (All features)
```bash
python test-automation-endpoints.py
```

## 🔧 **Troubleshooting Common Issues**

### Issue 1: Permission Errors (Windows/Anaconda)
**Error:** `Access is denied` when installing packages

**Solution:**
1. Try: `START-MINIMAL-SERVER.bat`
2. Or run as Administrator
3. Or use: `pip install --user [package]`

### Issue 2: Pandas/Numpy Installation Fails
**Error:** `Could not install packages due to an OSError`

**Solution:**
1. Use `START-SERVER-ONLY.bat` (basic functionality works without pandas)
2. Or install manually: `conda install pandas numpy`
3. Or use virtual environment

### Issue 3: Import Errors
**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
- The server is designed to work without pandas
- Basic functionality will still work
- Use `test-server-only.py` to verify

### Issue 4: Port Already in Use
**Error:** `Address already in use`

**Solution:**
1. Kill existing process: `taskkill /f /im python.exe`
2. Or change port in `backend/config.py`
3. Or restart your computer

## 📊 **What Works Without Heavy Dependencies**

✅ **Always Available:**
- Health check endpoint
- File operations (create, open, write)
- OCR text extraction from text files
- Document classification
- Email rule creation
- Calendar scheduling (basic)
- Workflow processing
- API documentation

⚠️ **Requires Additional Packages:**
- Spreadsheet analysis (needs pandas)
- Chart generation (needs matplotlib)
- Advanced OCR (needs opencv, tesseract)
- PDF processing (needs PyMuPDF)

## 🎯 **For Hackathon Demo**

**Recommended Flow:**
1. Run: `START-MINIMAL-SERVER.bat`
2. Test: `python test-server-only.py`
3. Open: http://localhost:8000/docs
4. Demo the API endpoints in the browser

**Key Demo Points:**
- Show API documentation at `/docs`
- Test file creation endpoint
- Test OCR data extraction
- Test document classification
- Test workflow creation
- Show comprehensive error handling

## 🏆 **Success Metrics**

Your server is working correctly if:
- ✅ Health check returns 200 OK
- ✅ File creation works
- ✅ OCR extraction works (even with text files)
- ✅ Document classification works
- ✅ API docs are accessible at `/docs`

## 🆘 **Emergency Backup Plan**

If nothing works:
1. Open `backend/main.py` directly
2. Comment out problematic imports
3. Run: `python backend/main.py`
4. Use only the health check endpoint for demo

## 📞 **Quick Commands Reference**

```bash
# Start server (minimal)
START-MINIMAL-SERVER.bat

# Test server
python test-server-only.py

# View API docs
# Open: http://localhost:8000/docs

# Stop server
# Press Ctrl+C in terminal

# Kill all Python processes (if stuck)
taskkill /f /im python.exe
```

**🎉 You're ready for the hackathon! Focus on demonstrating the API capabilities and automation concepts rather than getting every dependency perfect.**