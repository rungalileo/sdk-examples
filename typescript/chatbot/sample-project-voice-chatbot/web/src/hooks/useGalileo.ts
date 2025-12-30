"use client";

import { useCallback, useRef } from "react";

interface ConversationContext {
  role: string;
  content: string;
}

interface GuardrailResult {
  checked: boolean;
  blocked: boolean;
  overrideMessage?: string;
  inputResult: {
    status: string;
    triggeredRules: Array<{
      metric: string;
      value: number;
      threshold: number;
      operator: string;
    }>;
  } | null;
  outputResult: {
    status: string;
    triggeredRules: Array<{
      metric: string;
      value: number;
      threshold: number;
      operator: string;
    }>;
  } | null;
}

export interface LogTurnResult {
  success: boolean;
  guardrails: GuardrailResult;
}

export function useGalileo() {
  const sessionIdRef = useRef<string | null>(null);
  const turnCountRef = useRef(0);
  const conversationContextRef = useRef<ConversationContext[]>([]);
  const pendingUserTranscriptRef = useRef<string | null>(null);

  const startSession = useCallback(async (sessionId: string) => {
    try {
      const response = await fetch("/api/galileo/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId,
          name: `ElevenLabs-${sessionId.slice(0, 8)}`,
        }),
      });

      if (!response.ok) {
        console.error("Failed to start Galileo session");
        return;
      }

      sessionIdRef.current = sessionId;
      turnCountRef.current = 0;
      conversationContextRef.current = [];
      pendingUserTranscriptRef.current = null;

      console.log("Galileo session started:", sessionId);
    } catch (error) {
      console.error("Error starting Galileo session:", error);
    }
  }, []);

  const logUserTurn = useCallback((transcript: string) => {
    if (!sessionIdRef.current) {
      console.warn("No active Galileo session");
      return;
    }

    // Buffer the user turn - we'll log it when agent responds
    turnCountRef.current += 1;
    pendingUserTranscriptRef.current = transcript;
    conversationContextRef.current.push({ role: "user", content: transcript });

    console.log("Galileo: User turn buffered, waiting for agent response...");
  }, []);

  const logAgentTurn = useCallback(async (
    response: string,
    latencyMs: number
  ): Promise<LogTurnResult | null> => {
    if (!sessionIdRef.current) {
      console.warn("No active Galileo session");
      return null;
    }

    const userTranscript = pendingUserTranscriptRef.current;
    if (!userTranscript) {
      console.warn("No pending user transcript to pair with agent response");
      return null;
    }

    conversationContextRef.current.push({ role: "assistant", content: response });

    try {
      const apiResponse = await fetch("/api/galileo/trace", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sessionId: sessionIdRef.current,
          userTranscript,
          agentResponse: response,
          turnNumber: turnCountRef.current,
          latencyMs,
          conversationContext: [...conversationContextRef.current],
          checkGuardrails: true,
        }),
      });

      const result = await apiResponse.json();

      if (result.success) {
        console.log(`Galileo: Turn ${turnCountRef.current} logged (${latencyMs}ms)`);

        if (result.guardrails?.blocked) {
          console.warn("Guardrail triggered:", result.guardrails);
        }
      }

      // Clear pending user transcript
      pendingUserTranscriptRef.current = null;

      return {
        success: result.success,
        guardrails: result.guardrails,
      };
    } catch (error) {
      console.error("Error logging Galileo turn:", error);
      return null;
    }
  }, []);

  const endSession = useCallback(async () => {
    if (!sessionIdRef.current) {
      console.warn("No active Galileo session");
      return;
    }

    try {
      const response = await fetch(
        `/api/galileo/session?sessionId=${sessionIdRef.current}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        console.log("Galileo session ended");
      }
    } catch (error) {
      console.error("Error ending Galileo session:", error);
    } finally {
      sessionIdRef.current = null;
      turnCountRef.current = 0;
      conversationContextRef.current = [];
      pendingUserTranscriptRef.current = null;
    }
  }, []);

  return {
    startSession,
    logUserTurn,
    logAgentTurn,
    endSession,
  };
}
