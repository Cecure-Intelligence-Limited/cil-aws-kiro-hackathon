/**
 * Intent Recognition Tests
 * Tests 20 utterances against expected intents using Vitest
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { kiroAgent } from '../services/kiroAgent';

describe('Intent Recognition', () => {
  let agent: typeof kiroAgent;

  beforeEach(() => {
    agent = kiroAgent;
  });

  const testCases = [
    // CreateFile Intent Tests
    {
      utterance: 'Create a file called notes.txt',
      expectedTool: 'create_file',
      expectedParams: { title: 'notes.txt' },
      minConfidence: 0.8,
      description: 'Simple file creation'
    },
    {
      utterance: 'Make a new document named report.docx with quarterly data',
      expectedTool: 'create_file',
      expectedParams: { title: 'report.docx', content: 'quarterly data' },
      minConfidence: 0.7,
      description: 'File creation with content'
    },
    {
      utterance: 'Write a file called config.json in the settings folder',
      expectedTool: 'create_file',
      expectedParams: { title: 'config.json', path: 'settings' },
      minConfidence: 0.75,
      description: 'File creation with path'
    },
    {
      utterance: 'Generate a new text file with meeting notes',
      expectedTool: 'create_file',
      expectedParams: { title: expect.stringContaining('.txt') },
      minConfidence: 0.7,
      description: 'File generation with content description'
    },
    {
      utterance: 'Create README.md with project documentation',
      expectedTool: 'create_file',
      expectedParams: { title: 'README.md', content: 'project documentation' },
      minConfidence: 0.8,
      description: 'Markdown file creation'
    },

    // OpenItem Intent Tests
    {
      utterance: 'Open Visual Studio Code',
      expectedTool: 'open_item',
      expectedParams: { query: 'Visual Studio Code', type: 'application' },
      minConfidence: 0.85,
      description: 'Application launch'
    },
    {
      utterance: 'Launch Chrome browser',
      expectedTool: 'open_item',
      expectedParams: { query: 'Chrome', type: 'application' },
      minConfidence: 0.8,
      description: 'Browser launch'
    },
    {
      utterance: 'Open the budget spreadsheet',
      expectedTool: 'open_item',
      expectedParams: { query: 'budget spreadsheet' },
      minConfidence: 0.75,
      description: 'File opening by description'
    },
    {
      utterance: 'Show me the Documents folder',
      expectedTool: 'open_item',
      expectedParams: { query: 'Documents', type: 'folder' },
      minConfidence: 0.8,
      description: 'Folder opening'
    },
    {
      utterance: 'Start Notepad',
      expectedTool: 'open_item',
      expectedParams: { query: 'Notepad', type: 'application' },
      minConfidence: 0.85,
      description: 'Simple application launch'
    },

    // AnalyzeSpreadsheet Intent Tests
    {
      utterance: 'Sum the salary column in employees.csv',
      expectedTool: 'analyze_sheet',
      expectedParams: { path: 'employees.csv', op: 'sum', column: 'salary' },
      minConfidence: 0.9,
      description: 'Sum operation on CSV'
    },
    {
      utterance: 'Calculate the average revenue from sales_data.xlsx',
      expectedTool: 'analyze_sheet',
      expectedParams: { path: 'sales_data.xlsx', op: 'avg', column: 'revenue' },
      minConfidence: 0.85,
      description: 'Average calculation on Excel'
    },
    {
      utterance: 'Count the entries in the status column of tasks.csv',
      expectedTool: 'analyze_sheet',
      expectedParams: { path: 'tasks.csv', op: 'count', column: 'status' },
      minConfidence: 0.8,
      description: 'Count operation'
    },
    {
      utterance: 'Total up the amount column in finance.xlsx',
      expectedTool: 'analyze_sheet',
      expectedParams: { path: 'finance.xlsx', op: 'total', column: 'amount' },
      minConfidence: 0.85,
      description: 'Total calculation'
    },
    {
      utterance: 'What is the mean of the price column in products.csv?',
      expectedTool: 'analyze_sheet',
      expectedParams: { path: 'products.csv', op: 'avg', column: 'price' },
      minConfidence: 0.8,
      description: 'Mean calculation (synonym for average)'
    },

    // SummarizeDoc Intent Tests
    {
      utterance: 'Summarize the quarterly report in bullet points',
      expectedTool: 'summarize_doc',
      expectedParams: { path: 'quarterly report', length: 'bullets' },
      minConfidence: 0.85,
      description: 'Bullet point summary'
    },
    {
      utterance: 'Give me a short summary of research-paper.pdf',
      expectedTool: 'summarize_doc',
      expectedParams: { path: 'research-paper.pdf', length: 'short' },
      minConfidence: 0.8,
      description: 'Short summary'
    },
    {
      utterance: 'Explain the main points in the meeting-minutes.pdf',
      expectedTool: 'summarize_doc',
      expectedParams: { path: 'meeting-minutes.pdf' },
      minConfidence: 0.75,
      description: 'Document explanation'
    },
    {
      utterance: 'Create a tweet-length summary of the annual-report.pdf',
      expectedTool: 'summarize_doc',
      expectedParams: { path: 'annual-report.pdf', length: 'tweet' },
      minConfidence: 0.8,
      description: 'Tweet-length summary'
    },
    {
      utterance: 'Find the key points in documentation.pdf',
      expectedTool: 'summarize_doc',
      expectedParams: { path: 'documentation.pdf', length: 'bullets' },
      minConfidence: 0.75,
      description: 'Key points extraction'
    }
  ];

  testCases.forEach((testCase, index) => {
    it(`should recognize intent ${index + 1}: ${testCase.description}`, () => {
      const analysis = agent.analyzeInput(testCase.utterance);
      
      // Check tool selection
      expect(analysis.tool).toBe(testCase.expectedTool);
      
      // Check confidence threshold
      expect(analysis.confidence).toBeGreaterThanOrEqual(testCase.minConfidence);
      
      // Extract parameters for validation
      const extractedParams = agent['extractParameters'](analysis.tool, testCase.utterance);
      
      // Validate expected parameters
      Object.entries(testCase.expectedParams).forEach(([key, expectedValue]) => {
        if (typeof expectedValue === 'string') {
          if (expectedValue.includes('expect.')) {
            // Handle expect matchers
            return;
          }
          expect(extractedParams[key]).toContain(expectedValue);
        } else {
          expect(extractedParams[key]).toBe(expectedValue);
        }
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle ambiguous input with low confidence', () => {
      const analysis = agent.analyzeInput('do something');
      expect(analysis.confidence).toBeLessThan(0.5);
    });

    it('should handle empty input gracefully', () => {
      const analysis = agent.analyzeInput('');
      expect(analysis.tool).toBe('create_file'); // fallback
      expect(analysis.confidence).toBeLessThan(0.4);
    });

    it('should handle very long input', () => {
      const longInput = 'create a file '.repeat(50) + 'test.txt';
      const analysis = agent.analyzeInput(longInput);
      expect(analysis.tool).toBe('create_file');
      expect(analysis.confidence).toBeGreaterThan(0.7);
    });

    it('should handle mixed case input', () => {
      const analysis = agent.analyzeInput('CREATE A FILE CALLED TEST.TXT');
      expect(analysis.tool).toBe('create_file');
      expect(analysis.confidence).toBeGreaterThan(0.7);
    });

    it('should handle input with special characters', () => {
      const analysis = agent.analyzeInput('create file "test-file_v2.txt" with content!');
      expect(analysis.tool).toBe('create_file');
      expect(analysis.confidence).toBeGreaterThan(0.7);
    });
  });

  describe('Parameter Extraction', () => {
    it('should extract file extensions correctly', () => {
      const params = agent['extractParameters']('create_file', 'create notes.txt');
      expect(params.title).toBe('notes.txt');
    });

    it('should extract paths correctly', () => {
      const params = agent['extractParameters']('create_file', 'create file in ./documents folder');
      expect(params.path).toContain('documents');
    });

    it('should extract content from quotes', () => {
      const params = agent['extractParameters']('create_file', 'create file with "hello world"');
      expect(params.content).toBe('hello world');
    });

    it('should handle missing parameters gracefully', () => {
      const params = agent['extractParameters']('analyze_sheet', 'analyze some data');
      expect(params.path).toBeDefined();
      expect(params.op).toBeDefined();
      expect(params.column).toBeDefined();
    });
  });
});