// Re-export types
export * from './types';

// Export actual handlers
export { GalileoCallbackHandler } from './handlers/GalileoCallbackHandler';

// Example structure for future handlers:

// Session management handlers
// export { SessionCallbackHandler } from './handlers/SessionCallbackHandler';
// export { MetricsCallbackHandler } from './handlers/MetricsCallbackHandler';

// Logging handlers  
// export { ConsoleLoggingHandler } from './handlers/ConsoleLoggingHandler';
// export { FileLoggingHandler } from './handlers/FileLoggingHandler';
// export { GalileoLoggingHandler } from './handlers/GalileoLoggingHandler';

// Cost tracking handlers
// export { CostTrackingHandler } from './handlers/CostTrackingHandler';

// Performance monitoring handlers
// export { PerformanceHandler } from './handlers/PerformanceHandler';

// Error tracking handlers
// export { ErrorTrackingHandler } from './handlers/ErrorTrackingHandler';

/**
 * Utility function to create a session context
 */
import { SessionContext, AgentMessage } from './types';

export function createSessionContext(sessionId: string, userId?: string): SessionContext {
  return {
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
}

/**
 * Utility function to update session context with new message
 */
export function updateSessionWithMessage(
  context: SessionContext, 
  message: AgentMessage
): SessionContext {
  return {
    ...context,
    conversationHistory: [...context.conversationHistory, message],
    messageCount: context.messageCount + 1,
    lastActivity: new Date(),
  };
}

/**
 * Utility function to add tool usage to session
 */
export function addToolToSession(
  context: SessionContext, 
  toolName: string
): SessionContext {
  return {
    ...context,
    toolsUsed: new Set([...context.toolsUsed, toolName]),
    lastActivity: new Date(),
  };
}

/**
 * Utility function to update session metrics
 */
export function updateSessionMetrics(
  context: SessionContext,
  executionTime: number,
  success: boolean,
  cost?: number
): SessionContext {
  const newMetrics = {
    ...context.metrics,
    totalExecutionTime: context.metrics.totalExecutionTime + executionTime,
  };

  if (success) {
    newMetrics.successfulOperations = context.metrics.successfulOperations + 1;
  } else {
    newMetrics.failedOperations = context.metrics.failedOperations + 1;
  }

  const totalOperations = newMetrics.successfulOperations + newMetrics.failedOperations;
  if (totalOperations > 0) {
    newMetrics.averageResponseTime = newMetrics.totalExecutionTime / totalOperations;
  }

  return {
    ...context,
    metrics: newMetrics,
    totalCost: cost ? (context.totalCost || 0) + cost : context.totalCost,
    lastActivity: new Date(),
  };
}

/**
 * Utility function to end a session
 */
export function endSession(context: SessionContext): SessionContext {
  return {
    ...context,
    isActive: false,
    lastActivity: new Date(),
  };
}
