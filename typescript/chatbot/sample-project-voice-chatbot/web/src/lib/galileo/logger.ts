import { GalileoLogger } from "galileo";
import { type GuardrailResult } from "./protect";

// Server-side only - this module should only be imported in API routes

// Configuration - use Python service if available for proper Protect Status
const PYTHON_SERVICE_URL = process.env.GALILEO_PYTHON_SERVICE_URL;
const USE_PYTHON_SERVICE = !!PYTHON_SERVICE_URL;

export interface ConversationTurnResult {
  logged: boolean;
  inputGuardrail?: GuardrailResult;
  outputGuardrail?: GuardrailResult;
  blocked: boolean;
  overrideMessage?: string;
}

export async function startGalileoSession(
  sessionId: string,
  name?: string
): Promise<string> {
  // When using Python service, session is auto-created on first log-conversation-turn call
  // No need to explicitly start a session here
  if (USE_PYTHON_SERVICE) {
    console.log(`[Galileo] Session ${sessionId} will be created by Python service on first log`);
    return sessionId;
  }

  // Fallback: TypeScript SDK (requires GALILEO_API_KEY)
  const logger = new GalileoLogger({
    projectName: process.env.GALILEO_PROJECT_NAME || "voice-chatbot",
    logStreamName: process.env.GALILEO_LOG_STREAM || "default",
  });

  const sessionName = name || `ElevenLabs-${sessionId.slice(0, 8)}`;

  await logger.startSession({
    name: sessionName,
    externalId: sessionId,
  });

  await logger.flush();

  console.log(`Galileo session started: ${sessionId}`);
  return sessionId;
}

export async function logConversationTurn(
  sessionId: string,
  userTranscript: string,
  agentResponse: string,
  turnNumber: number,
  latencyMs: number,
  conversationContext: Array<{ role: string; content: string }>,
  options: { checkGuardrails?: boolean } = {}
): Promise<ConversationTurnResult> {
  const { checkGuardrails = false } = options;
  const protectEnabled = process.env.GALILEO_PROTECT_ENABLED === "true";
  const stageId = process.env.GALILEO_PROTECT_STAGE_ID;
  const projectName = process.env.GALILEO_PROJECT_NAME || "voice-chatbot";

  // Use Python service for ALL logging when available
  // This ensures protect spans are in the same trace as conversation (required for Protect Status)
  if (USE_PYTHON_SERVICE) {
    console.log("[Galileo] Using Python service for unified logging with Protect Status");
    console.log("[Galileo] DEBUG: stageId=", stageId);
    console.log("[Galileo] DEBUG: protectEnabled=", protectEnabled);
    console.log("[Galileo] DEBUG: checkGuardrails=", checkGuardrails);
    console.log("[Galileo] DEBUG: check_guardrails value=", checkGuardrails && protectEnabled);
    console.log("[Galileo] DEBUG: userTranscript=", userTranscript.substring(0, 50));

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
          check_guardrails: checkGuardrails && protectEnabled,
          stage_id: stageId,
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
        console.log(`Turn ${turnNumber} blocked by guardrail`);
      }

      console.log(`Galileo turn ${turnNumber} logged via Python (blocked=${result.blocked})`);

      return {
        logged: true,
        inputGuardrail,
        outputGuardrail,
        blocked: result.blocked,
        overrideMessage: result.override_message,
      };
    } catch (error) {
      console.error("Python service logging failed, falling back to TypeScript:", error);
      // Fall through to TypeScript logging
    }
  }

  // Fallback: TypeScript logging (Protect Status will show N/A)
  console.log("[Galileo] Using TypeScript logging (Protect Status will show N/A)");

  const logger = new GalileoLogger({
    projectName: projectName,
    logStreamName: process.env.GALILEO_LOG_STREAM || "default",
  });

  await logger.startSession({
    externalId: sessionId,
  });

  logger.startTrace({
    input: userTranscript,
    name: `Turn-${turnNumber}`,
    metadata: {
      session_id: sessionId,
      turn_number: String(turnNumber),
      source: "elevenlabs-voice",
    },
  });

  logger.addLlmSpan({
    input: JSON.stringify(conversationContext),
    output: agentResponse,
    model: "elevenlabs-agent",
    name: "Agent_Response",
    metadata: {
      latency_ms: String(latencyMs),
    },
  });

  logger.conclude({ output: agentResponse });
  await logger.flush();

  console.log(`Galileo turn ${turnNumber} logged via TypeScript`);

  return {
    logged: true,
    blocked: false,
  };
}

export async function endGalileoSession(sessionId: string): Promise<void> {
  // When using Python service, call its end-session endpoint
  if (USE_PYTHON_SERVICE) {
    try {
      await fetch(`${PYTHON_SERVICE_URL}/end-session/${sessionId}`, {
        method: "POST",
      });
      console.log(`[Galileo] Session ${sessionId} ended via Python service`);
    } catch (error) {
      console.error("Failed to end session via Python service:", error);
    }
    return;
  }

  // Fallback: TypeScript SDK (requires GALILEO_API_KEY)
  const logger = new GalileoLogger({
    projectName: process.env.GALILEO_PROJECT_NAME || "voice-chatbot",
    logStreamName: process.env.GALILEO_LOG_STREAM || "default",
  });

  await logger.startSession({
    externalId: sessionId,
  });

  await logger.flush();
  logger.clearSession();
  console.log(`Galileo session ended: ${sessionId}`);
}
