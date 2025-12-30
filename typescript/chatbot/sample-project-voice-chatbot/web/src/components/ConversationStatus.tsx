"use client";

export type ConnectionStatus = "disconnected" | "connecting" | "connected";
export type AgentStatus = "listening" | "thinking" | "speaking";

interface ConversationStatusProps {
  connectionStatus: ConnectionStatus;
  agentStatus?: AgentStatus;
  isSpeaking?: boolean;
}

export function ConversationStatus({
  connectionStatus,
  agentStatus,
  isSpeaking,
}: ConversationStatusProps) {
  const getStatusColor = () => {
    switch (connectionStatus) {
      case "connected":
        return "bg-green-500";
      case "connecting":
        return "bg-yellow-500 animate-pulse";
      case "disconnected":
        return "bg-gray-400";
    }
  };

  const getStatusText = () => {
    if (connectionStatus !== "connected") {
      return connectionStatus === "connecting" ? "Connecting..." : "Disconnected";
    }

    if (isSpeaking) return "You are speaking...";

    switch (agentStatus) {
      case "listening":
        return "Listening...";
      case "thinking":
        return "Thinking...";
      case "speaking":
        return "Agent speaking...";
      default:
        return "Connected";
    }
  };

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className={`w-3 h-3 rounded-full ${getStatusColor()}`} />
      <span className="text-gray-600 dark:text-gray-400">{getStatusText()}</span>
    </div>
  );
}
