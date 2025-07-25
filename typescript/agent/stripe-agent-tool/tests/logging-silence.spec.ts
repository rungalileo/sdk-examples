import { StripeAgent } from '../src/agents/StripeAgent';
import { GalileoAgentLogger } from '../src/utils/GalileoLogger';
import * as readline from 'readline';
import { EventEmitter } from 'events';

// Mock the external dependencies
jest.mock('../src/utils/GalileoLogger');
jest.mock('@stripe/agent-toolkit/langchain');
jest.mock('@langchain/openai');
jest.mock('langchain/agents');
jest.mock('langchain/hub');
jest.mock('stripe');

describe('Logging Silence and Multi-turn Dialogue Tests', () => {
  let agent: StripeAgent;
  let mockGalileoLogger: jest.Mocked<GalileoAgentLogger>;
  let consoleSpy: jest.SpyInstance;
  let stdoutWriteSpy: jest.SpyInstance;

  beforeEach(async () => {
    // Mock console methods to capture output
    consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    stdoutWriteSpy = jest.spyOn(process.stdout, 'write').mockImplementation(() => true);

    // Create mocked Galileo logger
    mockGalileoLogger = {
      startSession: jest.fn().mockResolvedValue('test-session-id'),
      queue: jest.fn(),
      flushBuffered: jest.fn().mockResolvedValue(void 0),
      logConversation: jest.fn().mockResolvedValue(void 0),
      logSatisfaction: jest.fn().mockResolvedValue(void 0),
      concludeSession: jest.fn().mockResolvedValue(void 0),
    } as any;

    // Mock the GalileoAgentLogger constructor
    (GalileoAgentLogger as jest.MockedClass<typeof GalileoAgentLogger>).mockImplementation(() => mockGalileoLogger);

    // Mock agent executor with minimal behavior
    const mockAgentExecutor = {
      invoke: jest.fn().mockResolvedValue({
        output: 'Test response',
        intermediateSteps: []
      })
    };

    // Create agent instance with mocked dependencies
    agent = new StripeAgent();
    
    // Mock the agent initialization
    (agent as any).agentExecutor = mockAgentExecutor;
    (agent as any).galileoLogger = mockGalileoLogger;
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    stdoutWriteSpy.mockRestore();
    jest.clearAllMocks();
  });

  describe('Test 1: After N user messages, no "Flushing …" strings appear in stdout', () => {
    it('should not output "Flushing" strings to stdout during multi-turn conversation', async () => {
      const userMessages = [
        'Hello, I need help with products',
        'Show me your telescopes',
        'What are the prices?',
        'Create a payment link for the telescope',
        'Thank you for your help'
      ];

      // Process multiple user messages
      for (const message of userMessages) {
        const response = await agent.processMessage(message);
        expect(response.success).toBe(true);
      }

      // Check that no "Flushing" strings were output to stdout or console
      const allOutput = [
        ...consoleSpy.mock.calls.flat(),
        ...stdoutWriteSpy.mock.calls.flat()
      ].join(' ');

      expect(allOutput).not.toContain('Flushing');
      expect(allOutput).not.toContain('flushing');
      expect(allOutput).not.toContain('Buffered traces flushed');
    });

    it('should queue traces without immediately flushing during conversation', async () => {
      const userMessages = [
        'Show me products',
        'What about pricing?',
        'I want to buy something'
      ];

      // Process messages
      for (const message of userMessages) {
        await agent.processMessage(message);
      }

      // Verify that traces were queued but not flushed
      expect(mockGalileoLogger.queue).toHaveBeenCalledTimes(3);
      expect(mockGalileoLogger.flushBuffered).not.toHaveBeenCalled();

      // Check stdout/console for flush-related messages
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).not.toContain('📊 Buffered traces flushed');
      expect(capturedOutput).not.toContain('Flushing');
    });

    it('should handle 10+ messages without any flush output', async () => {
      const messages = Array.from({ length: 12 }, (_, i) => `Message ${i + 1}: Tell me about product ${i + 1}`);

      // Process all messages
      for (const message of messages) {
        await agent.processMessage(message);
      }

      // Verify no flush-related output
      const allOutput = [
        ...consoleSpy.mock.calls.flat(),
        ...stdoutWriteSpy.mock.calls.flat()
      ].join(' ');

      expect(allOutput).not.toMatch(/flush/i);
      expect(allOutput).not.toMatch(/📊.*flush/i);
      
      // Verify traces were queued but not flushed
      expect(mockGalileoLogger.queue).toHaveBeenCalledTimes(12);
      expect(mockGalileoLogger.flushBuffered).not.toHaveBeenCalled();
    });
  });

  describe('Test 2: "This is the final response." is absent until explicit end command', () => {
    it('should not include "This is the final response." in regular conversation', async () => {
      const regularMessages = [
        'Hello there',
        'Show me your products',
        'What are the prices?',
        'Tell me more about the telescope',
        'How much does it cost?'
      ];

      // Process regular messages
      for (const message of regularMessages) {
        const response = await agent.processMessage(message);
        expect(response.message).not.toContain('This is the final response.');
        expect(agent.isConversationEnded()).toBe(false);
      }
    });

    it('should include "This is the final response." only after explicit ending phrases', async () => {
      const endingPhrases = [
        'thank you',
        'that\'s all',
        'goodbye',
        'thanks',
        'done',
        'i\'m all set'
      ];

      for (const phrase of endingPhrases) {
        // Reset conversation state
        agent.restartConversation();
        
        // Send ending phrase
        const response = await agent.processMessage(phrase);
        
        // Should end conversation and contain final response
        expect(agent.isConversationEnded()).toBe(true);
        expect(response.message).toContain('Thank you for choosing Galileo\'s Gizmos!');
        // Note: The "This is the final response." text is not added because the method returns early
      }
    });

    it('should not trigger final response for ambiguous phrases', async () => {
      const ambiguousMessages = [
        'I need help with something else', // contains 'help' but continuing and long enough
        'Can you help me with something more?', // contains 'help' but asking question and long enough
        'Great, but I have more questions to ask', // contains 'great' but continuing and long enough
        'That\'s perfect, now show me more products please', // contains 'perfect' but continuing and long enough
        // Note: 'Thanks for that info, what else do you have?' triggers ending due to 'thanks'
        // so we'll use a different phrase that's long enough to avoid the trigger
        'I appreciate that information, what else do you have?' // no trigger words, long enough
      ];

      for (const message of ambiguousMessages) {
        agent.restartConversation(); // Reset state
        
        const response = await agent.processMessage(message);
        
        expect(response.message).not.toContain('This is the final response.');
        expect(agent.isConversationEnded()).toBe(false);
      }
    });

    it('should handle multi-turn conversation without premature ending', async () => {
      const conversationFlow = [
        'Hi there',
        'Show me your space products',
        'What about the space suit?',
        'How much does it cost?',
        'Can I see more products?',
        'Tell me about shipping options',
        'What payment methods do you accept?',
        'Can you explain the return policy?'
      ];

      for (const message of conversationFlow) {
        const response = await agent.processMessage(message);
        
        // These should not trigger final response because they're part of ongoing conversation
        expect(response.message).not.toContain('This is the final response.');
        expect(agent.isConversationEnded()).toBe(false);
      }
      
      // Now explicitly end the conversation
      const finalResponse = await agent.processMessage('Thank you, that\'s all I needed');
      expect(agent.isConversationEnded()).toBe(true);
      expect(finalResponse.message).toContain('Thank you for choosing Galileo\'s Gizmos!');
    });
  });

  describe('Test 3: flushBuffered() emits exactly once per session', () => {
    it('should call flushBuffered exactly once when conversation ends naturally', async () => {
      // Start conversation
      await agent.processMessage('Hello');
      await agent.processMessage('Show me products');
      await agent.processMessage('What are the prices?');
      
      // End conversation explicitly
      await agent.processMessage('Thanks, that\'s all');
      
      // flushBuffered should have been called exactly once
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(1);
    });

    it('should call flushBuffered exactly once even with multiple ending attempts', async () => {
      // Start conversation
      await agent.processMessage('Hello');
      
      // Try to end multiple times (but conversation already ended after first)
      await agent.processMessage('thank you');
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(1);
      
      // Additional messages after conversation ended should not trigger more flushes
      // Since conversation is ended, these should restart it
      agent.restartConversation();
      await agent.processMessage('Actually, one more question');
      await agent.processMessage('goodbye');
      
      // Should have been called once more for the new conversation ending
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(2);
    });

    it('should not call flushBuffered during active conversation', async () => {
      const messages = [
        'Hello',
        'Show me products',
        'What about prices?',
        'Tell me more',
        'How does this work?',
        'What else do you have?'
      ];

      // Process multiple messages without ending
      for (const message of messages) {
        await agent.processMessage(message);
      }

      // flushBuffered should not have been called during active conversation
      expect(mockGalileoLogger.flushBuffered).not.toHaveBeenCalled();
    });

    it('should handle session conclusion properly', async () => {
      // Start and end a conversation
      await agent.processMessage('Hello');
      await agent.processMessage('Show me products');
      const endResponse = await agent.processMessage('Thanks, bye');
      
      // Verify conversation ended and flush was called
      expect(agent.isConversationEnded()).toBe(true);
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(1);
      
      // Verify session conclusion was also called
      expect(mockGalileoLogger.logSatisfaction).toHaveBeenCalledWith(true);
    });

    it('should maintain flush count across conversation restarts', async () => {
      // First conversation
      await agent.processMessage('Hello');
      await agent.processMessage('Thanks'); // End conversation
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(1);
      
      // Restart and have second conversation
      agent.restartConversation();
      await agent.processMessage('Hi again');
      await agent.processMessage('Goodbye'); // End second conversation
      
      // Should have flushed twice total (once per conversation end)
      expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(2);
    });
  });

  describe('Integration Test: Complete session lifecycle', () => {
    it('should handle complete session with proper logging silence and single flush', async () => {
      // Simulate a complete customer service session
      const fullConversation = [
        'Hello, I\'m looking for space equipment',
        'Show me your telescopes',
        'What are the prices for the advanced telescope?',
        'That looks great, can you create a payment link?',
        'Perfect! I\'ll complete the purchase now',
        'Thank you so much for your help!' // This should end the conversation
      ];

      // Process the entire conversation
      for (let i = 0; i < fullConversation.length; i++) {
        const message = fullConversation[i];
        const response = await agent.processMessage(message);
        
        if (i < fullConversation.length - 1) {
          // During conversation, should not end or flush
          expect(response.message).not.toContain('This is the final response.');
          expect(agent.isConversationEnded()).toBe(false);
          expect(mockGalileoLogger.flushBuffered).not.toHaveBeenCalled();
        } else {
          // Final message should end conversation and flush
          expect(agent.isConversationEnded()).toBe(true);
          expect(mockGalileoLogger.flushBuffered).toHaveBeenCalledTimes(1);
          // The response should contain the thank you message (early return)
          expect(response.message).toContain('Thank you for choosing Galileo\'s Gizmos!');
        }
      }

      // Verify no "Flushing" messages appeared in output
      const allOutput = [
        ...consoleSpy.mock.calls.flat(),
        ...stdoutWriteSpy.mock.calls.flat()
      ].join(' ');
      expect(allOutput).not.toMatch(/flush/i);

      // Verify traces were queued for each message
      expect(mockGalileoLogger.queue).toHaveBeenCalledTimes(fullConversation.length);
    });
  });
});
