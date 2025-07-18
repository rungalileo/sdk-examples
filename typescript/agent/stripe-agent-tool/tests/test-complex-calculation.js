const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testComplexCalculation() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing complex calculation handling...\n');

  // Test 1: Simple product inquiry
  console.log('Test 1: Simple product inquiry');
  const response1 = await agent.processMessage('What products do you have?');
  console.log('Success:', response1.success);
  console.log('Tools used:', response1.data?.toolsUsed);
  console.log('Should work with increased iterations');
  console.log('---\n');

  // Test 2: Complex calculation request
  console.log('Test 2: Complex calculation request');
  const response2 = await agent.processMessage('can you create a payment link for however many telescopes i can buy for one million dollars');
  console.log('Success:', response2.success);
  console.log('Message:', response2.message);
  console.log('Tools used:', response2.data?.toolsUsed);
  console.log('Should complete without max iterations error');
  console.log('---\n');

  // Test 3: Another complex request
  console.log('Test 3: Another complex request');
  const response3 = await agent.processMessage('I have $500, what can I buy and how many?');
  console.log('Success:', response3.success);
  console.log('Tools used:', response3.data?.toolsUsed);
  console.log('Should complete without max iterations error');
  console.log('---\n');

  // Test 4: Normal conclusion
  console.log('Test 4: Normal conclusion');
  const response4 = await agent.processMessage('Thanks!');
  console.log('Success:', response4.success);
  console.log('Message:', response4.message);
  console.log('Should conclude session naturally');
  console.log('---\n');

  console.log('✅ Complex calculation test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- Complex operations should complete without max iterations error');
  console.log('- Agent should handle multi-step calculations properly');
  console.log('- Sessions should still conclude naturally when appropriate');
}

testComplexCalculation().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
