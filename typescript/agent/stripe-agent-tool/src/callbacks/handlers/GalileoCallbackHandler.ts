import { SessionContext, RunContext } from '../types';

// Import Galileo functions using require to work around TypeScript module resolution
const { getLogger, GalileoCallback } = require('galileo');

/**
 * Galileo Callback Handler for Stripe Agent
 * 
 * This handler provides session management and metrics tracking for the Stripe agent.
 * It uses the official Galileo LangChain callback for proper integration.
 */
export class GalileoCallbackHandler {
  private sessionContext: SessionContext | null = null;
  private currentRunContext: RunContext | null = null;
  private sessionStartTime: Date | null = null;
  private galileoLogger: any;
  private galileoCallback: any;
  private galileoEnabled: boolean = true;

  constructor() {
    // Initialize Galileo logger and callback with error handling
    try {
      this.galileoLogger = getLogger();
      this.galileoCallback = new GalileoCallback(this.galileoLogger, true, false);
      console.log('🔧 Galileo Callback Handler initialized with proper LangChain integration');
    } catch (error: any) {
      console.warn('⚠️  Galileo initialization failed, running in local-only mode:', error.message);
      this.galileoEnabled = false;
      this.galileoLogger = null;
      this.galileoCallback = null;
    }
  }

  /**
   * Start a new session for tracking agent interactions
   */
  async startSession(sessionId: string, userId?: string): Promise<void> {
    this.sessionContext = {
      sessionId,
      startTime: new Date(),
      conversationHistory: [],
      userId,
      metadata: {},
      isActive: true,
      lastActivity: new Date(),
      messageCount: 0,
      totalCost: 0,
      toolsUsed: new Set<string>(),
      metrics: {
        totalExecutionTime: 0,
        successfulOperations: 0,
        failedOperations: 0,
        averageResponseTime: 0,
      },
    };

    this.sessionStartTime = new Date();
    
    // Start a Galileo session if enabled
    if (this.galileoEnabled && this.galileoLogger) {
      try {
        const sessionName = `Stripe Agent Session - ${sessionId}`;
        await this.galileoLogger.startSession({ name: sessionName });
        console.log(`🚀 Galileo session started: ${sessionName}`);
      } catch (error: any) {
        console.warn('⚠️  Failed to start Galileo session:', error.message);
      }
    }
    
    console.log(`🚀 Session started: ${sessionId}`);
  }

  /**
   * End the current session and flush all traces
   */
  async endSession(): Promise<void> {
    if (!this.sessionContext) {
      return;
    }

    this.sessionContext.isActive = false;
    this.sessionContext.lastActivity = new Date();
    
    // Flush any remaining traces if Galileo is enabled
    if (this.galileoEnabled && this.galileoLogger) {
      try {
        await this.galileoLogger.flush();
      } catch (error: any) {
        console.warn('⚠️  Failed to flush Galileo traces:', error.message);
      }
    }
    
    console.log(`📊 Session ended: ${this.sessionContext.sessionId}`);
  }

  /**
   * Update session with a new message
   */
  updateSessionWithMessage(message: any): void {
    if (!this.sessionContext) {
      return;
    }

    this.sessionContext.conversationHistory.push({
      role: message.role || 'user',
      content: message.content || '',
      timestamp: new Date(),
    });

    this.sessionContext.messageCount++;
    this.sessionContext.lastActivity = new Date();
  }

  /**
   * Add tool usage to session tracking
   */
  addToolToSession(toolName: string): void {
    if (!this.sessionContext) {
      return;
    }

    this.sessionContext.toolsUsed.add(toolName);
  }

  /**
   * Update session metrics with execution results
   */
  updateSessionMetrics(executionTime: number, success: boolean, cost?: number): void {
    if (!this.sessionContext) {
      return;
    }

    this.sessionContext.metrics.totalExecutionTime += executionTime;
    
    if (success) {
      this.sessionContext.metrics.successfulOperations++;
    } else {
      this.sessionContext.metrics.failedOperations++;
    }

    if (cost) {
      this.sessionContext.totalCost = (this.sessionContext.totalCost || 0) + cost;
    }

    // Calculate average response time
    const totalOperations = this.sessionContext.metrics.successfulOperations + this.sessionContext.metrics.failedOperations;
    if (totalOperations > 0) {
      this.sessionContext.metrics.averageResponseTime = this.sessionContext.metrics.totalExecutionTime / totalOperations;
    }
  }

