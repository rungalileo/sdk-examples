import { AgentMetrics, AgentMessage } from '../types';
/**
 * Galileo logging utility following the proper pattern from documentation
 */
export declare class GalileoAgentLogger {
    private logger;
    private sessionId?;
    private currentTraceActive;
    constructor();
    /**
     * Start a session for grouping multiple traces
     */
    startSession(sessionName?: string): Promise<string>;
    /**
     * Log a single agent execution following the proper Galileo pattern
     */
    logAgentExecution(metrics: AgentMetrics, userInput: string, agentOutput: string, traceName?: string, metadata?: Record<string, unknown>, intermediateSteps?: Array<{
        action?: {
            tool?: string;
            toolInput?: unknown;
            tool_input?: unknown;
        };
        observation?: unknown;
    }>): Promise<void>;
    /**
     * Generate a meaningful trace name from user input
     */
    private generateTraceName;
    /**
     * Log conversation summary
     */
    logConversation(messages: AgentMessage[]): Promise<void>;
    /**
     * Extract message content safely
     */
    private extractMessageContent;
    /**
     * Log user satisfaction feedback
     */
    logSatisfaction(satisfaction: boolean): Promise<void>;
    /**
     * Flush all traces to ensure they're sent to Galileo
     */
    flushAllTraces(): Promise<void>;
    /**
     * Conclude the current session
     */
    concludeSession(): Promise<void>;
}
//# sourceMappingURL=GalileoLogger.d.ts.map