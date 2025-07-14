/**
 * A tool for retrieving information from the Pinecone vector database.
 */
import { PineconeStore } from "@langchain/pinecone";
import { OpenAIEmbeddings } from "@langchain/openai";
import { z } from 'zod';

import { Pinecone } from "@pinecone-database/pinecone";
import { tool } from "@langchain/core/tools";

// Load environment variables from .env file so we have the Pinecone API key
import dotenv from 'dotenv';
dotenv.config();

/**
 * RetrievalInput is a Zod schema representing the input for a document retrieval operation.
 * Attributes:
 *   query (string): The search query used to find relevant documents.
 *   k (number, optional): The number of documents to retrieve. Defaults to 3.
 */
const RetrievalInputSchema = z.object({
    query: z.string().describe('The search query to find relevant documents'),
    k: z.number().default(3).describe('Number of documents to retrieve'),
});


/**
 * A retriever class that interfaces with a Pinecone vector store to perform semantic search
 * using OpenAI embeddings. It allows querying the vector store for documents similar to a given query.
 *
 * @remarks
 * This class initializes the OpenAI embeddings and connects to a Pinecone index via the PineconeStore.
 * The `run` method executes a similarity search and returns the most relevant documents' content.
 *
 * @example
 * ```typescript
 * const retriever = new PineconeRetriever('my-index');
 * const result = await retriever.run({ query: 'What is LangChain?', k: 3 });
 * console.log(result);
 * ```
 */
class PineconeRetriever {

    private embeddings: OpenAIEmbeddings;
    private vectorStore: PineconeStore;

    constructor(indexName: string) {
        this.embeddings = new OpenAIEmbeddings();
        const pinecone = new Pinecone();
        this.vectorStore = new PineconeStore(this.embeddings, { pineconeIndex: pinecone.Index(indexName) });
    }

    /**
     * Execute the retrieval.
     * @param input RetrievalInput
     * @returns Promise<string>
     */
    async run(input: any): Promise<string> {
        try {
            const { query, k } = input;
            const results = await this.vectorStore.similaritySearch(query, k);

            if (!results || results.length === 0) {
                return 'No relevant information found in the knowledge base.';
            }

            const formattedResults = results.map((doc, i) => `Document ${i + 1}:\n${doc.pageContent}\n`);
            return formattedResults.join('\n');
        } catch (e: any) {
            return `Error retrieving information: ${e.message || String(e)}`;
        }
    }
}

// Create an instance of the PineconeRetriever with the index name for credit card information
const pineconeRetrievalTool = new PineconeRetriever("credit-card-information");

/**
 * Define a tool for retrieving information from the Pinecone vector database.
 * It extends the ClientTool class.
 */
// @ts-ignore - Complex type instantiation issue with LangChain tool function
export const creditCardInformationRetrievalTool = tool(
    async (input): Promise<string> => {
        try {
            return await pineconeRetrievalTool.run(input);
        } catch (e: any) {
            return `Error retrieving information: ${e.message || String(e)}`;
        }
    },
    {
        name: 'credit_card_information_retrieval',
        description: 'Retrieve relevant information about credit card options from the Brahe Bank knowledge base.',
        schema: RetrievalInputSchema,
    }
);
