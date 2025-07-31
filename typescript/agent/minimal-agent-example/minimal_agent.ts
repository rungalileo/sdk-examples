import * as dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';
import { OpenAI } from 'openai';
import { log, wrapOpenAI, init, flush } from 'galileo';
import chalk from 'chalk';
import inquirer from 'inquirer';
import readline from 'readline';

// Load environment variables
dotenv.config();

// Suppress any warnings if needed
// process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

// Get Galileo configuration from environment variables
const projectName = process.env.GALILEO_PROJECT || 'agent_test_typescript';
const logStreamName = process.env.GALILEO_LOG_STREAM || 'dev';

// Initialize clients
const client = wrapOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }));
const openaiClient = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// Tool: Convert text to arithmetic expression
const convertTextToArithmeticExpression = log(
  { spanType: 'tool', name: 'convert_text_to_arithmetic_expression' },
  async (text: string): Promise<string> => {
    console.log(chalk.blue(`Converting: ${text}`));
    
    const response = await openaiClient.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { 
          role: "user", 
          content: `Convert the expression ${text} with text numbers to a valid arithmetic expression. Respond with only the arithmetic expression.`
        }
      ],
    });
    
    const result = response.choices[0].message.content?.trim() || '';
    try {
      const expression = result;
      console.log(chalk.green(`Converted to: ${expression}`));
      return expression;
    } catch (error) {
      console.log(chalk.red(`Error parsing: ${result}`));
      return "Error";
    }
  }
);

// Tool: Calculator for arithmetic operations
const calculate = log(
  { spanType: 'tool', name: 'calculate' },
  async (expression: string): Promise<string> => {
    console.log(chalk.blue(`Calculating: ${expression}`));
    
    try {
      // Using Function instead of eval for slightly better security
      // Still not recommended for production without proper validation
      const result = Function(`'use strict'; return (${expression})`)();
      console.log(chalk.green(`Result: ${result}`));
      return `The result of ${expression} is ${result}`;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      return `Error calculating ${expression}: ${errorMessage}`;
    }
  }
);

// Load tools from tools.json
function getTools(): any[] {
  try {
    const toolsPath = path.join(__dirname, 'tools.json');
    const toolsData = fs.readFileSync(toolsPath, 'utf8');
    return JSON.parse(toolsData);
  } catch (error) {
    console.error('Error loading tools:', error);
    return [];
  }
}

// Main processing function
const processQuery = log(
  { spanType: 'llm' },
  async (query: string): Promise<string> => {
    console.log(chalk.blue(`Processing query: ${query}`));
    
    // Initialize conversation history with serializable dictionaries
    const messages: any[] = [
      { role: "system", content: "Convert text expressions to valid arithmetic expressions, then calculate results. Use tools one at a time." },
      { role: "user", content: `Process this query: '${query}'` }
    ];
    
    const tools = getTools();
    const results: string[] = [];
    
    // Agent loop - continue until the LLM decides we're done
    while (true) {
      // Get next tool call from LLM
      const response = await client.chat.completions.create({
        model: "gpt-4o",
        messages: messages,
        tools: tools,
      });
      
      // Convert the assistant message to a serializable dictionary
      const assistantMessage = response.choices[0].message;
      const assistantDict: any = {
        role: "assistant",
        content: assistantMessage.content
      };
      
      // Add tool calls if present
      if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
        const toolCallsList = assistantMessage.tool_calls.map(toolCall => ({
          id: toolCall.id,
          type: "function",
          function: {
            name: toolCall.function.name,
            arguments: toolCall.function.arguments
          }
        }));
        assistantDict.tool_calls = toolCallsList;
      }
          
      messages.push(assistantDict);  // Add assistant's response to history
      
      // Check if LLM is done (no more tool calls)
      if (!assistantMessage.tool_calls || assistantMessage.tool_calls.length === 0) {
        // LLM provided a final answer
        if (assistantMessage.content) {
          results.push(assistantMessage.content);
        }
        break;
      }
      
      // Process the tool call
      for (const toolCall of assistantMessage.tool_calls || []) {
        const functionName = toolCall.function.name;
        const functionArgs = JSON.parse(toolCall.function.arguments);
        
        console.log(chalk.bold(`\nExecuting ${functionName} tool:`));
        
        // Execute the appropriate tool
        let result: string;
        if (functionName === "convert_text_to_arithmetic_expression") {
          const text = functionArgs.text;
          result = await convertTextToArithmeticExpression(text);
        } else if (functionName === "calculate") {
          const expression = functionArgs.expression;
          result = await calculate(expression);
        } else {
          result = `Unknown tool: ${functionName}`;
        }
        
        // Add the tool result to conversation history as a serializable dictionary
        const toolResultMessage = {
          tool_call_id: toolCall.id,
          role: "tool",
          name: functionName,
          content: result
        };
        messages.push(toolResultMessage);
        results.push(result);
      }
    }
    
    // Create a summary
    if (results.length > 0) {        
      return results.join('\n');
    } else {
      return "No results produced.";
    }
  }
);

async function main() {
  // Initialize Galileo with project and log stream names
  await init({
    projectName,
    logStreamName
  });

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log("Welcome to the Minimal Agent!");
  console.log("Ask me anything. Type 'exit' to quit.\n");

  // Track interactions for batched flushing
  let interactionCount = 0;
  const FLUSH_INTERVAL = 5; // Flush every 5 interactions

  const askQuestion = () => {
    rl.question("You: ", async (userInput) => {
      if (userInput.toLowerCase() === "exit") {
        console.log("Goodbye!");
        // Final flush on exit
        try {
          await flush();
        } catch (error) {
          // Silent error handling for flush
        }
        rl.close();
        return;
      }

      try {
        const response = await processQuery(userInput);
        console.log("Agent:", response);

        interactionCount++;
        
        // Only flush periodically instead of after every interaction
        if (interactionCount % FLUSH_INTERVAL === 0) {
          try {
            await flush();
          } catch (error) {
            // Silent error handling for flush
          }
        }
      } catch (error) {
        console.error("Error:", error);
      }

      askQuestion();
    });
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