  /**
   * Log agent start event - Creates a new trace for this conversation step
   */
  logAgentStart(runId: string, input: any): void {
    this.currentRunContext = {
      sessionId: this.sessionContext?.sessionId || 'unknown',
      operationType: 'agent_call',
      input,
      startTime: new Date(),
      metadata: {
        runId,
        operation: 'agent_start'
      }
    };

    // Start a new trace for this conversation step in Galileo
    if (this.galileoEnabled && this.galileoLogger) {
      try {
        const traceName = this.generateTraceName(input?.input || 'Agent Processing');
        const cleanInput = this.formatInputForGalileo(input?.input || input);
        
        this.galileoLogger.startTrace({ 
          name: traceName, 
          input: cleanInput,
          metadata: {
            runId,
            sessionId: this.sessionContext?.sessionId,
            operationType: 'agent_workflow',
            timestamp: new Date().toISOString()
          }
        });
        console.log(`🔍 Galileo trace started: ${traceName}`);
      } catch (error: any) {
        console.warn('⚠️  Failed to start Galileo trace:', error.message);
      }
    }

    console.log(`🤖 Agent started processing: ${runId}`);
  }

  /**
   * Log agent end event - Concludes the current trace
   */
  logAgentEnd(runId: string, output: any): void {
    if (this.currentRunContext) {
      const executionTime = Date.now() - this.currentRunContext.startTime.getTime();
      this.updateSessionMetrics(executionTime, true);
      
      // Conclude the current trace in Galileo
      if (this.galileoEnabled && this.galileoLogger) {
        try {
          const cleanOutput = this.formatOutputForGalileo(output?.output || output);
          this.galileoLogger.conclude({ 
            output: cleanOutput,
            durationNs: executionTime * 1000000, // Convert ms to nanoseconds
            metadata: {
              runId,
              sessionId: this.sessionContext?.sessionId,
              success: true,
              executionTimeMs: executionTime
            }
          });
          console.log(`🔍 Galileo trace concluded: ${runId}`);
        } catch (error: any) {
          console.warn('⚠️  Failed to conclude Galileo trace:', error.message);
        }
      }
      
      console.log(`✅ Agent completed: ${runId} (${executionTime}ms)`);
    }
  }

  /**
   * Log tool start event
   */
  logToolStart(runId: string, toolName: string, input: any): void {
    this.addToolToSession(toolName);
    
    this.currentRunContext = {
      sessionId: this.sessionContext?.sessionId || 'unknown',
      operationType: 'tool_call',
      toolName,
      input,
      startTime: new Date(),
      metadata: {
        runId,
        operation: 'tool_start'
      }
    };

    console.log(`🔧 Tool started: ${toolName}`);
  }

  /**
   * Log tool end event
   */
  logToolEnd(runId: string, output: any): void {
    if (this.currentRunContext) {
      const executionTime = Date.now() - this.currentRunContext.startTime.getTime();
      this.updateSessionMetrics(executionTime, true);
      
      console.log(`✅ Tool completed: ${this.currentRunContext.toolName} (${executionTime}ms)`);
    }
  }

  /**
   * Log LLM start event
   */
  logLLMStart(runId: string, input: any): void {
    this.currentRunContext = {
      sessionId: this.sessionContext?.sessionId || 'unknown',
      operationType: 'llm_call',
      input,
      startTime: new Date(),
      metadata: {
        runId,
        operation: 'llm_start'
      }
    };

    console.log(`🧠 LLM call started: ${runId}`);
  }

  /**
   * Log LLM end event
   */
  logLLMEnd(runId: string, output: any): void {
    if (this.currentRunContext) {
      const executionTime = Date.now() - this.currentRunContext.startTime.getTime();
      this.updateSessionMetrics(executionTime, true);
      
      console.log(`✅ LLM call completed: ${runId} (${executionTime}ms)`);
    }
  }

  /**
   * Log error event
   */
  logError(runId: string, error: Error): void {
    if (this.currentRunContext) {
      const executionTime = Date.now() - this.currentRunContext.startTime.getTime();
      this.updateSessionMetrics(executionTime, false);
      
      console.log(`❌ Error in ${this.currentRunContext.operationType}: ${error.message}`);
    }
  }

  /**
   * Get the Galileo callback for LangChain integration
   * This now returns the actual Galileo callback for proper integration
   * Falls back to a mock callback if Galileo is disabled
   */
  getGalileoCallback(): any {
    if (this.galileoEnabled && this.galileoCallback) {
      return this.galileoCallback;
    } else {
      // Return a mock callback when Galileo is disabled
      return {
        name: 'galileo_callback_mock',
        handleLLMStart: () => {},
        handleLLMEnd: () => {},
        handleToolStart: () => {},
        handleToolEnd: () => {},
        handleAgentStart: () => {},
        handleAgentEnd: () => {},
        handleError: () => {},
      };
    }
  }

  /**
   * Get current session context
   */
  getSessionContext(): SessionContext | null {
    return this.sessionContext;
  }

  /**
   * Flush all buffered traces
   */
  async flush(): Promise<void> {
    console.log('📊 Flushing traces...');
    if (this.galileoEnabled && this.galileoLogger) {
      try {
        await this.galileoLogger.flush();
      } catch (error: any) {
        console.warn('⚠️  Failed to flush Galileo traces:', error.message);
      }
    }
  }

