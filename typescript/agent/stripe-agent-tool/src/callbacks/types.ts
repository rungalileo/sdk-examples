import { AgentMessage } from '../types';

// Re-export for convenience
export { AgentMessage } from '../types';

/**
 * Session-level metadata that can be shared across LangChain handlers
 * via the RunManager's runId metadata
 */
export interface SessionContext {
  /** Unique identifier for the conversation session */
  sessionId: string;
  
  /** When the session was started */
  startTime: Date;
  
  /** Complete conversation history for this session */
  conversationHistory: AgentMessage[];
  
  /** Current user identifier (if available) */
  userId?: string;
  
  /** Session metadata for custom tracking */
  metadata?: Record<string, any>;
  
  /** Whether the session is currently active */
  isActive: boolean;
  
  /** Last activity timestamp */
  lastActivity: Date;
  
  /** Total number of messages in this session */
  messageCount: number;
  
  /** Total cost accumulated for this session */
  totalCost?: number;
  
  /** Tools used during this session */
  toolsUsed: Set<string>;
  
  /** Session performance metrics */
  metrics: {
    /** Total execution time for all operations */
    totalExecutionTime: number;
    /** Number of successful operations */
    successfulOperations: number;
    /** Number of failed operations */
    failedOperations: number;
    /** Average response time */
    averageResponseTime?: number;
  };
}

/**
 * Context data that can be attached to LangChain run metadata
 */
export interface RunContext {
  /** Reference to the session this run belongs to */
  sessionId: string;
  
  /** Type of operation being performed */
  operationType: 'agent_call' | 'tool_call' | 'llm_call' | 'chain_call';
  
  /** Specific tool or model being used */
  toolName?: string;
  
  /** Input data for this run */
  input?: any;
  
  /** Start time of this specific run */
  startTime: Date;
  
  /** Parent run ID if this is a nested operation */
  parentRunId?: string;
  
  /** Custom metadata for this run */
  metadata?: Record<string, any>;
}

/**
 * Callback event types for different stages of execution
 */
export type CallbackEventType = 
  | 'session_start'
  | 'session_end' 
  | 'message_received'
  | 'message_processed'
  | 'tool_start'
  | 'tool_end'
  | 'llm_start'
  | 'llm_end'
  | 'agent_start'
  | 'agent_end'
  | 'error_occurred';

/**
 * Base interface for callback events
 */
export interface CallbackEvent {
  type: CallbackEventType;
  timestamp: Date;
  sessionId: string;
  runId?: string;
  data?: any;
  error?: Error;
}
