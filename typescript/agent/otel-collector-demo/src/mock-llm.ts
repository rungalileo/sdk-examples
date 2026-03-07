export interface LLMResponse {
  content: string;
  model: string;
  inputTokens: number;
  outputTokens: number;
  finishReason: string;
}

export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

export interface LLMResponseWithToolCall extends LLMResponse {
  toolCall?: ToolCall;
}

async function simulateLatency(minMs: number, maxMs: number): Promise<void> {
  const delay = Math.floor(Math.random() * (maxMs - minMs)) + minMs;
  await new Promise((resolve) => setTimeout(resolve, delay));
}

// Turn 1, step 1: LLM decides to call web_search
export async function mockLLMCallWithToolDecision(
  userMessage: string,
): Promise<LLMResponseWithToolCall> {
  await simulateLatency(200, 500);
  return {
    content:
      "I'll search for restaurants nearby to help you find a good option.",
    model: "gpt-4o",
    inputTokens: 28,
    outputTokens: 42,
    finishReason: "tool_calls",
    toolCall: {
      name: "web_search",
      arguments: { query: "best restaurants near me" },
    },
  };
}

// Turn 1, step 2: LLM synthesizes final answer from tool results
export async function mockLLMFinalAnswer(
  toolResult: string,
): Promise<LLMResponse> {
  await simulateLatency(300, 600);
  return {
    content:
      'Based on the search results, I recommend "The Golden Fork" — a highly rated Italian restaurant just 0.3 miles away. They have excellent pasta and a cozy atmosphere. Rating: 4.8/5 with over 500 reviews. Would you like me to help with a reservation?',
    model: "gpt-4o",
    inputTokens: 156,
    outputTokens: 67,
    finishReason: "stop",
  };
}

// Turn 2, step 1: LLM decides to check availability
export async function mockLLMFollowUpWithTool(
  userMessage: string,
): Promise<LLMResponseWithToolCall> {
  await simulateLatency(200, 400);
  return {
    content: "Let me check their available reservation times for you.",
    model: "gpt-4o",
    inputTokens: 95,
    outputTokens: 35,
    finishReason: "tool_calls",
    toolCall: {
      name: "check_availability",
      arguments: {
        restaurant: "The Golden Fork",
        date: "2026-02-22",
        party_size: 2,
      },
    },
  };
}

// Turn 2, step 2: LLM presents reservation options
export async function mockLLMFollowUpFinalAnswer(
  toolResult: string,
): Promise<LLMResponse> {
  await simulateLatency(250, 500);
  return {
    content:
      "Great news! The Golden Fork has availability tonight at 7:00 PM and 8:30 PM for a party of 2. The 7:00 PM slot is a window table. Shall I book one of these for you?",
    model: "gpt-4o",
    inputTokens: 210,
    outputTokens: 52,
    finishReason: "stop",
  };
}

// Simulated tool execution
export async function mockToolExecution(
  toolName: string,
  args: Record<string, unknown>,
): Promise<string> {
  await simulateLatency(100, 300);

  if (toolName === "web_search") {
    return JSON.stringify({
      results: [
        {
          name: "The Golden Fork",
          cuisine: "Italian",
          rating: 4.8,
          distance: "0.3 mi",
          reviews: 523,
        },
        {
          name: "Sakura Garden",
          cuisine: "Japanese",
          rating: 4.6,
          distance: "0.5 mi",
          reviews: 312,
        },
        {
          name: "Blue Agave",
          cuisine: "Mexican",
          rating: 4.5,
          distance: "0.7 mi",
          reviews: 198,
        },
      ],
    });
  }

  if (toolName === "check_availability") {
    return JSON.stringify({
      restaurant: args.restaurant,
      date: args.date,
      available_slots: ["7:00 PM (window table)", "8:30 PM"],
      party_size: args.party_size,
    });
  }

  return JSON.stringify({ error: `Unknown tool: ${toolName}` });
}
