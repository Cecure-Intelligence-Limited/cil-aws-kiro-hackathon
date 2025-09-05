@echo off
REM Test the simple MCP batch file

echo Testing MCP Batch File...
echo.

REM Start the MCP server in the background
start /B scripts\simple-mcp.bat > mcp-output.txt 2>&1

REM Wait a moment for it to start
timeout /t 2 /nobreak >nul

REM Send test requests
echo Testing initialize request...
echo {"method":"initialize","params":{"protocolVersion":"2024-11-05"},"jsonrpc":"2.0","id":0} | scripts\simple-mcp.bat

echo.
echo Testing tools/list request...
echo {"method":"tools/list","params":{},"jsonrpc":"2.0","id":1} | scripts\simple-mcp.bat

echo.
echo Testing ping request...
echo {"method":"ping","params":{},"jsonrpc":"2.0","id":2} | scripts\simple-mcp.bat

echo.
echo Test completed!