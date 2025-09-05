# Aura Desktop Assistant - MCP Server Setup

This guide helps you set up the Model Context Protocol (MCP) server for Aura Desktop Assistant to work with Kiro IDE.

## Prerequisites

1. **Node.js** (v18 or higher) - Download from [nodejs.org](https://nodejs.org/)
2. **Kiro IDE** with MCP support
3. **Aura Backend Server** running on `http://localhost:8000`

## Quick Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Test the MCP Server

```bash
npm run mcp:test
```

This will start the MCP server and send test requests to verify it's working.

### 3. Configure Kiro IDE

The MCP server configuration is already set up in `.kiro/settings/mcp.json`. Kiro IDE should automatically detect and connect to the server.

## Manual Testing

### Start the MCP Server Manually

**Windows:**
```cmd
scripts\mcp-server.bat
```

**macOS/Linux:**
```bash
chmod +x scripts/mcp-server.sh
scripts/mcp-server.sh
```

### Test with Raw JSON

You can test the server by sending JSON-RPC requests via stdin:

```bash
# Initialize the server
echo '{"method":"initialize","params":{},"id":1}' | npm run mcp:server

# List available tools
echo '{"method":"tools/list","params":{},"id":2}' | npm run mcp:server

# Call a tool
echo '{"method":"tools/call","params":{"name":"create_file","arguments":{"title":"test.txt","content":"Hello World"}},"id":3}' | npm run mcp:server
```

## Available Tools

The MCP server provides these tools:

### 1. `create_file`
Create a new file with optional content.

**Parameters:**
- `title` (required): File name with extension
- `path` (optional): Directory path
- `content` (optional): File content

**Example:**
```json
{
  "name": "create_file",
  "arguments": {
    "title": "notes.txt",
    "path": "./documents",
    "content": "Meeting notes..."
  }
}
```

### 2. `open_item`
Open a file, application, or folder.

**Parameters:**
- `query` (required): Search query for the item
- `type` (optional): Type of item (`file`, `application`, `folder`, `auto`)

**Example:**
```json
{
  "name": "open_item",
  "arguments": {
    "query": "Visual Studio Code",
    "type": "application"
  }
}
```

### 3. `analyze_sheet`
Analyze spreadsheet data with mathematical operations.

**Parameters:**
- `path` (required): Path to spreadsheet file
- `op` (required): Operation (`sum`, `avg`, `count`, `total`)
- `column` (required): Column name to analyze

**Example:**
```json
{
  "name": "analyze_sheet",
  "arguments": {
    "path": "data.csv",
    "op": "sum",
    "column": "salary"
  }
}
```

### 4. `summarize_doc`
Summarize PDF documents using AI.

**Parameters:**
- `path` (required): Path to PDF file
- `length` (optional): Summary type (`short`, `bullets`, `tweet`)

**Example:**
```json
{
  "name": "summarize_doc",
  "arguments": {
    "path": "report.pdf",
    "length": "bullets"
  }
}
```

## Troubleshooting

### Common Issues

#### 1. "Node.js not found"
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Make sure Node.js is in your system PATH
- Restart your terminal/command prompt

#### 2. "MCP server connection timeout"
- Ensure the backend server is running: `npm run tauri:dev`
- Check that port 8000 is not blocked by firewall
- Verify the MCP server starts without errors: `npm run mcp:test`

#### 3. "Tool execution failed"
- Make sure the Aura backend API is running
- Check the backend logs for errors
- Verify the API endpoint is accessible: `curl http://localhost:8000/health`

#### 4. "Permission denied" on scripts
**macOS/Linux:**
```bash
chmod +x scripts/mcp-server.sh
```

### Debug Mode

Set environment variables for more detailed logging:

```bash
# Windows
set LOG_LEVEL=DEBUG
set NODE_ENV=development

# macOS/Linux
export LOG_LEVEL=DEBUG
export NODE_ENV=development
```

### Manual MCP Configuration

If the automatic configuration doesn't work, manually add this to your Kiro IDE MCP settings:

```json
{
  "mcpServers": {
    "aura-desktop-assistant": {
      "command": "scripts/mcp-server.bat",
      "args": [],
      "cwd": "./",
      "env": {
        "AURA_API_URL": "http://localhost:8000",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "autoApprove": [
        "create_file",
        "open_item",
        "analyze_sheet",
        "summarize_doc"
      ]
    }
  }
}
```

## Development

### Adding New Tools

1. Add the tool definition to `src/services/kiroAgent.ts`
2. Update the routing rules in the same file
3. Add the corresponding API endpoint mapping
4. Test with `npm run mcp:test`

### Debugging

The MCP server logs to stderr, so you can see debug information while it runs:

```bash
npm run mcp:server 2>debug.log
```

## Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Run `npm run mcp:test` to verify the setup
3. Check the Kiro IDE MCP logs
4. Ensure the backend server is running and accessible