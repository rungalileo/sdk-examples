import "./config/env";  // side-effect: loads env vars
import { getLogger, log, wrapOpenAI } from "galileo";

import { OpenAI } from "openai";


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
 * This sends the chat history to the OpenAI API and returns the response.
 *
 * The streamed response is also printed to the console in real-time.
 *
 * The response is logged automatically to Galileo as an LLM span, including the number of
 * input and output tokens, the model used, and the duration of the request in nanoseconds.
 * This is handled by the Galileo OpenAI client
 *
 * @returns The response from the LLM.
 */
async function sendChatToOpenAI(): Promise<string> {
    // Create an OpenAI client
    // This will use the environment variables set in the .env file, so can connect to
    // any OpenAI-compatible API, such as OpenAI or Ollama
    // @ts-expect-error TS2345
    const client = wrapOpenAI(new OpenAI({
        apiKey: process.env.OPENAI_API_KEY!,
        baseURL: process.env.OPENAI_BASE_URL
    }));

    // Send the prompt to the LLM and get a streaming response
    // This uses the Galileo OpenAI client which is configured to log the request and response
    // to Galileo automatically in an LLM span, along with token and other information.
    const stream = await client.chat.completions.create({
        model: modelName!,
        messages: chatHistory,
        stream: true
    });

    // Stream the response to the console and capture the full response
    // Also capture the full response to add to the chat history and return
    let fullResponse = "";
    for await (const chunk of stream) {
        const content = chunk.choices?.[0]?.delta?.content;
        if (content) {
            // Write the chunk to the terminal
            process.stdout.write(content);

            // Append the chunk content to the full response
            fullResponse += content;
        }
    }

    // Print a newline for better formatting
    process.stdout.write("\n");

    // Return the full response from the LLM
    return fullResponse;
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
    response = await sendChatToOpenAI();

    // Append the assistant's response to the chat history
    chatHistory.push({ "role": "assistant", "content": response });

    // Return the full response after streaming is complete
    return response;
});