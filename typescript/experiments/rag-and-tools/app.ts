import dotenv from "dotenv";
import { OpenAI } from "openai";
import { getLogger, wrapOpenAI } from "galileo";

// Load environment variables from .env
dotenv.config();

async function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Capture the current time in nanoseconds for logging
function getNanoSecTime(): number {
    var hrTime = process.hrtime();
    return hrTime[0] * 1000000000 + hrTime[1];
};

// A mock RAG retriever function
async function retrieveHoroscopeData(sign: string): Promise<string[]> {
    const startTimeNs = getNanoSecTime();

    const horoscopes: Record<string, string[]> = {
        Aquarius: [
            "Next Tuesday you will befriend a baby otter.",
            "Next Tuesday you will find a dollar on the ground.",
        ],
        Taurus: [
            "Next Tuesday you will find a four-leaf clover.",
            "Next Tuesday you will have a great conversation with a stranger.",
        ],
        Gemini: [
            "Next Tuesday you will learn to juggle.",
            "Next Tuesday you will discover a new favorite book.",
        ],
    };
    const response = horoscopes[sign] ?? ["No horoscope available."];

    await sleep(100); // Simulate RAG latency

    const galileoLogger = getLogger();
    galileoLogger.addRetrieverSpan({
        name: "get_horoscope",
        input: sign,
        output: response,
        durationNs: getNanoSecTime() - startTimeNs,
    });

    return response;
}

// Tool function to get today's horoscope for a given astrological sign
async function getHoroscope({ sign }: { sign: string }): Promise<string> {
    const startTimeNs = getNanoSecTime();

    const response = (await retrieveHoroscopeData(sign)).join("\n");

    await sleep(100); // Simulate tool latency

    const galileoLogger = getLogger();
    galileoLogger.addToolSpan({
        name: "get_horoscope",
        input: sign,
        output: response,
        durationNs: getNanoSecTime() - startTimeNs,
    });

    await sleep(100); // Simulate tool latency

    return response;
}

// Define a list of callable tools for the model
const tools: any[] = [
    {
        type: "function",
        function: {
            name: "get_horoscope",
            description: "Get today's horoscope for an astrological sign.",
            parameters: {
                type: "object",
                properties: {
                    sign: {
                        type: "string",
                        description: "An astrological sign like Taurus or Aquarius",
                    },
                },
                required: ["sign"],
            },
        },
    },
];

// Map tool names to their implementations
const availableTools: Record<string, (args: any) => any> = {
    get_horoscope: getHoroscope,
};

// Create the OpenAI client
const openai = wrapOpenAI(new OpenAI());

// Call the LLM with the provided messages and tools
async function callLlm(messages: any[]) {
    const response = await openai.chat.completions.create({
        model: "gpt-5.1",
        tools,
        messages,
    });

    return response
}

// Get the user's horoscope given a sign
export async function getUsersHoroscope(sign: string): Promise<string> {
    // Create a running message history list we will add to over time
    const messageHistory: any[] = [
        {
            role: "system",
            content: `You are a helpful assistant that provides horoscopes.
Provide a flowery response based off any information retrieved.
Include typical horoscope phrases, and characteristics of
the sign in question.
`,
        },
        { role: "user", content: `What is my horoscope? I am ${sign}.` },
    ];

    // Prompt the model with tools defined
    let response = await callLlm(messageHistory);

    // Add the tool call to the message history (if any)
    const completionToolCalls = response.choices[0].message.tool_calls ?? [];
    if (completionToolCalls.length > 0) {
        messageHistory.push({
            role: "assistant",
            tool_calls: completionToolCalls.map((tc: any) => ({
                id: tc.id,
                type: "function",
                function: {
                    name: tc.function.name,
                    arguments: tc.function.arguments,
                },
            })),
        });

        // Call any tools the model requested
        for (const call of completionToolCalls) {
            const toolToCall = availableTools[call.function.name];
            const args = JSON.parse(call.function.arguments ?? "{}");
            const result = await toolToCall(args);
            messageHistory.push({
                role: "tool",
                content: String(result),
                tool_call_id: call.id,
                name: call.function.name,
            });
        }

        // Now we call the model again, with the tool results included
        response = await callLlm(messageHistory);
    }

    return response.choices[0].message.content ?? "";
}

async function main() {
    // Get the user's horoscope

    // Start a session and trace
    const galileoLogger = getLogger();
    await galileoLogger.startSession({ name: "RAG with Tools Example" });
    galileoLogger.startTrace({ input: "What is my horoscope? I am Aquarius.", name: "Calling LLM with Tool" });

    const response = await getUsersHoroscope("Aquarius");

    // Conclude the trace and flush
    galileoLogger.conclude({ output: response });
    await galileoLogger.flush();

    console.log(response);
}

(async () => {
    if (require.main === module) {
        await main();
    }
})();