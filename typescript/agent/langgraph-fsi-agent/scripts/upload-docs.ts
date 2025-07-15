/**
 * This script sets up a Pinecone index for storing and retrieving documents using the documents in the `source-docs` folder.
 *
 * To use this, you will need to have the following environment variables set in the .env file:
 * - `PINECONE_API_KEY`: Your Pinecone API key.
 * - `OPENAI_API_KEY`: Your OpenAI API key (for embeddings).
 */

import { DirectoryLoader } from "langchain/document_loaders/fs/directory";
import { TextLoader } from "langchain/document_loaders/fs/text";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { OpenAIEmbeddings } from "@langchain/openai";
import { PineconeStore } from "@langchain/pinecone";
import { Pinecone } from "@pinecone-database/pinecone";
import { Document } from "@langchain/core/documents";
import * as dotenv from "dotenv";

dotenv.config();

const EMBEDDINGS = new OpenAIEmbeddings();
const PINECONE_API_KEY = process.env.PINECONE_API_KEY;

if (!PINECONE_API_KEY) {
    throw new Error("PINECONE_API_KEY environment variable is required");
}

/**
 * Load all markdown documents from source-docs folder
 */
async function loadDocuments(path: string): Promise<Document[]> {
    const loader = new DirectoryLoader(
        path,
        {
            ".md": (path: string) => new TextLoader(path),
        }
    );
    const documents = await loader.load();
    return documents;
}

/**
 * Chunk documents semantically
 */
async function chunkDocuments(documents: Document[]): Promise<Document[]> {
    const textSplitter = new RecursiveCharacterTextSplitter({
        chunkSize: 1000,
        chunkOverlap: 200,
        separators: [
            "\n\n", // Double newlines (paragraphs)
            "\n",   // Single newlines
            " ",    // Spaces
            ".",    // Sentences
            ",",    // Clauses
            "\u200b", // Zero-width space
            "\uff0c", // Fullwidth comma
            "\u3001", // Ideographic comma
            "\uff0e", // Fullwidth full stop
            "\u3002", // Ideographic full stop
            "",     // Character-level
        ],
    });

    const chunkedDocs = await textSplitter.splitDocuments(documents);
    return chunkedDocs;
}

/**
 * Initialize Pinecone and create/connect to index
 */
async function setupPineconeIndex(indexName: string): Promise<void> {
    const pc = new Pinecone({
        apiKey: PINECONE_API_KEY!,
    });

    // Check if index exists, create if not
    const indexList = await pc.listIndexes();
    const indexExists = indexList.indexes?.some(index => index.name === indexName);

    if (!indexExists) {
        console.log(`Creating new index: ${indexName}`);
        await pc.createIndex({
            name: indexName,
            dimension: 1536, // OpenAI embeddings dimension
            metric: "cosine",
            spec: {
                serverless: {
                    cloud: "aws",
                    region: "us-east-1"
                }
            }
        });
    } else {
        console.log(`Index ${indexName} already exists`);
    }
}

/**
 * Check if the index already contains data
 */
async function checkIndexHasData(indexName: string): Promise<boolean> {
    try {
        const pc = new Pinecone({
            apiKey: PINECONE_API_KEY!,
        });
        const index = pc.index(indexName);
        const stats = await index.describeIndexStats();
        const totalVectorCount = stats.totalRecordCount || 0;
        return totalVectorCount > 0;
    } catch (error) {
        console.error(`Error checking index stats: ${error}`);
        return false;
    }
}

/**
 * Upload chunked documents to Pinecone
 */
async function uploadToPinecone(
    chunkedDocs: Document[],
    indexName: string,
    forceUpload: boolean = false
): Promise<PineconeStore> {
    // Check if index has data and we're not forcing upload
    if (!forceUpload) {
        const hasData = await checkIndexHasData(indexName);
        if (hasData) {
            console.log(`Index ${indexName} already contains data. Skipping upload.`);
            console.log("Use forceUpload=true to overwrite existing data.");
            
            const pc = new Pinecone({
                apiKey: PINECONE_API_KEY!,
            });
            const pineconeIndex = pc.index(indexName);
            
            return new PineconeStore(EMBEDDINGS, {
                pineconeIndex,
            });
        }
    }

    // Create vector store and upload
    console.log(`Uploading ${chunkedDocs.length} chunks to Pinecone...`);
    
    const pc = new Pinecone({
        apiKey: PINECONE_API_KEY!,
    });
    const pineconeIndex = pc.index(indexName);
    
    const vectorStore = await PineconeStore.fromDocuments(
        chunkedDocs,
        EMBEDDINGS,
        {
            pineconeIndex,
        }
    );

    console.log(`Successfully uploaded ${chunkedDocs.length} document chunks to Pinecone`);
    return vectorStore;
}

/**
 * Test document retrieval from Pinecone
 */
async function testRetrieval(indexName: string, query: string): Promise<void> {
    const pc = new Pinecone({
        apiKey: PINECONE_API_KEY!,
    });
    const pineconeIndex = pc.index(indexName);
    
    const vectorStore = new PineconeStore(EMBEDDINGS, {
        pineconeIndex,
    });

    // Test similarity search
    const results = await vectorStore.similaritySearch(query, 3);

    console.log(`\nTest query: '${query}'`);
    console.log(`Found ${results.length} relevant chunks:`);
    results.forEach((doc, i) => {
        console.log(`\n${i + 1}. ${doc.pageContent.substring(0, 200)}...`);
    });
}

interface BankDocument {
    index_name: string;
    path: string;
    test_query: string;
}

const bankDocuments: BankDocument[] = [
    {
        index_name: "credit-card-information",
        path: "source-docs/credit-cards",
        test_query: "credit card",
    }
];

/**
 * Main function to process and upload documents asynchronously
 */
async function main(): Promise<void> {
    for (const doc of bankDocuments) {
        const { index_name: indexName, path, test_query: testQuery } = doc;

        console.log(`Loading documents for ${indexName} folder...`);
        const loadedDocuments = await loadDocuments(path);
        console.log(`Loaded ${loadedDocuments.length} documents`);

        console.log(`Chunking documents for ${indexName}...`);
        const chunkedDocs = await chunkDocuments(loadedDocuments);
        console.log(`Created ${chunkedDocs.length} chunks`);

        console.log(`Setting up Pinecone for ${indexName}...`);
        await setupPineconeIndex(indexName);

        // Only upload if index is new or doesn't have data
        console.log(`Uploading to Pinecone for ${indexName}...`);
        await uploadToPinecone(chunkedDocs, indexName);
    }

    // Wait for Pinecone to index the data
    console.log("Waiting for Pinecone to index the data...");
    await new Promise(resolve => setTimeout(resolve, 30000));

    // Test retrieval for each index
    for (const doc of bankDocuments) {
        const { index_name: indexName, test_query: testQuery } = doc;
        console.log(`Testing retrieval for ${indexName} with query: '${testQuery}'`);
        await testRetrieval(indexName, testQuery);
    }

    console.log("✅ Document processing and upload complete!");
}

// Run the main function if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}
