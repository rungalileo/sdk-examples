"use client";

import { useState, useRef } from "react";
import { VoiceConversation, VoiceConversationHandle } from "@/components/VoiceConversation";
import { useGalileo } from "@/hooks/useGalileo";

export default function Home() {
  const galileo = useGalileo();
  const [guardrailWarning, setGuardrailWarning] = useState<string | null>(null);
  const conversationRef = useRef<VoiceConversationHandle>(null);

  const handleUserTranscript = (transcript: string) => {
    console.log("User said:", transcript);
    galileo.logUserTurn(transcript);
  };

  const handleAgentResponse = async (response: string, latencyMs: number) => {
    console.log("Agent responded:", response, `(${latencyMs}ms)`);

    const result = await galileo.logAgentTurn(response, latencyMs);

    // Check for guardrail triggers
    if (result?.guardrails?.blocked) {
      const triggeredRules = [
        ...(result.guardrails.inputResult?.triggeredRules || []),
        ...(result.guardrails.outputResult?.triggeredRules || []),
      ];

      const ruleNames = triggeredRules.map((r) => r.metric).join(", ");
      setGuardrailWarning(`Guardrail triggered: ${ruleNames} - Ending conversation.`);

      // End the conversation when guardrail is triggered
      conversationRef.current?.stopConversation();

      // Clear warning after 5 seconds
      setTimeout(() => setGuardrailWarning(null), 5000);
    }
  };

  const handleSessionStart = (sessionId: string) => {
    console.log("Session started:", sessionId);
    galileo.startSession(sessionId);
    setGuardrailWarning(null);
  };

  const handleSessionEnd = () => {
    console.log("Session ended");
    galileo.endSession();
  };

  return (
    <main className="min-h-screen flex flex-col p-4 md:p-8">
      <div className="text-center mb-6">
        <h1 className="text-3xl md:text-4xl font-bold mb-2">
          ElevenLabs + Galileo Voice Agent
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Voice conversation with AI observability and guardrails
        </p>
      </div>

      {/* Guardrail Warning Banner */}
      {guardrailWarning && (
        <div className="max-w-2xl mx-auto w-full mb-4 p-3 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded-lg text-sm flex items-center gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <span>{guardrailWarning}</span>
        </div>
      )}

      <div className="flex-1 flex items-start justify-center">
        <VoiceConversation
          ref={conversationRef}
          onUserTranscript={handleUserTranscript}
          onAgentResponse={handleAgentResponse}
          onSessionStart={handleSessionStart}
          onSessionEnd={handleSessionEnd}
        />
      </div>
    </main>
  );
}
