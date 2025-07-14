
import { ChatOpenAI } from "@langchain/openai";
import { createCreditCardInformationAgent } from "./creditCardInformationAgent";
import { createSupervisor } from "@langchain/langgraph-supervisor";

// Supervisor Agent for Brahe Bank Application


// Define the agents that the supervisor will manage
const creditCardInformationAgent = createCreditCardInformationAgent();

export function createSupervisorAgent() {
    /**
     * Create a supervisor agent that manages all the agents in the Brahe Bank application.
     */
    const bankSupervisorAgent = createSupervisor({
        llm: new ChatOpenAI({ model: "gpt-4.1-mini" }),
        agents: [creditCardInformationAgent],
        prompt: `
            You are a supervisor managing the following agents:
            - a credit card information agent. Assign any tasks related to information about credit cards to this agent
            Otherwise, only respond with 'I don't know' or 'I cannot answer that question'.
            If you need to ask the user for more information, do so in a concise manner.
        `,
        addHandoffBackMessages: true,
        outputMode: "full_history",
        supervisorName: "brahe-bank-supervisor-agent",
    }).compile();

    (bankSupervisorAgent as any).name = "brahe-bank-supervisor-agent";

    // Uncomment the following lines to print the compiled graph to the console in Mermaid format
    // console.log("Compiled Bank Supervisor Agent Graph:");
    // console.log(bankSupervisorAgent.getGraph().drawMermaid());

    return bankSupervisorAgent;
}
