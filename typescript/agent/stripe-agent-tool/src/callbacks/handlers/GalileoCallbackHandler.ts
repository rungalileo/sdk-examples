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
      const realCallback = this.galileoCallback;
      const logWrapper = (methodName: string, originalMethod: Function) => {
        // Ensure the original method exists before wrapping
        if (typeof originalMethod !== 'function') {
          return () => {}; // Return a no-op if the method doesn't exist
        }
        return (...args: any[]) => {
          // Attempt to find the run_id from common argument structures
          const runId = args[1]?.id || args[0]?.id || 'unknown';
          console.log(`[Tracer DEBUG] ==> ${methodName}`, { runId });
          try {
            const result = originalMethod.apply(realCallback, args);
            if (result && typeof result.then === 'function') {
              return result.finally(() => {
                console.log(`[Tracer DEBUG] <== ${methodName}`, { runId });
              });
            }
            return result;
          } finally {
             // This will run for sync methods, for async it runs before promise resolves.
             // The .finally() on the promise is better for async.
          }
        };
      };

      // Wrap all potential callback methods with our logger
      return {
        name: 'galileo_logging_wrapper',
        handleLLMStart: logWrapper('handleLLMStart', realCallback.handleLLMStart),
        handleLLMEnd: logWrapper('handleLLMEnd', realCallback.handleLLMEnd),
        handleLLMError: logWrapper('handleLLMError', realCallback.handleLLMError),
        handleToolStart: logWrapper('handleToolStart', realCallback.handleToolStart),
        handleToolEnd: logWrapper('handleToolEnd', realCallback.handleToolEnd),
        handleToolError: logWrapper('handleToolError', realCallback.handleToolError),
        handleAgentStart: logWrapper('handleAgentStart', realCallback.handleAgentStart),
        handleAgentEnd: logWrapper('handleAgentEnd', realCallback.handleAgentEnd),
        handleChainStart: logWrapper('handleChainStart', realCallback.handleChainStart),
        handleChainEnd: logWrapper('handleChainEnd', realCallback.handleChainEnd),
        handleChainError: logWrapper('handleChainError', realCallback.handleChainError),
        handleText: logWrapper('handleText', realCallback.handleText),
      };
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
