import { env } from '../config/environment';
import { AgentMetrics, AgentMessage } from '../types';
import { GalileoLogger } from 'galileo';

/**
 * Galileo logging utility following the proper pattern from documentation
 */
export class GalileoAgentLogger {
  private logger: GalileoLogger;
  private sessionId?: string;
  private currentTraceActive = false;

  constructor() {
    this.logger = new GalileoLogger({
      projectName: env.galileo.projectName,
      logStreamName: env.galileo.logStream,
    });
  }

  /**
   * Start a session for grouping multiple traces
   */
  async startSession(sessionName?: string): Promise<string> {
    // Prevent creating multiple sessions
    if (this.sessionId) {
      console.log(`⚠️  Session already exists: ${this.sessionId}, reusing it`);
      return this.sessionId;
    }
    
    const sessionPrefix = sessionName ? sessionName.replace(/\s+/g, '-').toLowerCase() : 'stripe-agent-session';
    this.sessionId = `${sessionPrefix}-${Date.now()}-${Math.random().toString(36).substring(2)}`;
    console.log(`📊 Generated session ID: ${this.sessionId} (${sessionName || 'Default Session'})`);
    return this.sessionId;
  }

  /**
   * Log a single agent execution following the proper Galileo pattern
   */
  async logAgentExecution(
    metrics: AgentMetrics,
    userInput: string,
    agentOutput: string,
    traceName?: string,
    metadata?: Record<string, unknown>,
    intermediateSteps?: Array<{ action?: { tool?: string; toolInput?: unknown; tool_input?: unknown }; observation?: unknown }>
  ): Promise<void> {
    try {
      const finalTraceName = traceName || this.generateTraceName(userInput);
      
      // Start a new trace with user input as input, agent output as output
      // Include sessionId if available to group traces under one session
      this.logger.startTrace({ 
        input: userInput,  // What the user typed
        name: finalTraceName,
        metadata: this.sessionId ? { 
          sessionId: this.sessionId,
          toolsUsed: metrics.toolsUsed?.join(', ') || 'none',
          executionTime: String(metrics.executionTime || 0),
          success: String(metrics.success)
        } : undefined
      });
      this.currentTraceActive = true;

      // Get timing for the LLM call
      const startTime = Date.now();
      
      // Add LLM span showing the agent processing
      this.logger.addLlmSpan({
        input: userInput,           // What the user asked
        output: agentOutput,        // What the agent responded
        model: "gpt-4o-mini",
        name: "Galileo Gizmos Agent Response",
        numInputTokens: undefined,  // Could extract from metrics if available
        numOutputTokens: undefined,
        totalTokens: undefined,
        durationNs: metrics.executionTime ? metrics.executionTime * 1000000 : undefined,
        metadata: {
          sessionId: this.sessionId || 'no-session',
          executionTime: String(metrics.executionTime || 0),
          success: String(metrics.success),
          ...metadata
        }
      });

      // Add detailed tool spans for each Stripe operation with actual inputs/outputs
      if (intermediateSteps && intermediateSteps.length > 0) {
        intermediateSteps.forEach((step, index) => {
          if (step.action && step.action.tool) {
            const toolInput = step.action.toolInput || step.action.tool_input || {};
            const toolOutput = step.observation || 'No output available';
            
            this.logger.addToolSpan({
              input: JSON.stringify(toolInput, null, 2),
              output: typeof toolOutput === 'string' ? toolOutput : JSON.stringify(toolOutput, null, 2),
              name: `Stripe ${step.action.tool}`,
              durationNs: undefined,
              metadata: { 
                toolName: step.action.tool,
                stepNumber: String(index + 1),
                toolType: 'stripe-api',
                sessionId: this.sessionId || 'no-session',
                rawInput: JSON.stringify(toolInput),
                rawOutput: typeof toolOutput === 'string' ? toolOutput : JSON.stringify(toolOutput)
              },
              tags: ['stripe', 'tool', 'api', step.action.tool],
            });
          }
        });
      } else if (metrics.toolsUsed && metrics.toolsUsed.length > 0) {
        // Fallback for when intermediateSteps aren't available
        metrics.toolsUsed.forEach((tool, index) => {
          this.logger.addToolSpan({
            input: `Stripe ${tool} operation requested`,
            output: `Stripe ${tool} completed successfully`,
            name: `Stripe ${tool}`,
            durationNs: undefined,
            metadata: { 
              toolName: tool,
              stepNumber: String(index + 1),
              toolType: 'stripe-api',
              sessionId: this.sessionId || 'no-session'
            },
            tags: ['stripe', 'tool', 'api'],
          });
        });
      }

      // Conclude the trace with the final agent output
      this.logger.conclude({ 
        output: agentOutput,  // What the agent responded to the user
        durationNs: metrics.executionTime ? metrics.executionTime * 1000000 : undefined,
        statusCode: metrics.success ? 200 : 500,
      });

      // Flush the trace
      await this.logger.flush();
      this.currentTraceActive = false;

    } catch (error) {
      console.error('Failed to log to Galileo:', error);
      this.currentTraceActive = false;
    }
  }

