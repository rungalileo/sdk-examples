// Enable LangChain callbacks for Galileo integration
process.env.LANGCHAIN_LOGGING = 'info';
process.env.LANGCHAIN_VERBOSE = 'false';
process.env.LANGCHAIN_CALLBACKS = 'true';

// Suppress Galileo SDK internal messages to reduce console noise
// These messages come from the Galileo SDK when it flushes traces to the server
const originalConsoleError = console.error;
const originalConsoleLog = console.log;
const originalConsoleDebug = console.debug;
const originalConsoleWarn = console.warn;
const originalConsoleInfo = console.info;

console.error = (...args: any[]) => {
  const message = args.join(' ');
  if (message.includes('No node exists for run_id') ||
      message.includes('Flushing') ||
      message.includes('Traces ingested') ||
      message.includes('Successfully flushed') ||
      message.includes('Setting root node') ||
      message.includes('No traces to flush')) {
    return; // Suppress Galileo SDK internal messages
  }
  originalConsoleError(...args);
};

console.log = (...args: any[]) => {
  const message = args.join(' ');
  if (message.includes('Flushing') ||
      message.includes('Traces ingested') ||
      message.includes('Successfully flushed') ||
      message.includes('Setting root node') ||
      message.includes('No traces to flush')) {
    return; // Suppress Galileo SDK internal messages
  }
  originalConsoleLog(...args);
};

// Override console methods to respect VERBOSE environment variable
console.debug = (...args: any[]) => {
  if (process.env.VERBOSE !== 'false') {
    originalConsoleDebug(...args);
  }
};

console.warn = (...args: any[]) => {
  if (process.env.VERBOSE !== 'false') {
    originalConsoleWarn(...args);
  }
};

console.info = (...args: any[]) => {
  if (process.env.VERBOSE !== 'false') {
    originalConsoleInfo(...args);
  }
};

import { StripeAgent } from './agents/StripeAgent';
import { env } from './config/environment';

async function main() {
  let agent: StripeAgent | null = null;
  
  try {
    // Initialize the agent
    agent = new StripeAgent();
    await agent.init(); // Ensure agent is fully initialized
    
    console.log('🚀 Galileo Gizmos CLI Example - Galileo logging enabled');

    // Example interactions 
    const examples = [
      {
        description: "List existing products",
        message: "Show me all the products in my Stripe account"
      },
      {
        description: "Get product pricing",
        message: "What are the prices for Galileo's Premium Telescope?"
      },
      {
        description: "Create a customer record",
        message: "Create a new customer with email john.doe@example.com and name John Doe"
      },
      {
        description: "Check inventory",
        message: "What space exploration gear do you have available?"
      }
    ];

    for (let i = 0; i < examples.length; i++) {
      const example = examples[i];
      try {
        const response = await agent.processMessage(example.message);
        
        if (response.success) {
          console.log(`✅ ${example.description}: Success`);
        } else {
          console.log(`❌ ${example.description}: ${response.message}`);
        }
      } catch (error) {
        console.error(`💥 ${example.description}: Unexpected error:`, error);
      }
      // Add a small delay between examples
      await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // End the conversation and flush traces
    await agent.endConversation();
    console.log('📊 Session concluded and all traces flushed');
    
  } catch (error) {
    console.error('💥 Unexpected error in main:', error);
  } finally {
    // Ensure cleanup happens even if there's an error
    if (agent) {
      try {
        await agent.endConversation();
      } catch (error) {
        console.error('Error during cleanup:', error);
      }
    }
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  process.exit(0);
});

process.on('SIGTERM', () => {
  process.exit(0);
});

// Run the main function
if (require.main === module) {
  main().catch(error => {
    console.error('💥 Unhandled error:', error);
    process.exit(1);
  });
}