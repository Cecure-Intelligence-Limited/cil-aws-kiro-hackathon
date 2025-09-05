// import { Intent } from '../types';

// JSON Schema definitions based on INTENTS.md
const INTENT_SCHEMAS = {
  CreateFile: {
    type: 'object',
    properties: {
      intent: { type: 'string', const: 'CreateFile' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      parameters: {
        type: 'object',
        properties: {
          title: { type: 'string', minLength: 1, maxLength: 255 },
          path: { type: 'string', pattern: '^[^<>:"|?*\\x00-\\x1f]*$' },
          content: { type: 'string' }
        },
        required: ['title'],
        additionalProperties: false
      }
    },
    required: ['intent', 'confidence', 'parameters']
  },
  OpenItem: {
    type: 'object',
    properties: {
      intent: { type: 'string', const: 'OpenItem' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      parameters: {
        type: 'object',
        properties: {
          query: { type: 'string', minLength: 1, maxLength: 500 },
          type: { type: 'string', enum: ['file', 'application', 'folder', 'auto'] }
        },
        required: ['query'],
        additionalProperties: false
      }
    },
    required: ['intent', 'confidence', 'parameters']
  },
  AnalyzeSpreadsheet: {
    type: 'object',
    properties: {
      intent: { type: 'string', const: 'AnalyzeSpreadsheet' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', pattern: '\\.(csv|xlsx|xls|ods)$' },
          op: { type: 'string', enum: ['sum', 'avg', 'count', 'total'] },
          column: { type: 'string', minLength: 1, maxLength: 100 }
        },
        required: ['path', 'op', 'column'],
        additionalProperties: false
      }
    },
    required: ['intent', 'confidence', 'parameters']
  },
  SummarizeDoc: {
    type: 'object',
    properties: {
      intent: { type: 'string', const: 'SummarizeDoc' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', pattern: '\\.pdf$' },
          length: { type: 'string', enum: ['short', 'bullets', 'tweet'] }
        },
        required: ['path', 'length'],
        additionalProperties: false
      }
    },
    required: ['intent', 'confidence', 'parameters']
  }
};

export interface ParseError {
  error: {
    code: 'INTENT_PARSE_FAILED' | 'AMBIGUOUS_INTENT' | 'MISSING_PARAMETERS' | 
          'INVALID_PARAMETERS' | 'LOW_CONFIDENCE' | 'UNSUPPORTED_OPERATION' | 'CONTEXT_REQUIRED';
    message: string;
    details?: {
      userInput: string;
      confidence?: number | undefined;
      missingFields?: string[] | undefined;
      invalidFields?: Array<{
        field: string;
        value: any;
        reason: string;
      }> | undefined;
    };
  };
  suggestions: Array<{
    type: 'rephrase' | 'clarify' | 'example' | 'alternative';
    message: string;
    example?: string;
  }>;
  context?: {
    sessionId: string;
    timestamp: string;
    userInput: string;
  };
}

export interface ParsedIntent {
  intent: 'CreateFile' | 'OpenItem' | 'AnalyzeSpreadsheet' | 'SummarizeDoc';
  confidence: number;
  parameters: Record<string, any>;
  context?: {
    sessionId: string;
    timestamp: string;
    userInput: string;
  };
}

// GPT-4o Function definitions for intent parsing
const INTENT_FUNCTIONS = [
  {
    name: 'create_file',
    description: 'Create a new file with optional content',
    parameters: {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Name of the file to create (with extension)'
        },
        path: {
          type: 'string',
          description: 'Optional directory path where file should be created'
        },
        content: {
          type: 'string',
          description: 'Optional initial content for the file'
        },
        confidence: {
          type: 'number',
          description: 'Confidence score from 0.0 to 1.0'
        }
      },
      required: ['title', 'confidence']
    }
  },
  {
    name: 'open_item',
    description: 'Open a file, application, or folder',
    parameters: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query for the item to open (file name, app name, etc.)'
        },
        type: {
          type: 'string',
          enum: ['file', 'application', 'folder', 'auto'],
          description: 'Type of item to open - auto will attempt to determine type'
        },
        confidence: {
          type: 'number',
          description: 'Confidence score from 0.0 to 1.0'
        }
      },
      required: ['query', 'confidence']
    }
  },
  {
    name: 'analyze_spreadsheet',
    description: 'Perform analysis operations on spreadsheet data',
    parameters: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the spreadsheet file (CSV, XLSX, XLS, ODS)'
        },
        op: {
          type: 'string',
          enum: ['sum', 'avg', 'count', 'total'],
          description: 'Operation to perform on the data'
        },
        column: {
          type: 'string',
          description: 'Column name or identifier to analyze'
        },
        confidence: {
          type: 'number',
          description: 'Confidence score from 0.0 to 1.0'
        }
      },
      required: ['path', 'op', 'column', 'confidence']
    }
  },
  {
    name: 'summarize_document',
    description: 'Summarize a PDF document',
    parameters: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the PDF document to summarize'
        },
        length: {
          type: 'string',
          enum: ['short', 'bullets', 'tweet'],
          description: 'Desired summary format and length'
        },
        confidence: {
          type: 'number',
          description: 'Confidence score from 0.0 to 1.0'
        }
      },
      required: ['path', 'length', 'confidence']
    }
  }
];

