import { trace, context, SpanStatusCode, Span } from "@opentelemetry/api";
import { randomUUID } from "crypto";
import type { LLMResponse, LLMResponseWithToolCall } from "./mock-llm.js";

const tracer = trace.getTracer("otel-ts-collector-demo", "1.0.0");

// ---------------------------------------------------------------------------
// Real OpenAI mode (dynamic import so openai is only loaded when needed)
// ---------------------------------------------------------------------------
async function realLLMCall(
  messages: Array<{ role: string; content: string }>,
  tools?: Array<{ name: string; description: string; parameters: Record<string, unknown> }>,
): Promise<LLMResponseWithToolCall> {
  const { default: OpenAI } = await import("openai");
  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

  const toolDefs = tools
    ? tools.map((t) => ({
        type: "function" as const,
        function: { name: t.name, description: t.description, parameters: t.parameters },
      }))
    : undefined;

  const response = await client.chat.completions.create({
    model: "gpt-4o",
    temperature: 0.7,
    messages: messages as any,
    tools: toolDefs,
  });

  const choice = response.choices[0];
  const result: LLMResponseWithToolCall = {
    content: choice.message.content || "",
    model: response.model,
    inputTokens: response.usage?.prompt_tokens || 0,
    outputTokens: response.usage?.completion_tokens || 0,
    finishReason: choice.finish_reason,
  };

  if (choice.message.tool_calls && choice.message.tool_calls.length > 0) {
    const tc = choice.message.tool_calls[0];
    result.toolCall = {
      name: tc.function.name,
      arguments: JSON.parse(tc.function.arguments),
    };
    result.finishReason = "tool_calls";
  }

  return result;
}

// ---------------------------------------------------------------------------
// System prompt for real mode — encourages tool usage for a complete span tree
// ---------------------------------------------------------------------------
const SYSTEM_PROMPT =
  "You are a restaurant assistant. You MUST use the provided tools to answer " +
  "user questions. For restaurant searches, use web_search. For reservation " +
  "queries, use check_availability. Always call a tool before answering.";

// ---------------------------------------------------------------------------
// Tool definitions for real mode
// ---------------------------------------------------------------------------
const TOOL_DEFS = [
  {
    name: "web_search",
    description: "Search the web for information",
    parameters: {
      type: "object",
      properties: { query: { type: "string", description: "Search query" } },
      required: ["query"],
    },
  },
  {
    name: "check_availability",
    description: "Check restaurant availability",
    parameters: {
      type: "object",
      properties: {
        restaurant: { type: "string" },
        date: { type: "string" },
        party_size: { type: "number" },
      },
      required: ["restaurant", "date", "party_size"],
    },
  },
];

// ---------------------------------------------------------------------------
// Single conversation turn (creates invoke_agent → LLM → tool → LLM)
// ---------------------------------------------------------------------------
interface TurnResult {
  finalAnswer: string;
}

