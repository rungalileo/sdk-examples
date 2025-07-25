import { GalileoAgentLogger } from '../src/utils/GalileoLogger';
import { AgentMetrics } from '../src/types';

// Mock the galileo package
jest.mock('galileo', () => ({
  GalileoLogger: jest.fn().mockImplementation(() => ({
    startTrace: jest.fn(),
    addLlmSpan: jest.fn(),
    addToolSpan: jest.fn(),
    conclude: jest.fn(),
    flush: jest.fn().mockResolvedValue(void 0),
  }))
}));

describe('GalileoLogger Flush Behavior Tests', () => {
  let galileoLogger: GalileoAgentLogger;
  let consoleSpy: jest.SpyInstance;
  let mockGalileoLoggerInstance: any;

  beforeEach(() => {
    // Mock console.log to capture output
    consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {});
    
    // Create a new instance of GalileoAgentLogger
    galileoLogger = new GalileoAgentLogger();
    
    // Access the mocked internal logger
    mockGalileoLoggerInstance = (galileoLogger as any).logger;
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    jest.clearAllMocks();
  });

  describe('Queue and Flush Behavior', () => {
    it('should queue traces without immediately flushing', () => {
      const mockMetrics: AgentMetrics = {
        executionTime: 1000,
        success: true,
        toolsUsed: ['list_products', 'list_prices']
      };

      // Queue multiple traces
      galileoLogger.queue(mockMetrics, 'Show me products', 'Here are the products...');
      galileoLogger.queue(mockMetrics, 'What are prices?', 'Here are the prices...');
      galileoLogger.queue(mockMetrics, 'Create payment link', 'Payment link created...');

      // Verify internal flush method hasn't been called yet
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();
      
      // Verify no flush messages in console
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).not.toContain('📊 Buffered traces flushed');
    });

    it('should flush all queued traces when flushBuffered is called', async () => {
      const mockMetrics: AgentMetrics = {
        executionTime: 1500,
        success: true,
        toolsUsed: ['create_payment_link']
      };

      // Queue some traces
      galileoLogger.queue(mockMetrics, 'User input 1', 'Agent response 1');
      galileoLogger.queue(mockMetrics, 'User input 2', 'Agent response 2');
      galileoLogger.queue(mockMetrics, 'User input 3', 'Agent response 3');

      // Verify no flush has happened yet
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();

      // Call flushBuffered
      await galileoLogger.flushBuffered();

      // Verify flush was called (once for each trace + final flush)
      expect(mockGalileoLoggerInstance.flush).toHaveBeenCalled();
      
      // Verify flush message appeared in console
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 Buffered traces flushed');
    });

    it('should handle empty queue gracefully', async () => {
      // Call flushBuffered with no queued traces
      await galileoLogger.flushBuffered();

      // Should still call flush and show message
      expect(mockGalileoLoggerInstance.flush).toHaveBeenCalledTimes(1);
      
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 Buffered traces flushed');
    });

    it('should clear queue after flushing', async () => {
      const mockMetrics: AgentMetrics = {
        executionTime: 800,
        success: true,
        toolsUsed: ['list_products']
      };

      // Queue traces
      galileoLogger.queue(mockMetrics, 'Test input', 'Test output');
      
      // Verify queue has content (indirectly by checking internal state)
      expect((galileoLogger as any).pendingTraces).toHaveLength(1);

      // Flush
      await galileoLogger.flushBuffered();

      // Verify queue is cleared
      expect((galileoLogger as any).pendingTraces).toHaveLength(0);
    });

    it('should handle flush errors gracefully', async () => {
      // Mock flush to throw an error
      mockGalileoLoggerInstance.flush.mockRejectedValueOnce(new Error('Network error'));
      
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      const mockMetrics: AgentMetrics = {
        executionTime: 500,
        success: false,
        toolsUsed: []
      };

      galileoLogger.queue(mockMetrics, 'Test input', 'Test output');

      // Should not throw error
      await expect(galileoLogger.flushBuffered()).resolves.not.toThrow();

      // Should log error to console
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Failed to log to Galileo:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Session Management', () => {
    it('should start session without immediately flushing', async () => {
      const sessionId = await galileoLogger.startSession('Test Session');
      
      expect(sessionId).toBeTruthy();
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();
      
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).not.toContain('📊 Buffered traces flushed');
    });

    it('should conclude session with flush', async () => {
      // Start session and queue some traces
      await galileoLogger.startSession('Test Session');
      
      const mockMetrics: AgentMetrics = {
        executionTime: 1200,
        success: true,
        toolsUsed: ['create_customer']
      };
      
      galileoLogger.queue(mockMetrics, 'Create customer', 'Customer created');

      // Conclude session
      await galileoLogger.concludeSession();

      // Should have flushed traces and concluded session
      expect(mockGalileoLoggerInstance.flush).toHaveBeenCalled();
      
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 Session concluded');
    });

    it('should prevent multiple session starts', async () => {
      // Start first session
      const sessionId1 = await galileoLogger.startSession('Session 1');
      
      // Try to start second session - should return same ID
      const sessionId2 = await galileoLogger.startSession('Session 2');
      
      expect(sessionId1).toBe(sessionId2);
    });

    it('should allow new session after conclusion', async () => {
      // Start and conclude first session
      const sessionId1 = await galileoLogger.startSession('Session 1');
      await galileoLogger.concludeSession();
      
      // Start new session
      const sessionId2 = await galileoLogger.startSession('Session 2');
      
      expect(sessionId1).not.toBe(sessionId2);
    });
  });

  describe('Conversation Logging', () => {
    it('should log conversation without flushing', async () => {
      const mockMessages = [
        { role: 'user', content: 'Hello', timestamp: new Date() },
        { role: 'assistant', content: 'Hi there!', timestamp: new Date() },
        { role: 'user', content: 'Show me products', timestamp: new Date() },
        { role: 'assistant', content: 'Here are our products...', timestamp: new Date() }
      ];

      await galileoLogger.logConversation(mockMessages as any);

      // Should not automatically flush
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();
      
      // Should log conversation summary
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 4 messages logged to Galileo');
    });

    it('should log satisfaction without auto-flushing', async () => {
      await galileoLogger.logSatisfaction(true);

      // Should not automatically flush
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();
      
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 Satisfaction logged: 👍');
    });

    it('should log negative satisfaction correctly', async () => {
      await galileoLogger.logSatisfaction(false);

      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 Satisfaction logged: 👎');
    });
  });

  describe('Integration: Complete Workflow', () => {
    it('should handle complete workflow with single flush at end', async () => {
      // Start session
      const sessionId = await galileoLogger.startSession('Complete Workflow Test');
      expect(sessionId).toBeTruthy();

      // Queue multiple traces (simulating conversation)
      const mockMetrics: AgentMetrics = {
        executionTime: 1000,
        success: true,
        toolsUsed: ['list_products']
      };

      galileoLogger.queue(mockMetrics, 'Hello', 'Hi there!');
      galileoLogger.queue(mockMetrics, 'Show products', 'Here are products...');
      galileoLogger.queue(mockMetrics, 'Create payment link', 'Link created...');

      // Log conversation
      const mockMessages = [
        { role: 'user', content: 'Hello', timestamp: new Date() },
        { role: 'assistant', content: 'Hi there!', timestamp: new Date() }
      ];
      await galileoLogger.logConversation(mockMessages as any);

      // Log satisfaction
      await galileoLogger.logSatisfaction(true);

      // Verify no flush happened during the workflow
      expect(mockGalileoLoggerInstance.flush).not.toHaveBeenCalled();

      // Conclude session (this should trigger flush)
      await galileoLogger.concludeSession();

      // Verify flush happened exactly once during conclusion
      expect(mockGalileoLoggerInstance.flush).toHaveBeenCalled();
      
      // Verify all expected messages
      const capturedOutput = consoleSpy.mock.calls.flat().join(' ');
      expect(capturedOutput).toContain('📊 2 messages logged to Galileo');
      expect(capturedOutput).toContain('📊 Satisfaction logged: 👍');
      expect(capturedOutput).toContain('📊 Buffered traces flushed');
      expect(capturedOutput).toContain('📊 Session concluded');
    });

    it('should handle multiple flush calls correctly', async () => {
      const mockMetrics: AgentMetrics = {
        executionTime: 1000,
        success: true,
        toolsUsed: ['list_products']
      };

      // Queue a trace
      galileoLogger.queue(mockMetrics, 'Test', 'Response');

      // Call flush multiple times
      await galileoLogger.flushBuffered();
      await galileoLogger.flushBuffered();
      await galileoLogger.flushBuffered();

      // Each call should trigger flush (even if queue is empty after first)
      // The first call processes the trace and flushes, subsequent calls just flush
      expect(mockGalileoLoggerInstance.flush).toHaveBeenCalledTimes(4);
      
      // Verify queue is empty after first flush
      expect((galileoLogger as any).pendingTraces).toHaveLength(0);
    });
  });
});
