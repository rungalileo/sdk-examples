import { StripeAgent } from '../src/agents/StripeAgent';

async function testAgentPrices() {
  console.log('🧪 Testing agent price reading...\n');
  
  try {
    // Initialize the agent
    const agent = new StripeAgent();
    await agent.init();
    
    console.log('✅ Agent initialized successfully');
    
    // Test a simple query to see if prices are being read
    console.log('\n📝 Testing agent response...');
    const response = await agent.processMessage("Show me all your products with prices");
    
    console.log('\n🤖 Agent Response:');
    console.log('Success:', response.success);
    console.log('Message:', response.message);
    
    if (response.data) {
      console.log('Tools Used:', response.data.toolsUsed);
      console.log('Execution Time:', response.data.executionTime + 'ms');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testAgentPrices().catch(console.error); 