// Thin wrapper that forwards logging calls to the Python service.
// python service handles all Galileo SDK calls (logging, traces, protect spans).
const PYTHON_SERVICE_URL = process.env.GALILEO_PYTHON_SERVICE_URL;

export interface GuardrailResult {
  blocked: boolean;
  status: "triggered" | "not_triggered";
  overrideMessage?: string;
  triggeredRules: Array<{
    metric: string;
    value: number;
    threshold: number;
    operator: string;
  }>;
}

export interface ConversationTurnResult {
  logged: boolean;
  inputGuardrail?: GuardrailResult;
  outputGuardrail?: GuardrailResult;
  blocked: boolean;
  overrideMessage?: string;
}

/**
 * Start a Galileo session for tracking conversation turns.
 * Session is auto-created by the Python service on first log call.
 * @param sessionId - Unique identifier for the session
 * @returns Promise resolving to the session ID
 */
export async function startGalileoSession(sessionId: string): Promise<string> {
  // Session is auto-created on first log-conversation-turn call
  console.log(`[Galileo] Session ${sessionId} will be created by Python service on first log`);
  return sessionId;
}

/**
 * Log a conversation turn to Galileo with optional guardrail checks.
 * Guardrails are configured via env vars in the Python service.
 * @param sessionId - The session ID for this conversation
 * @param userTranscript - The user's transcribed speech input
 * @param agentResponse - The agent's response text
 * @param turnNumber - Sequential turn number in the conversation
 * @param latencyMs - Response latency in milliseconds
 * @param conversationContext - Array of conversation messages for context
 * @returns Promise with logging status and guardrail results
 */
export async function logConversationTurn(
  sessionId: string,
  userTranscript: string,
  agentResponse: string,
  turnNumber: number,
  latencyMs: number,
  conversationContext: Array<{ role: string; content: string }>
): Promise<ConversationTurnResult> {
  if (!PYTHON_SERVICE_URL) {
    console.error("[Galileo] GALILEO_PYTHON_SERVICE_URL not configured");
    return { logged: false, blocked: false };
  }

  const projectName = process.env.GALILEO_PROJECT_NAME || "voice-chatbot";

  console.log("[Galileo] Logging turn via Python service");

  try {
    const response = await fetch(`${PYTHON_SERVICE_URL}/log-conversation-turn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        user_transcript: userTranscript,
        agent_response: agentResponse,
        turn_number: turnNumber,
        latency_ms: latencyMs,
        conversation_context: conversationContext,
        project_name: projectName,
      }),
    });

    if (!response.ok) {
      throw new Error(`Python service error: ${response.status}`);
    }

    const result = await response.json();

    const inputGuardrail: GuardrailResult | undefined = result.input_guardrail ? {
      blocked: result.input_guardrail.blocked,
      status: result.input_guardrail.status,
      triggeredRules: result.input_guardrail.triggered_rules || [],
      overrideMessage: result.input_guardrail.override_message,
    } : undefined;

    const outputGuardrail: GuardrailResult | undefined = result.output_guardrail ? {
      blocked: result.output_guardrail.blocked,
      status: result.output_guardrail.status,
      triggeredRules: result.output_guardrail.triggered_rules || [],
      overrideMessage: result.output_guardrail.override_message,
    } : undefined;

    if (result.blocked) {
      console.log(`[Galileo] Turn ${turnNumber} blocked by guardrail`);
    }

    console.log(`[Galileo] Turn ${turnNumber} logged (blocked=${result.blocked})`);

    return {
      logged: true,
      inputGuardrail,
      outputGuardrail,
      blocked: result.blocked,
      overrideMessage: result.override_message,
    };
  } catch (error) {
    console.error("[Galileo] Failed to log turn:", error);
    return { logged: false, blocked: false };
  }
}

/**
 * End a Galileo session.
 * @param sessionId - The session ID to end
 */
export async function endGalileoSession(sessionId: string): Promise<void> {
  if (!PYTHON_SERVICE_URL) {
    console.error("[Galileo] GALILEO_PYTHON_SERVICE_URL not configured");
    return;
  }

  try {
    await fetch(`${PYTHON_SERVICE_URL}/end-session/${sessionId}`, {
      method: "POST",
    });
    console.log(`[Galileo] Session ${sessionId} ended`);
  } catch (error) {
    console.error("[Galileo] Failed to end session:", error);
  }
}
