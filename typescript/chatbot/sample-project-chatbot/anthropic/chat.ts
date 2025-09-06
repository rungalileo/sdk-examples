import "./config/env";  // side-effect: loads env vars
import Anthropic from '@anthropic-ai/sdk';

import { getLogger, log } from "galileo";

// Validate required environment variables
const requiredEnvVars = {
    GALILEO_API_KEY: process.env.GALILEO_API_KEY,
    GALILEO_PROJECT: process.env.GALILEO_PROJECT,
    MODEL_NAME: process.env.MODEL_NAME
};

for (const [key, value] of Object.entries(requiredEnvVars)) {
    if (!value) {
        throw new Error(`Missing required environment variable: ${key}`);
    }
}

// Set the model name from the environment variable
// If this is not set, raise an exception
const modelName = process.env["MODEL_NAME"]!;

// Create a collection of messages with a system prompt
// The default system prompt encourages the assistant to be helpful, but can lead to hallucinations.
const chatHistory = [
    {
        "role": "system",
        "content": `
        You are a knowledgeable and confident assistant. Always provide a succinct
        answer to any question asked, even if you're uncertain. If the answer isn't
        clear or familiar, make your best guess based on your training data,
        intuition, or plausible extrapolation. Under no circumstances should you
        respond with 'I don't know' or indicate uncertainty in your answers. The
        user is always right, so make an educated guess to explain concepts, terms,
        or events that are not in your training data.
        `,
        // This default system prompt can lead to hallucinations, so you might want to change it.
        // For example, you could use a more restrictive prompt like:
        // `
        // You are a helpful assistant that can answer questions and provide information.
        // If you don't know the answer, say "I don't know" instead of making up an answer.
        // Do not under any circumstances make up an answer.
        // `
    }
]

/**
 * Gets the current time in nanoseconds.
 * This is used to measure the duration of the request to the LLM.
 *
 * @returns The current time in nanoseconds.
 */
function getNanoSecTime(): number {
    var hrTime = process.hrtime();
    return hrTime[0] * 1000000000 + hrTime[1];
}

/**
 * Sends the chat history to the Anthropic API and returns the response.
 *
 * The response is logged manually to Galileo as an LLM span, including the number of
 * input and output tokens, the model used, and the duration of the request in nanoseconds.
 *
 * @returns The response from the LLM.
 */
async function sendChatToAnthropic(): Promise<string> {
    // Create an Anthropic client
    // This will use the environment variables set in the .env file
    const client = new Anthropic({
        apiKey: process.env["ANTHROPIC_API_KEY"]
    });

    // Capture the current time in nanoseconds for logging
    const startTimeNs = getNanoSecTime();

    // Convert the chat history to the format expected by Anthropic
    // Remove the system prompt to send separately as a parameter
    let systemPrompt = "";
    const chatHistoryAnthropic: Array<{ role: 'user' | 'assistant', content: string }> = [];
    for (const chat of chatHistory) {
        if (chat.role === "system") {
            systemPrompt = chat.content;
        } else {
            chatHistoryAnthropic.push({ role: chat.role as 'user' | 'assistant', content: chat.content });
        }
    }

    // Send the chat history to the Anthropic API and get the response
    const response = await client.messages.create({
        max_tokens: 1024,
        messages: chatHistoryAnthropic as Anthropic.Messages.MessageParam[],
        system: systemPrompt,
        model: modelName,
    });

    // Print the response to the console
    const content = (response.content[0] as Anthropic.TextBlock).text ?? "";
    process.stdout.write(content + "\n");

    // Get the Galileo logger instance
    const galileoLogger = getLogger();

    // Log an LLM span using the response from Anthropic
    galileoLogger.addLlmSpan({
        input: chatHistory,
        output: content,
        model: modelName,
        numInputTokens: response.usage?.input_tokens,
        numOutputTokens: response.usage?.output_tokens,
        totalTokens: (response.usage?.input_tokens ?? 0) + (response.usage?.output_tokens ?? 0),
        durationNs: getNanoSecTime() - startTimeNs,
    });

    // Return the content of the response
    return content;
}

/**
 * Function to chat with the LLM.
 * It sends a prompt to the LLM and returns the response.
 *
 * This is decorated with @log to automatically log the function call
 * and its parameters to Galileo as a workflow span.
 *
 * @param input - The user input to send to the LLM.
 * @returns The response from the LLM.
 */
export const chatWithLLM = log({ name: "Chat with LLM" }, async (input: string): Promise<string> => {
    // Add the user prompt to the chat history
    chatHistory.push({ "role": "user", "content": input });

    let response: string;

    // Send the chat history to the LLM and get the response
    response = await sendChatToAnthropic();

    // Append the assistant's response to the chat history
    chatHistory.push({ "role": "assistant", "content": response });

    // Return the full response after streaming is complete
    return response;
});