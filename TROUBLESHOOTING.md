# 🔧 Troubleshooting Guide

## Quick Start
1. Run `START-EVERYTHING.bat` to start all services
2. Wait for all windows to open
3. Try the voice command: "Calculate total salary in my budget file"

## Common Issues

### ❌ CORS Errors (400 on OPTIONS requests)
**Problem**: Browser shows CORS policy errors
**Solution**: 
- Backend is configured to allow all origins (`allow_origins=["*"]`)
- Restart backend service if needed
- Check that backend is running on port 8000

### ❌ File Not Found Errors (404)
**Problem**: "Spreadsheet file not found: documents/sample-budget.csv"
**Solution**:
- Run `START-EVERYTHING.bat` which creates the sample file
- Or manually create `backend/documents/sample-budget.csv`
- Check file path in the command (use forward slashes)

### ❌ Backend Connection Failed
**Problem**: Frontend shows "Check that backend service is running"
**Solution**:
1. Open new terminal in `backend` folder
2. Run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
3. Check http://localhost:8000/health shows {"status": "healthy"}

### ❌ Python Dependencies Missing
**Problem**: Import errors when starting backend
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

### ❌ Node Dependencies Missing  
**Problem**: npm run commands fail
**Solution**:
```bash
npm install
```

## Testing Endpoints

Run the test script to verify all endpoints:
```bash
python test-endpoints.py
```

Expected output:
- ✅ Health check: 200
- ✅ Create file: 200  
- ✅ Analyze sheet: 200 (or 404 if no sample file)
- ✅ Update sheet: 200 (or 404 if no sample file)

## Manual API Testing

### Test Analysis Endpoint
```bash
curl -X POST "http://localhost:8000/api/analyze-sheet" \
  -H "Content-Type: application/json" \
  -d '{"path": "documents/sample-budget.csv", "op": "sum", "column": "Total_Monthly"}'
```

### Test Update Endpoint  
```bash
curl -X POST "http://localhost:8000/api/update-sheet" \
  -H "Content-Type: application/json" \
  -d '{"path": "documents/sample-budget.csv", "operation": "salary_increase", "percentage": 10.0}'
```

## Voice Commands That Should Work

- ✅ "Calculate total salary in my budget file"
- ✅ "Update salary with 10% increase in sample-budget.csv"  
- ✅ "Add performance rating column to employee data"
- ✅ "Analyze bonus amounts in my spreadsheet"
- ✅ "Create meeting notes for project review"

## Port Configuration

- **Backend API**: http://localhost:8000
- **Frontend Dev**: http://localhost:5173
- **Electron App**: Desktop application (no port)

## Log Files

Check these for detailed error information:
- Backend logs: Console output from uvicorn
- Frontend logs: Browser developer console (F12)
- Electron logs: Electron app console

## Still Having Issues?

1. Restart all services using `START-EVERYTHING.bat`
2. Check that all required ports (8000, 5173) are available
3. Verify Python and Node.js are installed
4. Run `python test-endpoints.py` to test API
5. Check browser console (F12) for JavaScript errors