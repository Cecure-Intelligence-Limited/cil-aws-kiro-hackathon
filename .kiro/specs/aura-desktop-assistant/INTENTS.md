# Aura Intent Schemas

This document defines the strict JSON schemas for all supported intents in the Aura desktop assistant, following JSON Schema Draft-07 specification.

## Base Intent Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "enum": ["CreateFile", "OpenItem", "AnalyzeSpreadsheet", "SummarizeDoc"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Confidence score from 0.0 to 1.0"
    },
    "parameters": {
      "type": "object"
    },
    "context": {
      "type": "object",
      "properties": {
        "sessionId": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "userInput": {"type": "string"}
      }
    }
  },
  "required": ["intent", "confidence", "parameters"],
  "additionalProperties": false
}
```

## Intent Definitions

### 1. CreateFile Intent

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "const": "CreateFile"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "parameters": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string",
          "minLength": 1,
          "maxLength": 255,
          "description": "The name of the file to create"
        },
        "path": {
          "type": "string",
          "pattern": "^[^<>:\"|?*\\x00-\\x1f]*$",
          "description": "Optional directory path where file should be created"
        },
        "content": {
          "type": "string",
          "description": "Optional initial content for the file"
        }
      },
      "required": ["title"],
      "additionalProperties": false
    }
  },
  "required": ["intent", "confidence", "parameters"]
}
```

**Example:**
```json
{
  "intent": "CreateFile",
  "confidence": 0.95,
  "parameters": {
    "title": "meeting-notes.txt",
    "path": "./documents",
    "content": "Meeting Notes - January 15, 2025\n\nAttendees:\n- "
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:30:00Z",
    "userInput": "Create a file called meeting-notes.txt in the documents folder with a header"
  }
}
```

### 2. OpenItem Intent

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "const": "OpenItem"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "minLength": 1,
          "maxLength": 500,
          "description": "Search query for the item to open (file name, app name, etc.)"
        },
        "type": {
          "type": "string",
          "enum": ["file", "application", "folder", "auto"],
          "default": "auto",
          "description": "Type of item to open - auto will attempt to determine type"
        }
      },
      "required": ["query"],
      "additionalProperties": false
    }
  },
  "required": ["intent", "confidence", "parameters"]
}
```

**Examples:**
```json
{
  "intent": "OpenItem",
  "confidence": 0.88,
  "parameters": {
    "query": "budget.xlsx",
    "type": "file"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:32:00Z",
    "userInput": "Open the budget spreadsheet"
  }
}
```

```json
{
  "intent": "OpenItem",
  "confidence": 0.92,
  "parameters": {
    "query": "Visual Studio Code",
    "type": "application"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:35:00Z",
    "userInput": "Launch VS Code"
  }
}
```

### 3. AnalyzeSpreadsheet Intent

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "const": "AnalyzeSpreadsheet"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "parameters": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "pattern": "\\.(csv|xlsx|xls|ods)$",
          "description": "Path to the spreadsheet file"
        },
        "op": {
          "type": "string",
          "enum": ["sum", "avg", "count", "total"],
          "description": "Operation to perform on the data"
        },
        "column": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "Column name or identifier to analyze"
        }
      },
      "required": ["path", "op", "column"],
      "additionalProperties": false
    }
  },
  "required": ["intent", "confidence", "parameters"]
}
```

**Examples:**
```json
{
  "intent": "AnalyzeSpreadsheet",
  "confidence": 0.94,
  "parameters": {
    "path": "./data/employees.csv",
    "op": "sum",
    "column": "Salary"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:40:00Z",
    "userInput": "Calculate the total salary from the employees CSV file"
  }
}
```

```json
{
  "intent": "AnalyzeSpreadsheet",
  "confidence": 0.89,
  "parameters": {
    "path": "sales_data.xlsx",
    "op": "avg",
    "column": "Revenue"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:42:00Z",
    "userInput": "What's the average revenue in the sales data spreadsheet?"
  }
}
```

