export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  charCount: number;
  latencyMs?: number;
}

export interface SessionMetrics {
  durationSec: number;
  totalTurns: number;
  userTurns: number;
  agentTurns: number;
  avgLatencyMs: number;
  minLatencyMs: number;
  maxLatencyMs: number;
  userCharCount: number;
  agentCharCount: number;
  totalCharCount: number;
}

export interface ConversationState {
  sessionId: string;
  startTime: Date;
  turns: ConversationTurn[];
  conversationContext: Array<{ role: string; content: string }>;
  latenciesMs: number[];
  userCharCount: number;
  agentCharCount: number;
  turnCount: number;
  lastUserTurnTime: number | null;
}

export interface LogUserTurnRequest {
  sessionId: string;
  transcript: string;
  turnNumber: number;
}

export interface LogAgentTurnRequest {
  sessionId: string;
  response: string;
  latencyMs: number;
  turnNumber: number;
  conversationContext: Array<{ role: string; content: string }>;
}

export interface StartSessionRequest {
  sessionId: string;
  name?: string;
}

export interface EndSessionRequest {
  sessionId: string;
  metrics?: SessionMetrics;
}
