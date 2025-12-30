import { NextResponse } from "next/server";
import { logConversationTurn } from "@/lib/galileo/logger";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const {
      sessionId,
      userTranscript,
      agentResponse,
      turnNumber,
      latencyMs,
      conversationContext,
      checkGuardrails,
    } = body;

    if (!sessionId) {
      return NextResponse.json(
        { error: "sessionId is required" },
        { status: 400 }
      );
    }

    if (!userTranscript || !agentResponse) {
      return NextResponse.json(
        { error: "userTranscript and agentResponse are required" },
        { status: 400 }
      );
    }

    const result = await logConversationTurn(
      sessionId,
      userTranscript,
      agentResponse,
      turnNumber || 1,
      latencyMs || 0,
      conversationContext || [],
      { checkGuardrails: checkGuardrails ?? true }
    );

    return NextResponse.json({
      success: true,
      message: "Conversation turn logged",
      turnNumber: turnNumber || 1,
      guardrails: {
        checked: checkGuardrails ?? true,
        blocked: result.blocked,
        overrideMessage: result.overrideMessage,
        inputResult: result.inputGuardrail ? {
          status: result.inputGuardrail.status,
          triggeredRules: result.inputGuardrail.triggeredRules,
        } : null,
        outputResult: result.outputGuardrail ? {
          status: result.outputGuardrail.status,
          triggeredRules: result.outputGuardrail.triggeredRules,
        } : null,
      },
    });
  } catch (error) {
    console.error("Error logging Galileo trace:", error);
    return NextResponse.json(
      { error: "Failed to log trace", details: String(error) },
      { status: 500 }
    );
  }
}