class IntentParser {
  private apiKey: string;
  private sessionId: string;

  constructor(apiKey: string, sessionId: string = 'default') {
    this.apiKey = apiKey;
    this.sessionId = sessionId;
  }

  async parseIntent(text: string): Promise<ParsedIntent | ParseError> {
    try {
      // Call GPT-4o with function calling
      const response = await this.callGPT4o(text);
      
      if (!response.choices?.[0]?.message?.function_call) {
        return this.createParseError(text, 'INTENT_PARSE_FAILED', 
          'No valid intent could be determined from the input');
      }

      const functionCall = response.choices[0].message.function_call;
      const parsedIntent = this.processFunctionCall(functionCall, text);
      
      // Validate the parsed intent
      const validationResult = this.validateIntent(parsedIntent);
      if (validationResult !== true) {
        return validationResult;
      }

      return parsedIntent;
    } catch (error) {
      console.error('Intent parsing error:', error);
      return this.createParseError(text, 'INTENT_PARSE_FAILED', 
        `Failed to parse intent: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  private async callGPT4o(text: string): Promise<any> {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: `You are an intent parser for a desktop assistant. Parse user commands into structured intents.
            
Available intents:
- create_file: Create new files with optional content
- open_item: Open files, applications, or folders
- analyze_spreadsheet: Perform calculations on spreadsheet data
- summarize_document: Summarize PDF documents

Always provide a confidence score between 0.0 and 1.0. Use function calling to return structured data.
If the intent is unclear or ambiguous, use a lower confidence score.`
          },
          {
            role: 'user',
            content: text
          }
        ],
        functions: INTENT_FUNCTIONS,
        function_call: 'auto',
        temperature: 0.1,
        max_tokens: 500
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  private processFunctionCall(functionCall: any, originalText: string): ParsedIntent {
    const { name, arguments: args } = functionCall;
    const parsedArgs = JSON.parse(args);
    
    const intentMap: Record<string, string> = {
      'create_file': 'CreateFile',
      'open_item': 'OpenItem',
      'analyze_spreadsheet': 'AnalyzeSpreadsheet',
      'summarize_document': 'SummarizeDoc'
    };

    const intent = intentMap[name];
    if (!intent) {
      throw new Error(`Unknown function: ${name}`);
    }

    // Extract confidence and remove it from parameters
    const { confidence, ...parameters } = parsedArgs;

    return {
      intent: intent as any,
      confidence: confidence || 0.5,
      parameters,
      context: {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        userInput: originalText
      }
    };
  }

  private validateIntent(intent: ParsedIntent): true | ParseError {
    const schema = INTENT_SCHEMAS[intent.intent];
    if (!schema) {
      return this.createParseError(intent.context?.userInput || '', 'UNSUPPORTED_OPERATION',
        `Unsupported intent: ${intent.intent}`);
    }

    // Check confidence threshold
    if (intent.confidence < 0.7) {
      return this.createParseError(intent.context?.userInput || '', 'LOW_CONFIDENCE',
        'Intent confidence is too low, please be more specific', intent.confidence);
    }

    // Validate against JSON schema
    const validationErrors = this.validateAgainstSchema(intent, schema);
    if (validationErrors.length > 0) {
      return this.createValidationError(intent.context?.userInput || '', validationErrors);
    }

    return true;
  }

  private validateAgainstSchema(intent: ParsedIntent, schema: any): Array<{field: string, value: any, reason: string}> {
    const errors: Array<{field: string, value: any, reason: string}> = [];
    
    // Check required parameters
    if (schema.properties?.parameters?.required) {
      for (const field of schema.properties.parameters.required) {
        if (!(field in intent.parameters)) {
          errors.push({
            field,
            value: undefined,
            reason: 'Required parameter is missing'
          });
        }
      }
    }

    // Validate parameter types and constraints
    if (schema.properties?.parameters?.properties) {
      for (const [field, fieldSchema] of Object.entries(schema.properties.parameters.properties as any)) {
        const value = intent.parameters[field];
        if (value !== undefined) {
          const fieldError = this.validateField(field, value, fieldSchema);
          if (fieldError) {
            errors.push(fieldError);
          }
        }
      }
    }

    return errors;
  }

  private validateField(field: string, value: any, schema: any): {field: string, value: any, reason: string} | null {
    // Type validation
    if (schema.type && typeof value !== schema.type) {
      return { field, value, reason: `Expected ${schema.type}, got ${typeof value}` };
    }

    // String validations
    if (schema.type === 'string') {
      if (schema.minLength && value.length < schema.minLength) {
        return { field, value, reason: `Minimum length is ${schema.minLength}` };
      }
      if (schema.maxLength && value.length > schema.maxLength) {
        return { field, value, reason: `Maximum length is ${schema.maxLength}` };
      }
      if (schema.pattern && !new RegExp(schema.pattern).test(value)) {
        return { field, value, reason: 'Value does not match required pattern' };
      }
      if (schema.enum && !schema.enum.includes(value)) {
        return { field, value, reason: `Value must be one of: ${schema.enum.join(', ')}` };
      }
    }

    // Number validations
    if (schema.type === 'number') {
      if (schema.minimum !== undefined && value < schema.minimum) {
        return { field, value, reason: `Minimum value is ${schema.minimum}` };
      }
      if (schema.maximum !== undefined && value > schema.maximum) {
        return { field, value, reason: `Maximum value is ${schema.maximum}` };
      }
    }

    return null;
  }

  private createParseError(
    userInput: string, 
    code: ParseError['error']['code'], 
    message: string, 
    confidence?: number
  ): ParseError {
    const suggestions = this.generateSuggestions(code, userInput);
    
    return {
      error: {
        code,
        message,
        details: {
          userInput,
          confidence
        }
      },
      suggestions,
      context: {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        userInput
      }
    };
  }

  private createValidationError(userInput: string, validationErrors: Array<{field: string, value: any, reason: string}>): ParseError {
    const missingFields = validationErrors
      .filter(e => e.value === undefined)
      .map(e => e.field);
    
    const invalidFields = validationErrors
      .filter(e => e.value !== undefined);

    return {
      error: {
        code: missingFields.length > 0 ? 'MISSING_PARAMETERS' : 'INVALID_PARAMETERS',
        message: missingFields.length > 0 ? 'Required parameters are missing' : 'One or more parameters are invalid',
        details: {
          userInput,
          missingFields: missingFields.length > 0 ? missingFields : undefined,
          invalidFields: invalidFields.length > 0 ? invalidFields : undefined
        }
      },
      suggestions: this.generateValidationSuggestions(validationErrors),
      context: {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        userInput
      }
    };
  }

  private generateSuggestions(code: ParseError['error']['code'], _userInput: string): ParseError['suggestions'] {
    switch (code) {
      case 'INTENT_PARSE_FAILED':
        return [
          {
            type: 'rephrase',
            message: 'Please be more specific about what you\'d like me to do',
            example: 'Try saying "Create a file called notes.txt" or "Open the budget spreadsheet"'
          },
          {
            type: 'example',
            message: 'Here are some things I can help with:',
            example: '• Create and edit files\n• Analyze spreadsheet data\n• Summarize PDF documents\n• Open files and applications'
          }
        ];
      
      case 'LOW_CONFIDENCE':
        return [
          {
            type: 'clarify',
            message: 'I\'m not sure what you want me to do. Could you be more specific?',
            example: 'Try adding more details about the file, operation, or location'
          }
        ];
      
      case 'AMBIGUOUS_INTENT':
        return [
          {
            type: 'clarify',
            message: 'Your request could mean several things. Please clarify:',
            example: 'Are you trying to create, open, or analyze something?'
          }
        ];
      
      default:
        return [
          {
            type: 'rephrase',
            message: 'Please try rephrasing your request',
            example: 'Be more specific about what you want to do'
          }
        ];
    }
  }

  private generateValidationSuggestions(errors: Array<{field: string, value: any, reason: string}>): ParseError['suggestions'] {
    const suggestions: ParseError['suggestions'] = [];
    
    for (const error of errors) {
      if (error.field === 'title' && error.reason.includes('pattern')) {
        suggestions.push({
          type: 'rephrase',
          message: 'File names cannot contain these characters: < > : " | ? *',
          example: 'Try "Create file called report.txt" instead'
        });
      } else if (error.field === 'path' && error.reason.includes('pattern')) {
        suggestions.push({
          type: 'rephrase',
          message: 'Please specify a valid file path',
          example: 'Use "./documents/file.csv" or just "file.csv"'
        });
      } else if (error.value === undefined) {
        suggestions.push({
          type: 'clarify',
          message: `Please specify the ${error.field}`,
          example: `Add information about the ${error.field} you want to use`
        });
      }
    }
    
    if (suggestions.length === 0) {
      suggestions.push({
        type: 'rephrase',
        message: 'Please check your input and try again',
        example: 'Make sure all required information is provided'
      });
    }
    
    return suggestions;
  }
}

// Factory function to create parser with API key
export const createIntentParser = (apiKey: string, sessionId?: string): IntentParser => {
  return new IntentParser(apiKey, sessionId);
};

// Main parsing function
export const parseIntent = async (text: string, apiKey?: string): Promise<ParsedIntent | ParseError> => {
  const key = apiKey || process.env.REACT_APP_OPENAI_API_KEY;
  if (!key) {
    throw new Error('OpenAI API key is required for intent parsing');
  }
  
  const parser = createIntentParser(key);
  return await parser.parseIntent(text);
};