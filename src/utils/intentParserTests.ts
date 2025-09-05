import { parseIntent } from '../services/intentParser';
import { ParsedIntent, ParseError } from '../types';

export interface TestCase {
  input: string;
  expectedIntent?: string;
  expectedConfidence?: number;
  shouldFail?: boolean;
  description: string;
}

export const TEST_CASES: TestCase[] = [
  // CreateFile Intent Tests
  {
    input: 'Create a file called meeting-notes.txt',
    expectedIntent: 'CreateFile',
    expectedConfidence: 0.9,
    description: 'Simple file creation'
  },
  {
    input: 'Make a new document named report.docx with quarterly data',
    expectedIntent: 'CreateFile',
    expectedConfidence: 0.85,
    description: 'File creation with content'
  },
  {
    input: 'Create file <invalid>.txt',
    shouldFail: true,
    description: 'Invalid filename characters'
  },

  // OpenItem Intent Tests
  {
    input: 'Open the budget spreadsheet',
    expectedIntent: 'OpenItem',
    expectedConfidence: 0.8,
    description: 'Open file by description'
  },
  {
    input: 'Launch Visual Studio Code',
    expectedIntent: 'OpenItem',
    expectedConfidence: 0.9,
    description: 'Launch application'
  },
  {
    input: 'Open budget.xlsx',
    expectedIntent: 'OpenItem',
    expectedConfidence: 0.95,
    description: 'Open specific file'
  },

  // AnalyzeSpreadsheet Intent Tests
  {
    input: 'Sum the salary column in employees.csv',
    expectedIntent: 'AnalyzeSpreadsheet',
    expectedConfidence: 0.9,
    description: 'Sum operation on CSV'
  },
  {
    input: 'Calculate the average revenue from sales_data.xlsx',
    expectedIntent: 'AnalyzeSpreadsheet',
    expectedConfidence: 0.85,
    description: 'Average operation on Excel file'
  },
  {
    input: 'Count entries in the status column of tasks.csv',
    expectedIntent: 'AnalyzeSpreadsheet',
    expectedConfidence: 0.8,
    description: 'Count operation'
  },
  {
    input: 'Sum the column in file.txt',
    shouldFail: true,
    description: 'Invalid file extension for spreadsheet'
  },

  // SummarizeDoc Intent Tests
  {
    input: 'Summarize the quarterly report in bullet points',
    expectedIntent: 'SummarizeDoc',
    expectedConfidence: 0.85,
    description: 'Summarize with bullet format'
  },
  {
    input: 'Give me a tweet-length summary of research-paper.pdf',
    expectedIntent: 'SummarizeDoc',
    expectedConfidence: 0.9,
    description: 'Tweet-length summary'
  },
  {
    input: 'Summarize document.docx',
    shouldFail: true,
    description: 'Invalid file extension for document summary'
  },

  // Ambiguous/Unclear Intent Tests
  {
    input: 'do something with the thing',
    shouldFail: true,
    description: 'Completely ambiguous input'
  },
  {
    input: 'open report',
    expectedConfidence: 0.6,
    description: 'Ambiguous but parseable'
  },
  {
    input: 'file',
    shouldFail: true,
    description: 'Single word, unclear intent'
  },

  // Edge Cases
  {
    input: '',
    shouldFail: true,
    description: 'Empty input'
  },
  {
    input: 'Create a file with a very long name that exceeds the maximum length limit and should cause validation to fail because it is too long for the system to handle properly',
    shouldFail: true,
    description: 'Filename too long'
  }
];

export interface TestResult {
  testCase: TestCase;
  result: ParsedIntent | ParseError;
  passed: boolean;
  reason?: string;
}

export const runIntentParserTests = async (apiKey?: string): Promise<TestResult[]> => {
  const results: TestResult[] = [];

  for (const testCase of TEST_CASES) {
    try {
      const result = await parseIntent(testCase.input, apiKey);
      const passed = evaluateTestResult(testCase, result);
      
      results.push({
        testCase,
        result,
        passed: passed.success,
        reason: passed.reason || 'No reason provided'
      });
    } catch (error) {
      results.push({
        testCase,
        result: {
          error: {
            code: 'INTENT_PARSE_FAILED',
            message: error instanceof Error ? error.message : 'Unknown error'
          },
          suggestions: []
        } as ParseError,
        passed: testCase.shouldFail === true,
        reason: testCase.shouldFail ? 'Expected failure' : `Unexpected error: ${error}`
      });
    }
  }

  return results;
};

const evaluateTestResult = (testCase: TestCase, result: ParsedIntent | ParseError): { success: boolean; reason?: string } => {
  const isError = 'error' in result;

  // If we expected failure
  if (testCase.shouldFail) {
    if (isError) {
      return { success: true, reason: 'Expected failure occurred' };
    } else {
      return { success: false, reason: 'Expected failure but got success' };
    }
  }

  // If we expected success but got error
  if (isError) {
    return { success: false, reason: `Unexpected error: ${result.error.message}` };
  }

  // Check intent type
  if (testCase.expectedIntent && result.intent !== testCase.expectedIntent) {
    return { 
      success: false, 
      reason: `Expected intent ${testCase.expectedIntent}, got ${result.intent}` 
    };
  }

  // Check confidence threshold
  if (testCase.expectedConfidence && result.confidence < testCase.expectedConfidence) {
    return { 
      success: false, 
      reason: `Expected confidence >= ${testCase.expectedConfidence}, got ${result.confidence}` 
    };
  }

  return { success: true, reason: 'All checks passed' };
};

export const printTestResults = (results: TestResult[]): void => {
  console.log('\n=== Intent Parser Test Results ===\n');
  
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  
  console.log(`Overall: ${passed}/${total} tests passed (${((passed/total) * 100).toFixed(1)}%)\n`);
  
  results.forEach((result, index) => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${index + 1}. ${status} - ${result.testCase.description}`);
    console.log(`   Input: "${result.testCase.input}"`);
    
    if ('error' in result.result) {
      console.log(`   Error: ${result.result.error.code} - ${result.result.error.message}`);
    } else {
      console.log(`   Intent: ${result.result.intent} (confidence: ${(result.result.confidence * 100).toFixed(1)}%)`);
      console.log(`   Parameters: ${JSON.stringify(result.result.parameters)}`);
    }
    
    if (result.reason) {
      console.log(`   Reason: ${result.reason}`);
    }
    console.log('');
  });
};