import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { creditScoreTool } from "../tools/creditScoreTool";

/**
 * Create an agent that can help with inquiries about the available credit card options from the Brahe Bank.
 * 
 * returns: A compiled graph for this agent.
 */
export const createCreditScoreAgent = () => {    
    // Create the agent
    const agent = createReactAgent({
        llm: new ChatOpenAI({ model: process.env.MODEL_NAME }),
        tools: [creditScoreTool],
        prompt: `
            You are an expert on credit score. Provide the user with their credit score from the creditScoreTool.
        `,
        name: "credit-score-agent",
    });

    // Return the compiled graph
    return agent;
}