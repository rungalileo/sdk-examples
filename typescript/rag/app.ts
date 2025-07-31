import * as dotenv from 'dotenv';
import { OpenAI } from 'openai';
import { log, wrapOpenAI, init, flush } from 'galileo';
import chalk from 'chalk';
import inquirer from 'inquirer';
import readline from 'readline';

// Load environment variables
dotenv.config();

// Check if Galileo logging is enabled
const loggingEnabled = process.env.GALILEO_API_KEY !== undefined;
const projectName = process.env.GALILEO_PROJECT || 'rag_test_typescript';
const logStreamName = process.env.GALILEO_LOG_STREAM || 'dev';

// Initialize OpenAI client with Galileo logging
const client = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));

// Define document type
interface Document {
  id: string;
  text: string;
  metadata: {
    source: string;
    category: string;
  };
}

// Retriever function with Galileo logging
const retrieveDocuments = log(
  { spanType: 'retriever' },
  async (query: string): Promise<Document[]> => {
    // TODO: Replace with actual RAG retrieval
    const documents: Document[] = [
      {
        id: "doc1",
        text: "Galileo is an observability platform for LLM applications. It helps developers monitor, debug, and improve their AI systems by tracking inputs, outputs, and performance metrics.",
        metadata: {
          source: "galileo_docs",
          category: "product_overview"
        }
      },
      {
        id: "doc2",
        text: "RAG (Retrieval-Augmented Generation) is a technique that enhances LLM responses by retrieving relevant information from external knowledge sources before generating an answer.",
        metadata: {
          source: "ai_techniques",
          category: "methodology"
        }
      },
      {
        id: "doc3",
        text: "Common RAG challenges include hallucinations, retrieval quality issues, and context window limitations. Proper evaluation metrics include relevance, faithfulness, and answer correctness.",
        metadata: {
          source: "ai_techniques",
          category: "challenges"
        }
      },
      {
        id: "doc4",
        text: "Vector databases like Pinecone, Weaviate, and Chroma are optimized for storing embeddings and performing similarity searches, making them ideal for RAG applications.",
        metadata: {
          source: "tech_stack",
          category: "databases"
        }
      },
      {
        id: "doc5",
        text: "Prompt engineering is crucial for RAG systems. Well-crafted prompts should instruct the model to use retrieved context, avoid making up information, and cite sources when possible.",
        metadata: {
          source: "best_practices",
          category: "prompting"
        }
      }
    ];
    return documents;
  }
);

// Main RAG function
async function rag(query: string): Promise<string> {
  const documents = await retrieveDocuments(query);
  
  // Format documents for better readability in the prompt
  let formattedDocs = "";
  documents.forEach((doc, i) => {
    formattedDocs += `Document ${i+1} (Source: ${doc.metadata.source}):\n${doc.text}\n\n`;
  });

  const prompt = `
  Answer the following question based on the context provided. If the answer is not in the context, say you don't know.
  
  Question: ${query}

  Context:
  ${formattedDocs}
  `;

  try {
    console.log(chalk.blue('Generating answer...'));
    const response = await client.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: "You are a helpful assistant that answers questions based only on the provided context." },
        { role: "user", content: prompt }
      ],
    });
    return response.choices[0].message.content?.trim() || 'No response generated';
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return `Error generating response: ${errorMessage}`;
  }
}

async function main() {
  console.log(chalk.bold.blue('=== Galileo RAG Terminal Demo ==='));
  console.log(chalk.gray('This demo shows how to integrate Galileo logging with a RAG system.\n'));

  // Initialize Galileo with project and log stream names
  if (loggingEnabled) {
    try {
      await init({
        projectName,
        logStreamName,
      });
      console.log(chalk.green('✅ Galileo logging is enabled'));
      console.log(chalk.gray(`Project: ${projectName}, Stream: ${logStreamName}\n`));
    } catch (error) {
      console.error(chalk.red('❌ Failed to initialize Galileo:'), error);
    }
  } else {
    console.log(chalk.yellow('⚠️ Galileo logging is disabled'));
    console.log(chalk.gray('Set GALILEO_API_KEY to enable logging\n'));
  }

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  // Track interactions for batched flushing
  let interactionCount = 0;
  const FLUSH_INTERVAL = 3; // Flush every 3 interactions for RAG (smaller interval due to complexity)

  const askQuestion = () => {
    rl.question(
      chalk.cyan('\n? ') + 
      chalk.bold('Enter your question about Galileo, RAG, or AI techniques: '), 
      async (question) => {
        if (question.toLowerCase().trim() === 'exit' || question.toLowerCase().trim() === 'quit') {
          console.log(chalk.bold('\nExiting RAG Demo. Goodbye!'));
          // Final flush on exit
          if (loggingEnabled) {
            try {
              await flush();
            } catch (error) {
              // Silent error handling for flush
            }
          }
          rl.close();
          return;
        }

        if (!question.trim()) {
          console.log(chalk.yellow('Please enter a question or type "exit" to quit.'));
          askQuestion();
          return;
        }

        try {
          console.log(chalk.gray('\n🔍 Processing your question...'));
          
          const answer = await rag(question);
          
          console.log(chalk.bold.green('\n📝 Answer:'));
          console.log(chalk.white(answer));
          
          interactionCount++;
          
          // Only flush periodically instead of after every interaction
          if (loggingEnabled && interactionCount % FLUSH_INTERVAL === 0) {
            try {
              await flush();
            } catch (error) {
              // Silent error handling for flush
            }
          }
        } catch (error) {
          console.error(chalk.red('\n❌ Error processing question:'), error);
        }

        askQuestion();
      }
    );
  };

  askQuestion();
}

// Run the main function
if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
} 