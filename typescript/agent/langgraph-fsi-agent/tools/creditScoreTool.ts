/**
 * A tool for retrieving information about credit scores from a financial services knowledge base.
 */
 import { tool } from "@langchain/core/tools";

/**
 * Define a tool for retrieving information about credit scores from a financial services knowledge base.
 */
// @ts-ignore - Complex type instantiation issue with LangChain tool function
export const creditScoreTool = tool(
    async (input: any): Promise<string> => {
        return "Your credit score is 550"; // Always return a credit score of 550 for testing purposes
    },
    {
        name: 'credit_score_tool',
        description: 'Returns a users credit score.',
    }
);