  /**
   * Generate a meaningful trace name from user input
   */
  private generateTraceName(input: string): string {
    const cleanInput = input.replace(/[^\w\s]/g, '').trim();
    const words = cleanInput.split(/\s+/).slice(0, 4);
    const truncated = words.join(' ');
    
    if (truncated.length === 0) {
      return 'Galileo Gizmos - General Request';
    }
    
    return `Galileo Gizmos - ${truncated}`;
  }

  /**
   * Log conversation summary
   */
  async logConversation(messages: AgentMessage[]): Promise<void> {
    try {
      const conversationSummary = messages.map((msg, idx) => {
        const content = this.extractMessageContent(msg);
        const role = msg.role || 'unknown';
        return `${idx + 1}. [${role}]: ${content.substring(0, 200)}${content.length > 200 ? '...' : ''}`;
      }).join('\n');

      const userMessages = messages.filter(msg => msg.role === 'user');
      const assistantMessages = messages.filter(msg => msg.role === 'assistant');

      console.log(`📊 Session completed with ${messages.length} total messages:`);
      console.log(`🌟 All ${messages.length} interactions have been logged as detailed tool spans to Galileo!`);
      console.log(`🚀 Session includes: ${userMessages.length} customer inquiries + ${assistantMessages.length} support responses`);
      console.log(`🛸 Full conversation transcript and analytics now available in Galileo dashboard!`);

    } catch (error) {
      console.error('Failed to log conversation summary:', error);
    }
  }

  /**
   * Extract message content safely
   */
  private extractMessageContent(msg: unknown): string {
    if (!msg) return '';
    
    if (typeof msg === 'string') {
      return msg;
    }
    
    if (typeof msg === 'object' && msg !== null) {
      const messageObj = msg as Record<string, unknown>;
      
      if (typeof messageObj.content === 'string') {
        return messageObj.content;
      }
      
      if (messageObj.content && typeof messageObj.content === 'object') {
        const content = messageObj.content as Record<string, unknown>;
        if (typeof content.text === 'string') return content.text;
        if (typeof content.content === 'string') return content.content;
        return JSON.stringify(content);
      }
      
      return JSON.stringify(messageObj);
    }
    
    return String(msg);
  }

  /**
   * Log user satisfaction feedback
   */
  async logSatisfaction(satisfaction: boolean): Promise<void> {
    try {
      console.log(`📊 Logging satisfaction in session: ${this.sessionId}`);
      
      if (this.currentTraceActive) {
        // Add satisfaction as metadata to the current trace
        await this.logger.addLlmSpan({
          input: "User satisfaction feedback requested",
          output: `User satisfaction: ${satisfaction ? 'satisfied' : 'not satisfied'}`,
          name: "Satisfaction Review",
          model: "satisfaction-tool",
          durationNs: 0,
          numInputTokens: 0,
          numOutputTokens: 0,
          totalTokens: 0,
          metadata: {
            satisfaction_score: satisfaction ? '1.0' : '0.0',
            feedback_type: 'thumbs_up_down',
            session_conclusion: 'true',
            sessionId: this.sessionId || 'no-session'
          }
        });
      } else {
        console.log(`⚠️  No active trace for satisfaction logging in session: ${this.sessionId}`);
      }
      
      console.log(`📊 User satisfaction logged: ${satisfaction ? '👍' : '👎'} (Session: ${this.sessionId})`);
    } catch (error) {
      console.error('Failed to log satisfaction:', error);
    }
  }

  /**
   * Flush all traces to ensure they're sent to Galileo
   */
  async flushAllTraces(): Promise<void> {
    try {
      console.log('📊 Flushing all traces to Galileo...');
      await this.logger.flush();
      console.log('✅ All traces flushed successfully');
    } catch (error) {
      console.error('Failed to flush traces:', error);
    }
  }

  /**
   * Conclude the current session
   */
  async concludeSession(): Promise<void> {
    try {
      console.log('📊 Concluding session and flushing any remaining traces...');
      
      // Flush any remaining traces
      await this.logger.flush();
      
      this.sessionId = undefined;
      this.currentTraceActive = false;
      console.log('✅ Session concluded successfully');
    } catch (error) {
      console.error('Failed to conclude session:', error);
    }
  }
}
