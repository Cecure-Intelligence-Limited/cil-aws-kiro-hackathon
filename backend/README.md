# Aura Desktop Assistant API

A FastAPI-based backend service for the Aura Desktop Assistant, providing REST API endpoints for file operations, spreadsheet analysis, and document processing.

## Features

- **File Operations**: Create files and open items (files, applications, folders) cross-platform
- **Spreadsheet Analysis**: Analyze CSV, Excel, and ODS files with pandas and fuzzy column matching
- **Document Processing**: Extract text from PDFs and generate summaries using Hugging Face models
- **Structured Logging**: JSON logging with structlog for production monitoring
- **OpenAPI Documentation**: Auto-generated API documentation
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### Prerequisites

- Python 3.11+
- pip or poetry for dependency management

### Installation

1. **Clone and navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

## API Endpoints

### POST /create_file
Create a new file with optional content.

**Request:**
```json
{
  "title": "meeting-notes.txt",
  "path": "./documents",
  "content": "Meeting notes content..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "File 'meeting-notes.txt' created successfully",
  "data": {
    "file_path": "/app/documents/meeting-notes.txt",
    "size": 123,
    "created": true,
    "directory": "/app/documents"
  }
}
```

### POST /open_item
Open a file, application, or folder.

**Request:**
```json
{
  "query": "budget.xlsx",
  "type": "file"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Opened 'budget.xlsx' successfully",
  "data": {
    "path": "/app/documents/budget.xlsx",
    "type": "file",
    "opened": true,
    "method": "file_system"
  }
}
```

### POST /analyze_sheet
Analyze spreadsheet data with fuzzy column matching.

**Request:**
```json
{
  "path": "employees.csv",
  "op": "sum",
  "column": "salary"
}
```

**Response:**
```json
{
  "success": true,
  "result": 180000.0,
  "matched_column": "Salary",
  "cells_count": 10,
  "operation": "sum",
  "message": "Analysis completed: sum of 'Salary' = 180000.0"
}
```

### POST /summarize_doc
Summarize PDF documents using Hugging Face models.

**Request:**
```json
{
  "path": "quarterly-report.pdf",
  "length": "bullets"
}
```

**Response:**
```json
{
  "success": true,
  "summary": "• Q4 revenue increased by 15%\n• New product launch successful\n• Market expansion in Asia",
  "length_type": "bullets",
  "word_count": 12,
  "message": "Document summarized successfully (12 words)"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `127.0.0.1` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `HF_API_TOKEN` | Hugging Face API token | Required for AI features |
| `MAX_FILE_SIZE` | Maximum file size in bytes | `10485760` (10MB) |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FORMAT` | Log format (json/console) | `json` |

### Hugging Face Integration

The API uses Hugging Face Inference API for document summarization:

- **Summarization Model**: `facebook/bart-large-cnn`
- **QA Model**: `deepset/roberta-base-squad2`
- **Retry Logic**: Automatic retries with exponential backoff
- **Fallback**: Local text processing when API is unavailable

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in production mode with nginx
docker-compose --profile production up
```

## File System Security

The API implements several security measures:

- **Path Validation**: Prevents path traversal attacks
- **Safe Directories**: Restricts file operations to designated directories
- **File Size Limits**: Configurable maximum file sizes
- **Extension Filtering**: Whitelist of allowed file extensions
- **Input Sanitization**: Validates all user inputs

## Logging

Structured logging with contextual information:

```json
{
  "event": "File created successfully",
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "info",
  "file_path": "/app/documents/test.txt",
  "size": 123
}
```

## Error Handling

Comprehensive error handling with appropriate HTTP status codes:

- `400` - Bad Request (validation errors)
- `404` - Not Found (file/item not found)
- `409` - Conflict (file already exists)
- `413` - Payload Too Large (file size exceeded)
- `500` - Internal Server Error

## Performance

- **Async Operations**: All I/O operations are asynchronous
- **Connection Pooling**: HTTP client connection reuse
- **Caching**: Response caching for expensive operations
- **Streaming**: Large file processing with streaming
- **Rate Limiting**: Configurable request rate limiting

## Deployment

### Production Deployment

1. **Set production environment variables**
2. **Use a production ASGI server** (included uvicorn with workers)
3. **Set up reverse proxy** (nginx configuration included)
4. **Configure logging** (JSON format for log aggregation)
5. **Set up monitoring** (health check endpoint available)

### Docker Deployment

```bash
# Build production image
docker build -t aura-api .

# Run with environment file
docker run --env-file .env -p 8000:8000 aura-api
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.