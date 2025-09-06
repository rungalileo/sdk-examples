import "./config/env";  // side-effect: loads env vars
import { OpenAI } from 'openai';
import { log, wrapOpenAI, init, flush } from 'galileo';
import chalk from 'chalk';
import inquirer from 'inquirer';

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
  console.log('This demo uses a simulated RAG system to answer your questions.\n');
  
  // Initialize Galileo with project and log stream names
  init({
    projectName,
    logStreamName
  });
  
  // Check environment setup
  if (loggingEnabled) {
    console.log(chalk.green('✅ Galileo logging is enabled'));
    console.log(chalk.green(`✅ Project: ${projectName}`));
    console.log(chalk.green(`✅ Log Stream: ${logStreamName}`));
  } else {
    console.log(chalk.yellow('⚠️ Galileo logging is disabled'));
  }
  
  const apiKey = process.env.OPENAI_API_KEY;
  if (apiKey) {
    console.log(chalk.green('✅ OpenAI API Key is set'));
  } else {
    console.log(chalk.red('❌ OpenAI API Key is missing'));
    process.exit(1);
  }
  
  // Main interaction loop
  let continueSession = true;
  while (continueSession) {
    try {
      // Get user query
      const { query } = await inquirer.prompt([
        {
          type: 'input',
          name: 'query',
          message: 'Enter your question about Galileo, RAG, or AI techniques:',
          validate: (input: string) => input.length > 0 ? true : 'Please enter a question'
        }
      ]);
      
      if (['exit', 'quit', 'q'].includes(query.toLowerCase())) {
        break;
      }
      
      const result = await rag(query);
      
      console.log(chalk.bold.green('\nAnswer:'));
      console.log(chalk.green('-------------------------------------------'));
      console.log(result);
      console.log(chalk.green('-------------------------------------------'));
      
      // Ask if user wants to continue
      const { continue: shouldContinue } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'continue',
          message: 'Do you want to ask another question?',
          default: true
        }
      ]);
      
      continueSession = shouldContinue;
    } catch (error) {
      console.error(chalk.red(`Error: ${error instanceof Error ? error.message : String(error)}`));
    }
  }
  
  // Flush Galileo logs
  await flush();
  console.log(chalk.bold('\nExiting RAG Demo. Goodbye!'));
}

// Run the main function
if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
} 