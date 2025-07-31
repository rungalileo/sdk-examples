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

    // Create a unique session name with timestamp
    // This way every time you run the application, it will create a new session in Galileo
    const sessionName = `fsi-agent-session-${Date.now()}`;

    await galileoLogger.startSession({ name: sessionName });

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    console.log("Welcome to the Financial Services Agent!");
    console.log("Ask me about credit scores, credit cards, or other financial services.");
    console.log("Type 'exit' to quit.\n");

    // Track interactions for batched flushing
    let interactionCount = 0;
    const FLUSH_INTERVAL = 5; // Flush every 5 interactions

    const askQuestion = () => {
        rl.question("You: ", async (input) => {
            if (input.toLowerCase() === "exit") {
                console.log("Goodbye!");
                // Final flush on exit
                try {
                    await galileoLogger.flush();
                } catch (error) {
                    // Silent error handling for flush
                }
                rl.close();
                return;
            }

            try {
                const galileoCallback = new GalileoCallback(galileoLogger, true, false);

                const result = await graph.invoke({
                    messages: [new HumanMessage(input)],
                }, { configurable: { thread_id: "42" }, callbacks: [galileoCallback] });

                const lastMessage = result.messages[result.messages.length - 1];
                console.log("Agent:", lastMessage.content);

                interactionCount++;
                
                // Only flush periodically instead of after every interaction
                if (interactionCount % FLUSH_INTERVAL === 0) {
                    try {
                        await galileoLogger.flush();
                    } catch (error) {
                        // Silent error handling for flush
                    }
                }
            } catch (error) {
                console.error("Error:", error);
            }

            askQuestion();
        });
    };

    askQuestion();
})();