@echo off
echo Testing basic batch file functionality...
echo.

REM Test if the MCP batch file exists
if exist "scripts\simple-mcp.bat" (
    echo ✓ MCP batch file found
) else (
    echo ✗ MCP batch file not found
    exit /b 1
)

REM Test basic echo functionality
echo Testing basic input/output...
echo {"method":"ping","id":1} > temp-input.txt
type temp-input.txt | scripts\simple-mcp.bat
del temp-input.txt

echo.
echo Test completed!