const { init, flush, GalileoCallback } = require('galileo');

/**
 * A simplified Galileo Callback Handler for the Stripe Agent.
 *
 * This handler wraps the official Galileo LangChain callback and provides
 * a clean interface for initialization, retrieval, and flushing of traces.
 * It removes all manual session and trace management in favor of relying
 * on the automated tracing provided by LangChain and Galileo.
 */

// Global suppression for Galileo's noisy debug messages
const originalConsoleDebug = console.debug;
console.debug = (message?: any, ...optionalParams: any[]) => {
  // Convert message to string for checking, handling various input types
  const messageStr = typeof message === 'string' ? message : String(message);
  
  // Suppress various noisy Galileo debug messages
  if (
    messageStr.includes('No node exists for run_id') ||
    messageStr.includes('node exists for run_id') ||  // Catch partial matches too
    messageStr.includes('Galileo debug:') ||
    messageStr.includes('LangChain tracing') ||
    messageStr.includes('run_id') && messageStr.includes('not found') ||
    messageStr.includes('Missing node') ||
    messageStr.includes('Node registry')
  ) {
    return; // Suppress these noisy messages
  }
  originalConsoleDebug(message, ...optionalParams);
};

export class GalileoCallbackHandler {
  private galileoCallback: any;
  private galileoEnabled: boolean = false;
  private isInitialized: boolean = false;

  constructor() {}

  /**
   * Initializes the Galileo tracer. This must be called before any
   * agent interactions occur. It sets up the connection to Galileo
   * and prepares the LangChain callback.
   */
  public async init(): Promise<void> {
    if (this.isInitialized) {
      console.log('🔧 Galileo is already initialized.');
      return;
    }

    try {
      // Suppress noisy debug messages from the Galileo SDK during init
      const originalDebug = console.debug;
      console.debug = () => {};

      try {
        await init();
        this.galileoCallback = new GalileoCallback();
        this.galileoEnabled = true;
        this.isInitialized = true;
        console.log('✅ Galileo initialized successfully.');
      } finally {
        // Restore the original console.debug function
        console.debug = originalDebug;
      }
    } catch (error: any) {
      console.warn(`⚠️ Galileo initialization failed: ${error.message}`);
      console.warn('Stripe agent will run in local-only mode without tracing.');
      this.galileoEnabled = false;
      this.galileoCallback = null;
      this.isInitialized = false;
    }
  }

  /**
   * Returns the Galileo callback instance for LangChain integration.
   *
   * This callback should be passed to the `agentExecutor.invoke` call
   * to enable automatic tracing of LLM, tool, and agent runs.
   * If Galileo is disabled, it returns a mock callback to prevent errors.
   */
  public getCallback(): any {
    if (this.galileoEnabled && this.galileoCallback) {
      // Return the callback directly since we have global suppression in place
      return this.galileoCallback;
    }

    // Return a mock callback if Galileo is not enabled
    return this.createMockCallback();
  }
  
  /**
   * Flushes all buffered traces to Galileo.
   * This should be called at the end of a session or when the application
   * is shutting down to ensure all data is sent.
   */
  public async flush(): Promise<void> {
    if (this.galileoEnabled) {
      try {
        await flush();
        console.log('✅ All traces successfully flushed to Galileo.');
      } catch (error: any) {
        console.warn(`⚠️ Failed to flush Galileo traces: ${error.message}`);
      }
    }
  }


  /**
   * Creates a mock callback object with the same interface as the real
   * Galileo callback. This is used when Galileo is disabled to prevent
   * the application from crashing.
   */
  private createMockCallback(): any {
    const noOp = () => {};
    return {
      name: 'galileo_callback_mock',
      handleLLMStart: noOp,
      handleLLMEnd: noOp,
      handleLLMError: noOp,
      handleToolStart: noOp,
      handleToolEnd: noOp,
      handleToolError: noOp,
      handleAgentStart: noOp,
      handleAgentEnd: noOp,
      handleChainStart: noOp,
      handleChainEnd: noOp,
      handleChainError: noOp,
      handleText: noOp,
    };
  }
}
