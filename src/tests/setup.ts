/**
 * Vitest setup file
 */

import { vi } from 'vitest';

// Mock fetch for API calls
global.fetch = vi.fn();

// Mock environment variables
process.env.REACT_APP_OPENAI_API_KEY = 'test-key';

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
};