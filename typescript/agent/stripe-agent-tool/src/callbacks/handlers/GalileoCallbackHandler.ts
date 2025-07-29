const { init, flush, GalileoCallback } = require('galileo');

/**
 * A simplified Galileo Callback Handler for the Stripe Agent.
 *
 * This handler wraps the official Galileo LangChain callback and provides
 * a clean interface for initialization, retrieval, and flushing of traces.
 * It removes all manual session and trace management in favor of relying
 * on the automated tracing provided by LangChain and Galileo.
 */
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
      // Wrap the callback to suppress the noisy "No node exists for run_id" messages
      return this.createQuietGalileoCallback(this.galileoCallback);
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
   * Wraps the Galileo callback in a proxy to suppress specific, noisy
   * console messages that are not critical for debugging.
   */
  private createQuietGalileoCallback(originalCallback: any): any {
    const suppressDebugDuring = (fn: Function) => {
      return (...args: any[]) => {
        const originalDebug = console.debug;
        
        // Suppress "No node exists for run_id" which can be noisy
        console.debug = (message?: any, ...optionalParams: any[]) => {
          if (typeof message === 'string' && message.includes('No node exists for run_id')) {
            return;
          }
          originalDebug(message, ...optionalParams);
        };

        try {
          return fn.apply(originalCallback, args);
        } finally {
          console.debug = originalDebug;
        }
      };
    };

    // Return a proxy that wraps all handler methods
    return new Proxy(originalCallback, {
      get(target, prop) {
        const value = target[prop];
        if (typeof value === 'function') {
          return suppressDebugDuring(value);
        }
        return value;
      },
    });
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
