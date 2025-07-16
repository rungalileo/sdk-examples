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

    // Start a new session with a UUID as the external ID
    // This way every time you run the application, it will create a new session in Galileo
    // with the entire conversation inside the same session, with each message back and forth
    // logged as different traces within that session.
    const sessionId = crypto.randomUUID();
    await galileoLogger.startSession({ externalId: sessionId });

    // Create a readline interface to read input from the terminal
    // This allows the user to interact with the chatbot through the terminal.
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

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

        // Start a trace for the user input
        galileoLogger.startTrace({ name: "Conversation step", input: userInput });

        // Call the chatWithLLM function to get a response from the LLM
        const response = await chatWithLLM(userInput);

        // Conclude and flush the logger after each interaction
        // so that a new trace is started each time
        galileoLogger.conclude({ output: response });
        await galileoLogger.flush();
    }
    rl.close();
})();
