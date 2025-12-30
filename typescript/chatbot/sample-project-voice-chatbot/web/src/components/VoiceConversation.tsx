"use client";

import { useCallback, useState, forwardRef, useImperativeHandle } from "react";
import { useConversation } from "@elevenlabs/react";
import { ConversationStatus, ConnectionStatus, AgentStatus } from "./ConversationStatus";
import { TranscriptDisplay, TranscriptMessage } from "./TranscriptDisplay";

interface VoiceConversationProps {
  onUserTranscript?: (transcript: string) => void;
  onAgentResponse?: (response: string, latencyMs: number) => void;
  onSessionStart?: (sessionId: string) => void;
  onSessionEnd?: () => void;
}

export interface VoiceConversationHandle {
  stopConversation: () => Promise<void>;
}

export const VoiceConversation = forwardRef<VoiceConversationHandle, VoiceConversationProps>(
  function VoiceConversation({
    onUserTranscript,
    onAgentResponse,
    onSessionStart,
    onSessionEnd,
  }, ref) {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>("disconnected");
  const [agentStatus, setAgentStatus] = useState<AgentStatus>("listening");
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUserTurnTime, setLastUserTurnTime] = useState<number | null>(null);

  const conversation = useConversation({
    onConnect: () => {
      console.log("Connected to ElevenLabs");
      setConnectionStatus("connected");
      setError(null);

      // Generate session ID and notify parent
      const sessionId = crypto.randomUUID();
      onSessionStart?.(sessionId);
    },
    onDisconnect: () => {
      console.log("Disconnected from ElevenLabs");
      setConnectionStatus("disconnected");
      onSessionEnd?.();
    },
    onMessage: (message) => {
      console.log("Message received:", message);

      // Handle different message types based on ElevenLabs SDK
      if (message.source === "user") {
        // User transcript
        const transcript = message.message;
        setLastUserTurnTime(Date.now());

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "user",
            content: transcript,
            timestamp: new Date(),
          },
        ]);

        onUserTranscript?.(transcript);
        setAgentStatus("thinking");
      } else if (message.source === "ai") {
        // Agent response
        const response = message.message;
        const latencyMs = lastUserTurnTime ? Date.now() - lastUserTurnTime : 0;

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "agent",
            content: response,
            timestamp: new Date(),
          },
        ]);

        onAgentResponse?.(response, latencyMs);
        setAgentStatus("listening");
      }
    },
    onError: (error) => {
      console.error("Conversation error:", error);
      setError(typeof error === "string" ? error : "An error occurred");
      setConnectionStatus("disconnected");
    },
  });

  const startConversation = useCallback(async () => {
    setError(null);
    setConnectionStatus("connecting");
    setMessages([]);

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true });

      // Get signed URL from our API
      const response = await fetch("/api/get-signed-url");
      if (!response.ok) {
        throw new Error("Failed to get signed URL");
      }
      const { signedUrl } = await response.json();

      // Start conversation with signed URL
      await conversation.startSession({ signedUrl });
    } catch (err) {
      console.error("Failed to start conversation:", err);
      setError(err instanceof Error ? err.message : "Failed to start conversation");
      setConnectionStatus("disconnected");
    }
  }, [conversation]);

  const stopConversation = useCallback(async () => {
    await conversation.endSession();
    setConnectionStatus("disconnected");
  }, [conversation]);

  // Expose stopConversation to parent via ref
  useImperativeHandle(ref, () => ({
    stopConversation,
  }), [stopConversation]);

  return (
    <div className="flex flex-col h-full w-full max-w-2xl mx-auto">
      {/* Header with status */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold">Voice Conversation</h2>
        <ConversationStatus
          connectionStatus={connectionStatus}
          agentStatus={agentStatus}
          isSpeaking={conversation.isSpeaking}
        />
      </div>

      {/* Transcript area */}
      <div className="flex-1 min-h-[300px] border border-gray-200 dark:border-gray-700 rounded-lg m-4 overflow-hidden">
        <TranscriptDisplay messages={messages} />
      </div>

      {/* Error display */}
      {error && (
        <div className="mx-4 mb-4 p-3 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Controls */}
      <div className="flex justify-center gap-4 p-4 border-t border-gray-200 dark:border-gray-700">
        {connectionStatus === "disconnected" ? (
          <button
            onClick={startConversation}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <MicIcon />
            Start Conversation
          </button>
        ) : (
          <button
            onClick={stopConversation}
            disabled={connectionStatus === "connecting"}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
          >
            <StopIcon />
            {connectionStatus === "connecting" ? "Connecting..." : "End Conversation"}
          </button>
        )}
      </div>
    </div>
  );
});

function MicIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path d="M7 4a3 3 0 016 0v6a3 3 0 01-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" />
    </svg>
  );
}

function StopIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
    </svg>
  );
}
