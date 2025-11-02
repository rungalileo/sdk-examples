import "./src/config/env";  // side-effect: loads env vars
import { createDataset, GalileoScorers, getDataset, runExperiment } from "galileo";
import { chatWithLLM } from "./chat";
import fs from 'fs';
import path from 'path';

/**
 * This function is used to send input to the LLM for the chatbot.
 * It takes a dataset row, and sends the input value to the chat with LLM function.
 * 
 * @param {Object} datasetRow - The input object containing the user's question.
 * @returns {Promise<string>} - The response from the LLM.
 */
const sendInputToLlm = async (datasetRow: any): Promise<string> => {
    return chatWithLLM(datasetRow.input);
};

describe('Chatbot Galileo Tests', () => {
    beforeAll(async () => {

        // Verify required environment variables are set
        // You will also need to set up the environment variables for your OpenAI API connection.
        if (!process.env.GALILEO_PROJECT || !process.env.GALILEO_API_KEY) {
            throw new Error(
                "GALILEO_PROJECT and GALILEO_API_KEY environment variables are required"
            );
        }

        // Check to see if we already have the dataset, if not we can create it.
        let dataset = await getDataset({
            name: "simple-chatbot-unit-test-dataset",
        });

        // If we don't have the dataset, create it with data from the dataset.json file. Some of these questions
        // are designed to be factual, while others are designed to be nonsensical or not
        // answerable by the model. This will help us test the correctness and instruction adherence
        // of the model when running the experiment.
        if (dataset === null) {
            // Load test data from the dataset.json file
            const datasetPath = path.join(__dirname, '..', 'dataset.json');
            const testData = JSON.parse(fs.readFileSync(datasetPath, 'utf8'));
            dataset = await createDataset(testData, "simple-chatbot-unit-test-dataset");
        }
    });

    /**
     * This test will run the dataset against our chatbot app using the Galileo experiments framework.
     * This is designed to show how you can run experiments with a dataset against a real-world application.
     */
    test('should run chatbot experiment with Galileo', async () => {
        // Run the experiment using the canned dataset
        const experimentResponse = await runExperiment({
            // This name is reused, so each experiment run will get a generated name
            // with the run date and time
            name: "simple-chatbot-experiment",
            datasetName: "simple-chatbot-unit-test-dataset",
            function: sendInputToLlm,
            metrics: [
                GalileoScorers.Correctness,
                GalileoScorers.InstructionAdherence,
            ],
            projectName: process.env.GALILEO_PROJECT!,
        });

        // Log the experiment response link
        console.log(`Experiment response link: ${experimentResponse.link}`);
    }, 60000); // Increased timeout for API calls
});