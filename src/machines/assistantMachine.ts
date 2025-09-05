import { createMachine, assign, fromPromise } from 'xstate';
import { AssistantContext, Settings, Intent } from '../types';

const defaultSettings: Settings = {
  sttProvider: 'whisper',
  allowCloudNLP: true,
  ttsProvider: 'system',
};

export const orchestratorMachine = createMachine({
  id: 'orchestrator',
  initial: 'idle',
  context: {
    input: '',
    result: '',
    isRecording: false,
    settings: defaultSettings,
    intent: null,
    error: null,
    isVisible: true,
    inputMode: 'text', // 'text' | 'voice'
    executionResult: null,
  } as AssistantContext,
  states: {
    idle: {
      entry: assign({
        input: '',
        result: '',
        intent: null,
        error: null,
        isRecording: false,
      }),
      on: {
        HOTKEY_TOGGLE: {
          actions: assign({
            isVisible: ({ context }) => !context.isVisible,
          }),
        },
        TEXT_SUBMIT: {
          target: 'parseIntent',
          guard: 'isTextMode',
          actions: assign({
            input: ({ event }) => event.text,
            inputMode: 'text',
          }),
        },
        START_CAPTURE: {
          target: 'capture',
          guard: 'isVoiceMode',
          actions: assign({
            inputMode: 'voice',
          }),
        },
        UPDATE_SETTINGS: {
          actions: assign({
            settings: ({ event }) => event.settings,
          }),
        },
      },
    },
    capture: {
      entry: [
        assign({ isRecording: true }),
        'startRecording',
      ],
      exit: [
        assign({ isRecording: false }),
        'stopRecording',
      ],
      on: {
        STT_RESULT: {
          target: 'parseIntent',
          actions: assign({
            input: ({ event }) => event.text,
          }),
        },
        CANCEL: 'idle',
        HOTKEY_TOGGLE: 'idle',
      },
    },
    parseIntent: {
      invoke: {
        src: 'parseIntent',
        input: ({ context }) => ({
          text: context.input,
          settings: context.settings,
        }),
        onDone: {
          target: 'route',
          actions: assign({
            intent: ({ event }) => event.output,
          }),
        },
        onError: {
          target: 'recover',
          actions: [
            assign({
              error: ({ event }: { event: any }) => event.error?.message || 'Failed to parse intent',
            }),
            'showError',
          ],
        },
      },
    },
    route: {
      always: [
        {
          target: 'execute',
          guard: ({ context }) => context.intent?.action !== 'unknown',
        },
        {
          target: 'recover',
          actions: [
            assign({
              error: 'Could not understand the command',
            }),
            'showError',
          ],
        },
      ],
    },
    execute: {
      invoke: {
        src: 'executeCommand',
        input: ({ context }) => ({
          intent: context.intent,
          settings: context.settings,
        }),
        onDone: [
          {
            target: 'verify',
            guard: ({ event }) => event.output.requiresVerification,
            actions: assign({
              executionResult: ({ event }) => event.output,
            }),
          },
          {
            target: 'respond',
            actions: assign({
              executionResult: ({ event }) => event.output,
              result: ({ event }) => event.output.message,
            }),
          },
        ],
        onError: {
          target: 'recover',
          actions: [
            assign({
              error: ({ event }: { event: any }) => event.error?.message || 'Execution failed',
            }),
            'showError',
          ],
        },
      },
      on: {
        EXEC_ERR: {
          target: 'recover',
          actions: [
            assign({
              error: ({ event }) => event.message,
            }),
            'showError',
          ],
        },
      },
    },
    verify: {
      entry: 'requestVerification',
      on: {
        VERIFY_OK: {
          target: 'respond',
          actions: assign({
            result: ({ context }) => context.executionResult?.message || 'Operation completed',
          }),
        },
        VERIFY_ERR: {
          target: 'recover',
          actions: [
            assign({
              error: 'Operation cancelled by user',
            }),
            'showError',
          ],
        },
        CANCEL: 'idle',
      },
    },
    respond: {
      entry: [
        assign({
          result: ({ context }) => context.executionResult?.message || context.result,
        }),
        'speak',
      ],
      invoke: {
        src: 'generateResponse',
        input: ({ context }) => ({
          result: context.result,
          settings: context.settings,
        }),
        onDone: {
          target: 'idle',
          actions: assign({
            result: ({ event }) => event.output,
          }),
        },
        onError: 'idle',
      },
      after: {
        5000: 'idle',
      },
      on: {
        HOTKEY_TOGGLE: 'idle',
        CANCEL: 'idle',
      },
    },
    recover: {
      entry: 'speak',
      after: {
        3000: 'idle',
      },
      on: {
        HOTKEY_TOGGLE: 'idle',
        CANCEL: 'idle',
        TEXT_SUBMIT: {
          target: 'parseIntent',
          guard: 'isTextMode',
          actions: assign({
            input: ({ event }) => event.text,
            error: null,
          }),
        },
      },
    },
  },
}, {
  guards: {
    isTextMode: ({ context }) => context.inputMode === 'text',
    isVoiceMode: ({ context }) => context.inputMode === 'voice' || context.settings.sttProvider !== 'none',
    cloudAllowed: ({ context }) => context.settings.allowCloudNLP,
  },
  
  // mapActionToIntent removed - causing type issues
  actions: {
    speak: ({ context }) => {
      const textToSpeak = context.error || context.result;
      if (textToSpeak && context.settings.ttsProvider !== 'none') {
        // TTS will be handled by the service
        console.log('Speaking:', textToSpeak);
      }
    },
    showError: ({ context }) => {
      console.error('Assistant Error:', context.error);
      // UI error display implementation
    },
    startRecording: () => {
      console.log('Starting voice recording...');
      // Voice recording will be handled by the service
    },
    stopRecording: () => {
      console.log('Stopping voice recording...');
      // Stop voice recording will be handled by the service
    },
    requestVerification: ({ context }) => {
      console.log('Requesting verification for:', context.executionResult);
      // Show verification dialog
    },
  },
  actors: {
    parseIntent: fromPromise(async ({ input }: { input: { text: string; settings: Settings } }) => {
      const { text, settings } = input;
      
      if (settings.allowCloudNLP) {
        // Try Kiro agent first for intelligent routing
        try {
          const { kiroAgent } = await import('../services/kiroAgent');
          const analysis = kiroAgent.analyzeInput(text);
          
          if (analysis.confidence > 0.7) {
            // Extract parameters using Kiro agent
            const parameters = kiroAgent['extractParameters'](analysis.tool, text);
            
            return {
              action: analysis.tool,
              parameters,
              confidence: analysis.confidence,
            };
          }
        } catch (error) {
          console.warn('Kiro agent parsing failed, falling back to GPT-4o:', error);
        }
        
        // Fallback to GPT-4o for intent parsing
        const { parseIntent } = await import('../services/intentParser');
        const result = await parseIntent(text);
        
        if ('error' in result) {
          throw new Error(`Intent parsing failed: ${result.error.message}`);
        }
        
        // Convert ParsedIntent to legacy Intent format for compatibility
        return {
          action: result.intent.toLowerCase(),
          parameters: result.parameters,
          confidence: result.confidence,
        };
      } else {
        // Use Kiro agent for local pattern matching
        try {
          const { kiroAgent } = await import('../services/kiroAgent');
          const analysis = kiroAgent.analyzeInput(text);
          const parameters = kiroAgent['extractParameters'](analysis.tool, text);
          
          return {
            action: analysis.tool,
            parameters,
            confidence: analysis.confidence,
          };
        } catch (error) {
          console.warn('Kiro agent local parsing failed:', error);
          
          // Final fallback to simple pattern matching
          await new Promise(resolve => setTimeout(resolve, 500));
          
          const lowerText = text.toLowerCase();
          
          if (lowerText.includes('create') && lowerText.includes('file')) {
            return {
              action: 'create_file',
              parameters: { 
                title: text.match(/create.*?file.*?(?:called|named)?\s*([^\s]+)/i)?.[1] || 'untitled.txt',
                content: ''
              },
              confidence: 0.8,
            };
          } else if (lowerText.includes('open')) {
            return {
              action: 'open_item',
              parameters: { 
                query: text.replace(/open\s+/i, ''),
                type: 'auto'
              },
              confidence: 0.75,
            };
          } else if (lowerText.includes('sum') || lowerText.includes('analyze')) {
            return {
              action: 'analyze_sheet',
              parameters: { 
                path: 'data.csv',
                op: 'sum',
                column: 'value'
              },
              confidence: 0.7,
            };
          } else {
            return {
              action: 'create_file',
              parameters: { title: 'untitled.txt', content: text },
              confidence: 0.6,
            };
          }
        }
      }
    }),
    
    executeCommand: fromPromise(async ({ input }: { input: { intent: Intent; settings: Settings } }) => {
      const { intent, settings: _settings } = input;
      
      // Import router actions dynamically to avoid circular dependencies
      const { executeIntent } = await import('../services/routerActions');
      
      // Convert legacy intent format to ParsedIntent format
      const parsedIntent = {
        intent: (intent?.action as 'CreateFile' | 'OpenItem' | 'AnalyzeSpreadsheet' | 'SummarizeDoc') || 'CreateFile',
        confidence: intent.confidence,
        parameters: intent.parameters,
        context: {
          sessionId: 'default',
          timestamp: new Date().toISOString(),
          userInput: 'command execution'
        }
      };
      
      // Execute the intent with progress tracking
      const result = await executeIntent(parsedIntent, (progress) => {
        // Progress updates could be sent to the UI here
        console.log('Execution progress:', progress);
      });
      
      return {
        success: result.success,
        message: result.message,
        requiresVerification: result.requiresVerification || false,
        data: result.data
      };
    }),
    
    generateResponse: fromPromise(async ({ input }: { input: { result: string; settings: Settings } }) => {
      // Simulate response generation
      await new Promise(resolve => setTimeout(resolve, 800));
      return input.result;
    }),
  },
});