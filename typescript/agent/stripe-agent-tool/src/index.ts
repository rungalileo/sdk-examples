// Enable LangChain callbacks for Galileo integration
process.env.LANGCHAIN_LOGGING = 'info';
process.env.LANGCHAIN_VERBOSE = 'false';
process.env.LANGCHAIN_CALLBACKS = 'true';

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
        description: "Create a payment link for a digital product",
        message: "Create a payment link for a digital course called 'TypeScript Mastery' priced at $99 USD"
      },
      {
        description: "Create a customer record",
        message: "Create a new customer with email john.doe@example.com and name John Doe"
      },
      {
        description: "List existing products",
        message: "Show me all the products in my Stripe account"
      },
      {
        description: "Create a subscription product",
        message: "Create a monthly subscription product called 'Premium Plan' for $29.99 USD"
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