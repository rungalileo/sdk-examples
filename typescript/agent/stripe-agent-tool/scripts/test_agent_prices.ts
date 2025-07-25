import { StripeAgent } from '../src/agents/StripeAgent';

async function testAgentPrices() {
  try {
    // Initialize the agent
    const agent = new StripeAgent();
    await agent.init();
    
    // Test a simple query to see if prices are being read
    const response = await agent.processMessage("Show me all your products with prices");
    
    if (response.success) {
      console.log('✅ Agent price reading test: Success');
    } else {
      console.log('❌ Agent price reading test: Failed');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testAgentPrices().catch(console.error); 