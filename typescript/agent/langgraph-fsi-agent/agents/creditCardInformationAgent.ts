import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { creditCardInformationRetrievalTool } from "../tools/pineconeRetrievalTool";

/**
 * Create an agent that can help with inquiries about the available credit card options from the Brahe Bank.
 * 
 * returns: A compiled graph for this agent.
 */
export const createCreditCardInformationAgent = () => {    
    // Create the agent
    const agent = createReactAgent({
        llm: new ChatOpenAI({ model: "gpt-4.1-mini" }),
        tools: [creditCardInformationRetrievalTool],
        prompt: `
            You are an agent providing help on the credit card options at Brahe Bank.
            Be helpful, but succinct, and do not make up information that you do not already know to be true.
            If you need to retrieve information from the knowledge base, use the tools provided.
            If you are asked questions about credit card options, you can use the information you have to help the user. For example, you can answer questions about which
            card may best align with their interests if their interests align with rewards or features of a card.
            If you do not know the answer to a question, you can say that you do not know.
        `,
        name: "credit-card-agent",
    });

    // Return the compiled graph
    return agent;
}