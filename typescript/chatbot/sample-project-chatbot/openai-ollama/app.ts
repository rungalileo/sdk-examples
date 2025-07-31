/**
 * This file contains a very basic chatbot application to converse with an LLM
 * through your terminal.
 *
 * All interactions are logged to Galileo. The structure is:
 *
 * - A session is started at the beginning of the application,
 *     so every interaction is logged in the same session.
 * - For every message sent by the user, a new trace is started
 * - Each call to the function that interacts with the LLM is logged
 *     as a workflow span
 * - The call to the LLM is logged as an LLM span using the Galileo OpenAI integration
    which logs the span automatically.
 * - After the response is received, the trace is concluded with the response
 *     and flushed to ensure it is sent to Galileo.
 *
 * To run this, you will need to have the following environment variables set:
 * - `GALILEO_API_KEY`: Your Galileo API key.
 * - `GALILEO_PROJECT`: The name of your Galileo project.
 * - `GALILEO_CONSOLE_URL`: Optional. Your Galileo console URL for custom deployments.
 *     If you are using the free version, do not set this.
 *
 * Set the following environment variable for your LLM:
 * - `OPENAI_API_KEY`: Your OpenAI API key. If you are using Ollama then set this to ollama.
 * - `OPENAI_BASE_URL`: The base URL for your OpenAI API. If you are using Ollama,
 *     set this to "http://localhost:11434/v1".
 * - `MODEL_NAME`: The name of the model you want to use.
 */
import * as readline from 'readline';

import { getLogger } from "galileo";

import { chatWithLLM } from './chat';

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
    const sessionName = `chatbot-session-${Date.now()}`;

    await galileoLogger.startSession({ name: sessionName });

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout,
    });

    console.log("Welcome to the Chatbot!");
    console.log("Ask me anything. Type 'exit' to quit.\n");

    // Track interactions for batched flushing
    let interactionCount = 0;
    const FLUSH_INTERVAL = 5; // Flush every 5 interactions

    const askQuestion = () => {
        rl.question("You: ", async (userInput) => {
            if (userInput.toLowerCase() === "exit") {
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
                // Start a new trace for this conversation step
                galileoLogger.startTrace({ name: "Conversation step", input: userInput });

                const response = await chatWithLLM(userInput);
                console.log("Bot:", response);

                interactionCount++;

                // Conclude the trace
                galileoLogger.conclude({ output: response });
                
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
