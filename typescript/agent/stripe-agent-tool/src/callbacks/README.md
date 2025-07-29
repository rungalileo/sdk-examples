# Callbacks

This directory contains LangChain callback handlers and session management utilities for the Stripe Agent.

## Structure

```
src/callbacks/
├── index.ts           # Main entry point - re-exports all handlers and utilities
├── types.ts           # Shared types and interfaces for session context
├── handlers/          # Directory for custom callback handlers
└── README.md         # This file
```

## Core Types

### SessionContext
The `SessionContext` interface holds session-level metadata that can be shared across LangChain callbacks via the `RunManager`'s `runId` metadata. This includes:

- `sessionId`: Unique identifier for the conversation session
- `startTime`: When the session was started
- `conversationHistory`: Complete conversation history
- `userId`: Optional user identifier
- `metadata`: Custom session metadata
- `isActive`: Whether the session is currently active
- `messageCount`: Total number of messages
- `totalCost`: Accumulated cost for the session
- `toolsUsed`: Set of tools used during the session
- `metrics`: Performance metrics (execution time, success/failure rates, etc.)

### RunContext
The `RunContext` interface provides context data that can be attached to individual LangChain run metadata:

- `sessionId`: Reference to the parent session
- `operationType`: Type of operation (agent_call, tool_call, llm_call, chain_call)
- `toolName`: Specific tool or model being used
- `input`: Input data for the run
- `startTime`: When the run started
- `parentRunId`: Parent run ID for nested operations
- `metadata`: Custom run metadata

## Utility Functions

The main index exports several utility functions for managing session context:

- `createSessionContext(sessionId, userId?)`: Creates a new session context
- `updateSessionWithMessage(context, message)`: Updates session with new message
- `addToolToSession(context, toolName)`: Adds tool usage to session
- `updateSessionMetrics(context, executionTime, success, cost?)`: Updates performance metrics
- `endSession(context)`: Marks a session as ended

## Future Handlers

The `handlers/` directory is prepared for custom callback implementations such as:

- `SessionCallbackHandler`: Manages session lifecycle
- `MetricsCallbackHandler`: Tracks performance metrics
- `ConsoleLoggingHandler`: Console-based logging
- `FileLoggingHandler`: File-based logging
- `GalileoLoggingHandler`: Integration with Galileo logging
- `CostTrackingHandler`: Tracks API costs
- `PerformanceHandler`: Performance monitoring
- `ErrorTrackingHandler`: Error tracking and reporting

## Usage

Import the callback types and utilities:

```typescript
import { 
  SessionContext, 
  RunContext, 
  createSessionContext,
  updateSessionWithMessage,
  // ... other utilities
} from './callbacks';

// Create a new session
const sessionContext = createSessionContext('session-123', 'user-456');

// Update with messages
const updatedContext = updateSessionWithMessage(sessionContext, {
  role: 'user',
  content: 'Hello!',
  timestamp: new Date()
});
```

## Integration with LangChain

The callback handlers can be integrated with LangChain by:

1. Implementing the appropriate LangChain callback interfaces
2. Storing session context in the run metadata
3. Using the RunManager's runId to share context across handlers
4. Tracking session state and metrics throughout the agent execution

This structure allows for comprehensive monitoring, logging, and session management across the entire agent lifecycle.
