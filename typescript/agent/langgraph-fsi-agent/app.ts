/**
 * A demo Financial Services Agent using LangGraph, with Galileo as the evaluation platform.
 */
import * as readline from 'readline';

import { getLogger, GalileoCallback } from "galileo";
import { createSupervisorAgent } from './agents/supervisorAgent';

// Load environment variables from .env file
import dotenv from 'dotenv';
dotenv.config();

// Validate required environment variables
const requiredEnvVars = {
    GALILEO_API_KEY: process.env.GALILEO_API_KEY,
    GALILEO_PROJECT: process.env.GALILEO_PROJECT,
    GALILEO_LOG_STREAM: process.env.GALILEO_LOG_STREAM,
    MODEL_NAME: process.env.MODEL_NAME,
    PINECONE_API_KEY: process.env.PINECONE_API_KEY,
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
};

for (const [key, value] of Object.entries(requiredEnvVars)) {
    if (!value) {
        throw new Error(`Missing required environment variable: ${key}`);
    }
}

// Create a collection of messages with a system prompt
// The default system prompt encourages the assistant to be helpful, but can lead to hallucinations.
const chatHistory = [];

/*
 * Run the chatbot application.
 * This will continuously prompt the user for input, send it to the LLM,
 * and print the response until the user types "exit", "bye", or "quit".
 */
(async () => {
    // Get the Galileo logger instance
    const galileoLogger = getLogger();

    // Start a new session named using the current date and time
    // This way every time you run the application, it will create a new session in Galileo
    // with the entire conversation inside the same session, with each message back and forth
    // logged as different traces within that session.
    const sessionName = `LLM Chatbot session - ${new Date().toISOString()}`;
    await galileoLogger.startSession({ name: sessionName });

    // Create a readline interface to read input from the terminal
    // This allows the user to interact with the chatbot through the terminal.
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    // Create the supervisor agent
    // This agent will manage the conversation and delegate tasks to other agents as needed.
    const supervisorAgent = createSupervisorAgent();

    while (true) {
        // Prompt the user for input
        const userInput = await new Promise<string>((resolve) => {
            rl.question("You: ", resolve);
        });

        // Check if the user wants to exit the chatbot
        if (userInput === null || ["", "exit", "bye", "quit"].includes(userInput.toLowerCase())) {
            console.log("Goodbye!");
            break;
        }

        // Add the user input to the chat history
        chatHistory.push({ role: "user", content: userInput });

        const galileoCallback = new GalileoCallback(galileoLogger, true, false);

        // Invoke the supervisor agent with the chat history
        const response = await supervisorAgent.invoke({
            messages: chatHistory
        }, { configurable: { thread_id: "42" }, callbacks: [galileoCallback] });

        const responseContent = response.messages.slice(-1)[0].content;

        // Log the response to the console
        console.log("Assistant:", responseContent);

        // Add the response to the chat history
        chatHistory.push({ role: "assistant", content: responseContent });

        // Flush the logger after each interaction
        // This can be done automatically by the logger, but doing it explicitly to ensure
        // the console logging looks good.
        await galileoLogger.flush();
    }
    rl.close();
})();