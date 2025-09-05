@echo off
REM Aura Desktop Assistant MCP Server for Windows
REM This batch file starts the MCP server with proper Node.js detection

setlocal enabledelayedexpansion

REM Try to find Node.js in common locations
set "NODE_EXE="
for %%i in (node.exe) do set "NODE_EXE=%%~$PATH:i"

if not defined NODE_EXE (
    REM Try common installation paths
    if exist "C:\Program Files\nodejs\node.exe" set "NODE_EXE=C:\Program Files\nodejs\node.exe"
    if exist "C:\Program Files (x86)\nodejs\node.exe" set "NODE_EXE=C:\Program Files (x86)\nodejs\node.exe"
    if exist "%APPDATA%\npm\node.exe" set "NODE_EXE=%APPDATA%\npm\node.exe"
    if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" set "NODE_EXE=%LOCALAPPDATA%\Programs\nodejs\node.exe"
)

if not defined NODE_EXE (
    echo Error: Node.js not found. Please install Node.js from https://nodejs.org/ >&2
    exit /b 1
)

REM Set environment variables
set "AURA_API_URL=http://localhost:8000"
set "LOG_LEVEL=INFO"
set "NODE_ENV=development"

REM Change to the project directory
cd /d "%~dp0\.."

REM Check if tsx is available
"%NODE_EXE%" -e "require('tsx')" >nul 2>&1
if errorlevel 1 (
    echo Installing tsx... >&2
    "%NODE_EXE%" -e "require('child_process').execSync('npm install -g tsx', {stdio: 'inherit'})"
)

REM Start the MCP server
echo Starting Aura Desktop Assistant MCP Server... >&2
"%NODE_EXE%" -r tsx/cjs src/services/mcpStandalone.ts