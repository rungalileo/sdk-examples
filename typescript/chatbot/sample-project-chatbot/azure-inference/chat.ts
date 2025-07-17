import ModelClient from "@azure-rest/ai-inference";
import { AzureKeyCredential } from "@azure/core-auth";

import { getLogger, log } from "galileo";

// Load environment variables from .env file
import dotenv from 'dotenv';
dotenv.config();

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
 * Sends the chat history to the Azure AI Inference API and returns the response.
 * 
 * The response is logged manually to Galileo as an LLM span, including the number of
 * input and output tokens, the model used, and the duration of the request in nanoseconds.
 *
 * @returns The response from the LLM.
 */
async function sendChatToAzure(): Promise<string> {
    // Create an Azure AI inference client
    // This will use the environment variables set in the .env file
    const credential = new AzureKeyCredential(process.env["AZURE_AI_INFERENCE_API_KEY"]!);
    // @ts-expect-error TS2345
    const client = new ModelClient(process.env["AZURE_AI_INFERENCE_ENDPOINT"]!,
        credential);

    // Get the Galileo logger instance
    const galileoLogger = getLogger();

    // Capture the current time in nanoseconds for logging
    const startTimeNs = getNanoSecTime();

    // Send the chat history to Azure AI Inference and get the response
    const response = await client.path("/chat/completions").post({
        body: {
            messages: chatHistory,
            model: modelName
        }
    });

    const choice = response.body.choices[0];
    const content = choice.message?.content ?? "";

    // Print the response to the console
    process.stdout.write(content + "\n");

    // Log an LLM span using the response from Azure AI
    galileoLogger.addLlmSpan({
        input: chatHistory,
        output: content,
        model: modelName,
        numInputTokens: response.usage?.promptTokens,
        numOutputTokens: response.usage?.completionTokens,
        totalTokens: response.usage?.totalTokens,
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
    response = await sendChatToAzure();

    // Append the assistant's response to the chat history
    chatHistory.push({ "role": "assistant", "content": response });

    // Return the full response after streaming is complete
    return response;
});