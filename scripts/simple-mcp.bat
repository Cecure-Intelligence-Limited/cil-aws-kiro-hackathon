@echo off
REM Simple MCP Server that responds to JSON-RPC requests
REM This handles the proper MCP protocol format

echo Starting Simple MCP Server... >&2

:loop
set /p input=
if "%input%"=="" goto loop

echo Received: %input% >&2

REM Check if it's an initialize request
echo %input% | findstr /C:"initialize" >nul
if %errorlevel%==0 (
    echo {"jsonrpc":"2.0","id":0,"result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{"listChanged":false}},"serverInfo":{"name":"aura-desktop-assistant","version":"1.0.0"}}}
    goto loop
)

REM Check if it's a tools/list request
echo %input% | findstr /C:"tools/list" >nul
if %errorlevel%==0 (
    echo {"jsonrpc":"2.0","id":1,"result":{"tools":[{"name":"create_file","description":"Create a new file","inputSchema":{"type":"object","properties":{"title":{"type":"string","description":"File name"},"content":{"type":"string","description":"File content"}},"required":["title"]}}]}}
    goto loop
)

REM Check if it's a tools/call request
echo %input% | findstr /C:"tools/call" >nul
if %errorlevel%==0 (
    echo {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":"✅ File created successfully (simulated)"}],"isError":false}}
    goto loop
)

REM Check if it's a ping request
echo %input% | findstr /C:"ping" >nul
if %errorlevel%==0 (
    echo {"jsonrpc":"2.0","id":3,"result":{"status":"ok"}}
    goto loop
)

REM Default response for unknown methods
echo {"jsonrpc":"2.0","id":null,"error":{"code":-32601,"message":"Method not found"}}
goto loop