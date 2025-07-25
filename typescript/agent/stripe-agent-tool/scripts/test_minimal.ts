import { StripeAgent } from '../src/agents/StripeAgent';

async function testMinimal() {
  try {
    const agent = new StripeAgent();
    await agent.init();
    
    console.log('Testing agent with minimal logging...\n');
    
    const response = await agent.processMessage("What products do you have?");
    
    if (response.success) {
      console.log('✅ Agent response received successfully');
    } else {
      console.log('❌ Agent failed:', response.message);
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testMinimal().catch(console.error); 