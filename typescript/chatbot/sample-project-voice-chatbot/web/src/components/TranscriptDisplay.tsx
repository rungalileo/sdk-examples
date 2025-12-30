"use client";

import { useEffect, useRef } from "react";

export interface TranscriptMessage {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: Date;
}

interface TranscriptDisplayProps {
  messages: TranscriptMessage[];
}

export function TranscriptDisplay({ messages }: TranscriptDisplayProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>Start a conversation to see the transcript</p>
      </div>
    );
  }

  return (
    <div
      ref={scrollRef}
      className="flex flex-col gap-3 h-full overflow-y-auto p-4"
    >
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
        >
          <div
            className={`max-w-[80%] rounded-lg px-4 py-2 ${
              message.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            }`}
          >
            <p className="text-sm">{message.content}</p>
            <p className="text-xs opacity-70 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