async function runTurnSteps(
  turnCtx: ReturnType<typeof trace.setSpan>,
  userMessage: string,
  turnNumber: number,
  useRealLLM: boolean,
): Promise<TurnResult> {
  const mockLLM = await import("./mock-llm.js");

  // === LLM Call 1: decide what to do ===
  const llm1Answer = await context.with(turnCtx, () =>
    tracer.startActiveSpan("chat", async (llmSpan: Span) => {
      try {
        // GenAI attributes — matched by Galileo's detector (GENAI_ATTRIBUTES set)
        // and mapped by processor (OPERATION_TO_TYPE_MAPPING["chat"] → LLM)
        llmSpan.setAttribute("gen_ai.operation.name", "chat");
        llmSpan.setAttribute("gen_ai.request.model", "gpt-4o");
        llmSpan.setAttribute("gen_ai.provider.name", "openai");

        let response: LLMResponseWithToolCall;
        if (useRealLLM) {
          response = await realLLMCall(
            [
              { role: "system", content: SYSTEM_PROMPT },
              { role: "user", content: userMessage },
            ],
            TOOL_DEFS,
          );
        } else {
          response =
            turnNumber === 1
              ? await mockLLM.mockLLMCallWithToolDecision(userMessage)
              : await mockLLM.mockLLMFollowUpWithTool(userMessage);
        }

        // Token usage — extracted by processor via SCHEMA_MAPPING
        llmSpan.setAttribute("gen_ai.usage.input_tokens", response.inputTokens);
        llmSpan.setAttribute(
          "gen_ai.usage.output_tokens",
          response.outputTokens,
        );
        llmSpan.setAttribute("gen_ai.response.finish_reasons", [
          response.finishReason,
        ]);

        // Input/output via GenAI events — detected by GENAI_EVENTS set
        llmSpan.addEvent("gen_ai.user.message", { content: userMessage });
        llmSpan.addEvent("gen_ai.choice", { message: response.content });

        llmSpan.setStatus({ code: SpanStatusCode.OK });
        return response;
      } catch (err) {
        llmSpan.setStatus({
          code: SpanStatusCode.ERROR,
          message: String(err),
        });
        throw err;
      } finally {
        llmSpan.end();
      }
    }),
  );

  // === Tool Call (if LLM decided to use one) ===
  let toolResult = "";
  if (llm1Answer.toolCall) {
    toolResult = await context.with(turnCtx, () =>
      tracer.startActiveSpan("execute_tool", async (toolSpan: Span) => {
        try {
          const { name: toolName, arguments: toolArgs } =
            llm1Answer.toolCall!;

          // Tool attributes — mapped by processor (OPERATION_TO_TYPE_MAPPING["execute_tool"] → TOOL)
          toolSpan.setAttribute("gen_ai.operation.name", "execute_tool");
          toolSpan.setAttribute("gen_ai.tool.name", toolName);
          toolSpan.setAttribute(
            "gen_ai.tool.call.id",
            `call_${randomUUID().slice(0, 8)}`,
          );
          toolSpan.setAttribute(
            "gen_ai.tool.call.arguments",
            JSON.stringify(toolArgs),
          );

          const result = await mockLLM.mockToolExecution(toolName, toolArgs);

          toolSpan.setAttribute("gen_ai.tool.call.result", result);
          toolSpan.setStatus({ code: SpanStatusCode.OK });
          return result;
        } catch (err) {
          toolSpan.setStatus({
            code: SpanStatusCode.ERROR,
            message: String(err),
          });
          throw err;
        } finally {
          toolSpan.end();
        }
      }),
    );
  }

  // === LLM Call 2: synthesize final answer from tool results ===
  const finalResponse = await context.with(turnCtx, () =>
    tracer.startActiveSpan("chat", async (llm2Span: Span) => {
      try {
        llm2Span.setAttribute("gen_ai.operation.name", "chat");
        llm2Span.setAttribute("gen_ai.request.model", "gpt-4o");
        llm2Span.setAttribute("gen_ai.provider.name", "openai");

        let response: LLMResponse;
        if (useRealLLM) {
          // Pass tool result as a user message — we're making a fresh API call,
          // not continuing the same chat completion, so the "tool" role would
          // require tool_call metadata we don't carry across calls.
          response = (await realLLMCall([
            { role: "system", content: SYSTEM_PROMPT },
            { role: "user", content: userMessage },
            {
              role: "user",
              content: `Tool result from ${llm1Answer.toolCall?.name || "tool"}: ${toolResult}\n\nPlease synthesize a final answer using this information.`,
            },
          ])) as LLMResponse;
        } else {
          response =
            turnNumber === 1
              ? await mockLLM.mockLLMFinalAnswer(toolResult)
              : await mockLLM.mockLLMFollowUpFinalAnswer(toolResult);
        }

        llm2Span.setAttribute(
          "gen_ai.usage.input_tokens",
          response.inputTokens,
        );
        llm2Span.setAttribute(
          "gen_ai.usage.output_tokens",
          response.outputTokens,
        );
        llm2Span.setAttribute("gen_ai.response.finish_reasons", [
          response.finishReason,
        ]);

        llm2Span.addEvent("gen_ai.user.message", {
          content: `Previous context with tool result: ${toolResult}`,
        });
        llm2Span.addEvent("gen_ai.choice", { message: response.content });

        llm2Span.setStatus({ code: SpanStatusCode.OK });
        return response;
      } catch (err) {
        llm2Span.setStatus({
          code: SpanStatusCode.ERROR,
          message: String(err),
        });
        throw err;
      } finally {
        llm2Span.end();
      }
    }),
  );

  return { finalAnswer: finalResponse.content };
}

// ---------------------------------------------------------------------------
// Single conversation turn as its own trace (root span = invoke_agent)
// ---------------------------------------------------------------------------
async function runConversationTurn(
  sessionId: string,
  userMessage: string,
  turnNumber: number,
  useRealLLM: boolean,
): Promise<TurnResult> {
  return tracer.startActiveSpan("invoke_agent", async (turnSpan: Span) => {
    const turnCtx = trace.setSpan(context.active(), turnSpan);

    try {
      // invoke_agent → Galileo maps to GenAISpanType.AGENT (processor.py:41)
      turnSpan.setAttribute("gen_ai.operation.name", "invoke_agent");
      turnSpan.setAttribute("gen_ai.agent.name", "restaurant_assistant");

      // session.id on every root span → Galileo groups them into one session
      turnSpan.setAttribute("session.id", sessionId);

      // Input/output on the root so Galileo shows them at trace level
      turnSpan.addEvent("gen_ai.user.message", { content: userMessage });

      const result = await runTurnSteps(
        turnCtx,
        userMessage,
        turnNumber,
        useRealLLM,
      );

      turnSpan.addEvent("gen_ai.choice", { message: result.finalAnswer });
      turnSpan.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (err) {
      turnSpan.setStatus({
        code: SpanStatusCode.ERROR,
        message: String(err),
      });
      throw err;
    } finally {
      turnSpan.end();
    }
  });
}

// ---------------------------------------------------------------------------
// Full session: 2 turns as separate traces, grouped by session.id
// ---------------------------------------------------------------------------
export async function runSession(useRealLLM: boolean): Promise<void> {
  const sessionId = randomUUID();

  console.log(`\n${"=".repeat(60)}`);
  console.log(`Session: ${sessionId}`);
  console.log(`Mode:    ${useRealLLM ? "Real OpenAI" : "Simulated"}`);
  console.log(`${"=".repeat(60)}\n`);

  // --- Turn 1 (own trace) ---
  const turn1Input = "Help me find a good restaurant nearby";
  console.log(`[Turn 1] User: ${turn1Input}`);

  const turn1 = await runConversationTurn(sessionId, turn1Input, 1, useRealLLM);
  console.log(`[Turn 1] Assistant: ${turn1.finalAnswer}\n`);

  // --- Turn 2 (own trace, same session.id) ---
  const turn2Input =
    "Can you check if they have availability tonight for 2 people?";
  console.log(`[Turn 2] User: ${turn2Input}`);

  const turn2 = await runConversationTurn(sessionId, turn2Input, 2, useRealLLM);
  console.log(`[Turn 2] Assistant: ${turn2.finalAnswer}\n`);
}