  /**
   * Check if Galileo is enabled
   */
  isGalileoEnabled(): boolean {
    return this.galileoEnabled;
  }

  /**
   * Format input for Galileo to be more readable and concise
   */
  private formatInputForGalileo(input: any): string {
    if (typeof input === 'string') {
      // Truncate very long inputs and clean up
      return input.length > 200 ? input.substring(0, 200) + '...' : input;
    }
    
    if (typeof input === 'object' && input !== null) {
      try {
        // Format objects more cleanly, removing verbose metadata
        const cleanObject: any = {};
        
        if (input.input) {
          cleanObject.input = typeof input.input === 'string' && input.input.length > 200 
            ? input.input.substring(0, 200) + '...'
            : input.input;
        }
        
        if (input.chat_history && Array.isArray(input.chat_history)) {
          cleanObject.context_messages = input.chat_history.length;
        }
        
        // Include other relevant fields but keep them concise
        Object.keys(input).forEach(key => {
          if (!['input', 'chat_history'].includes(key) && input[key] !== undefined) {
            if (typeof input[key] === 'string' && input[key].length > 100) {
              cleanObject[key] = input[key].substring(0, 100) + '...';
            } else if (typeof input[key] !== 'object') {
              cleanObject[key] = input[key];
            }
          }
        });
        
        return JSON.stringify(cleanObject, null, 2);
      } catch (error) {
        return String(input);
      }
    }
    
    return String(input);
  }

  /**
   * Format output for Galileo to be more readable and concise
   */
  private formatOutputForGalileo(output: any): string {
    if (typeof output === 'string') {
      // Clean up very long outputs and remove excessive JSON nesting
      if (output.length > 500) {
        // Try to extract the key information
        const paymentLinkMatch = output.match(/https:\/\/buy\.stripe\.com\/[^\s"]+/);
        if (paymentLinkMatch) {
          return `Payment link created: ${paymentLinkMatch[0]}`;
        }
        return output.substring(0, 500) + '...';
      }
      return output;
    }
    
    if (typeof output === 'object' && output !== null) {
      try {
        // If it's a complex object, extract the essential information
        const summary: any = {};
        
        // Check for common output patterns
        if (output.text || output.content) {
          const text = output.text || output.content;
          summary.response = typeof text === 'string' && text.length > 300 
            ? text.substring(0, 300) + '...'
            : text;
        }
        
        if (output.url) {
          summary.payment_link = output.url;
        }
        
        if (output.success !== undefined) {
          summary.success = output.success;
        }
        
        if (output.data && typeof output.data === 'object') {
          if (output.data.executionTime) {
            summary.execution_time_ms = output.data.executionTime;
          }
          if (output.data.toolsUsed) {
            summary.tools_used = Array.isArray(output.data.toolsUsed) 
              ? output.data.toolsUsed 
              : Object.keys(output.data.toolsUsed);
          }
        }
        
        // If we have no meaningful summary, just show a truncated version
        if (Object.keys(summary).length === 0) {
          const outputStr = JSON.stringify(output);
          return outputStr.length > 300 ? outputStr.substring(0, 300) + '...' : outputStr;
        }
        
        return JSON.stringify(summary, null, 2);
      } catch (error) {
        return String(output);
      }
    }
    
    return String(output);
  }

  /**
   * Generate descriptive trace names based on user input
   */
  private generateTraceName(input: string): string {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('payment link')) {
      return "🚀 Galileo's Gizmos - Launch Payment Portal";
    } else if (lowerInput.includes('customer') && lowerInput.includes('create')) {
      return "👨‍🚀 Galileo's Gizmos - Register Space Explorer";
    } else if (lowerInput.includes('products') && (lowerInput.includes('list') || lowerInput.includes('show') || lowerInput.includes('what') || lowerInput.includes('have'))) {
      return "🌌 Galileo's Gizmos - Browse Cosmic Catalog";
    } else if (lowerInput.includes('buy') || lowerInput.includes('purchase') || lowerInput.includes('order')) {
      return "💳 Galileo's Gizmos - Process Space Purchase";
    } else if (lowerInput.includes('price') || lowerInput.includes('cost') || lowerInput.includes('much')) {
      return "💰 Galileo's Gizmos - Check Cosmic Pricing";
    } else if (lowerInput.includes('subscription') && lowerInput.includes('create')) {
      return "📦 Galileo's Gizmos - Setup Stellar Subscription";
    } else if (lowerInput.includes('create') && lowerInput.includes('product')) {
      return "⭐ Galileo's Gizmos - Add New Space Gadget";
    } else if (lowerInput.includes('create') && lowerInput.includes('price')) {
      return "💫 Galileo's Gizmos - Set Cosmic Pricing";
    } else {
      return "🛸 Galileo's Gizmos - Customer Support";
    }
  }
} 