### 4. SummarizeDoc Intent

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "intent": {
      "type": "string",
      "const": "SummarizeDoc"
    },
    "confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "parameters": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "pattern": "\\.pdf$",
          "description": "Path to the PDF document to summarize"
        },
        "length": {
          "type": "string",
          "enum": ["short", "bullets", "tweet"],
          "description": "Desired summary format and length"
        }
      },
      "required": ["path", "length"],
      "additionalProperties": false
    }
  },
  "required": ["intent", "confidence", "parameters"]
}
```

**Examples:**
```json
{
  "intent": "SummarizeDoc",
  "confidence": 0.91,
  "parameters": {
    "path": "./reports/quarterly-report.pdf",
    "length": "bullets"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:45:00Z",
    "userInput": "Summarize the quarterly report in bullet points"
  }
}
```

```json
{
  "intent": "SummarizeDoc",
  "confidence": 0.87,
  "parameters": {
    "path": "research-paper.pdf",
    "length": "tweet"
  },
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:47:00Z",
    "userInput": "Give me a tweet-length summary of this research paper"
  }
}
```

## Error Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "error": {
      "type": "object",
      "properties": {
        "code": {
          "type": "string",
          "enum": [
            "INTENT_PARSE_FAILED",
            "AMBIGUOUS_INTENT",
            "MISSING_PARAMETERS",
            "INVALID_PARAMETERS",
            "LOW_CONFIDENCE",
            "UNSUPPORTED_OPERATION",
            "CONTEXT_REQUIRED"
          ]
        },
        "message": {
          "type": "string",
          "description": "Human-readable error description"
        },
        "details": {
          "type": "object",
          "properties": {
            "userInput": {"type": "string"},
            "confidence": {"type": "number"},
            "missingFields": {
              "type": "array",
              "items": {"type": "string"}
            },
            "invalidFields": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "field": {"type": "string"},
                  "value": {},
                  "reason": {"type": "string"}
                }
              }
            }
          }
        }
      },
      "required": ["code", "message"]
    },
    "suggestions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["rephrase", "clarify", "example", "alternative"]
          },
          "message": {"type": "string"},
          "example": {"type": "string"}
        },
        "required": ["type", "message"]
      }
    },
    "context": {
      "type": "object",
      "properties": {
        "sessionId": {"type": "string"},
        "timestamp": {"type": "string", "format": "date-time"},
        "userInput": {"type": "string"}
      }
    }
  },
  "required": ["error"],
  "additionalProperties": false
}
```

## Error Examples

### Parse Failure Error
```json
{
  "error": {
    "code": "INTENT_PARSE_FAILED",
    "message": "Unable to determine intent from user input",
    "details": {
      "userInput": "do something with the thing",
      "confidence": 0.12
    }
  },
  "suggestions": [
    {
      "type": "rephrase",
      "message": "Please be more specific about what you'd like me to do",
      "example": "Try saying 'Create a file called notes.txt' or 'Open the budget spreadsheet'"
    },
    {
      "type": "example",
      "message": "Here are some things I can help with:",
      "example": "• Create and edit files\n• Analyze spreadsheet data\n• Summarize PDF documents\n• Open files and applications"
    }
  ],
  "context": {
    "sessionId": "sess_123",
    "timestamp": "2025-01-15T10:50:00Z",
    "userInput": "do something with the thing"
  }
}
```

### Ambiguous Intent Error
```json
{
  "error": {
    "code": "AMBIGUOUS_INTENT",
    "message": "Multiple possible intents detected",
    "details": {
      "userInput": "open report",
      "confidence": 0.65
    }
  },
  "suggestions": [
    {
      "type": "clarify",
      "message": "Did you want to:",
      "example": "• Open an existing report file?\n• Create a new report?\n• Open a reporting application?"
    },
    {
      "type": "rephrase",
      "message": "Please specify the file type or be more specific",
      "example": "Try 'Open report.pdf' or 'Open the quarterly report'"
    }
  ]
}
```

### Missing Parameters Error
```json
{
  "error": {
    "code": "MISSING_PARAMETERS",
    "message": "Required parameters are missing",
    "details": {
      "userInput": "sum the column",
      "missingFields": ["path", "column"]
    }
  },
  "suggestions": [
    {
      "type": "clarify",
      "message": "I need more information to analyze the spreadsheet:",
      "example": "• Which file should I analyze?\n• Which column should I sum?"
    },
    {
      "type": "example",
      "message": "Try something like:",
      "example": "Sum the Salary column in employees.csv"
    }
  ]
}
```

### Invalid Parameters Error
```json
{
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "One or more parameters are invalid",
    "details": {
      "userInput": "create file with name <>invalid",
      "invalidFields": [
        {
          "field": "title",
          "value": "<>invalid",
          "reason": "Contains invalid characters for filename"
        }
      ]
    }
  },
  "suggestions": [
    {
      "type": "rephrase",
      "message": "File names cannot contain these characters: < > : \" | ? *",
      "example": "Try 'Create file called report.txt' instead"
    },
    {
      "type": "alternative",
      "message": "Consider using underscores or hyphens instead of special characters",
      "example": "Use 'my_report.txt' or 'my-report.txt'"
    }
  ]
}
```

## Validation Rules

### General Validation
- All intents must have confidence score between 0.0 and 1.0
- Low confidence (< 0.7) should trigger clarification requests
- All required parameters must be present and valid
- File paths must be sanitized and validated for security

### File Path Validation
- No path traversal attempts (../, ..\)
- No system/protected directories
- Valid file extensions for respective operations
- Maximum path length limits (260 chars on Windows)

### Content Validation
- File content size limits (configurable, default 10MB)
- Text encoding validation (UTF-8)
- Malicious content scanning for file operations

### Spreadsheet Validation
- Supported formats: CSV, XLSX, XLS, ODS
- Column names must exist in the spreadsheet
- Numeric operations only on numeric columns
- File size limits for processing

### Document Validation
- PDF format validation
- File accessibility checks
- Size limits for AI processing
- Text extraction capability verification

This schema ensures strict validation of all user intents while providing comprehensive error handling and user guidance for improved interaction quality.