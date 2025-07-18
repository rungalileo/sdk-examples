const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testImprovedFeedback() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing improved feedback behavior...\n');

  // Test 1: Normal conversation ending
  console.log('Test 1: Payment completed - ask if anything else needed');
  const response1 = await agent.processMessage('Perfect! Thanks for creating the payment link');
  console.log('Response:', response1.message);
  console.log('Should show feedback buttons\n---\n');

  // Test 2: User says "nope" - should trigger feedback
  console.log('Test 2: User says "nope" - should trigger feedback');
  const response2 = await agent.processMessage('nope');
  console.log('Response:', response2.message);
  console.log('Should show feedback buttons without repetitive follow-up\n---\n');

  // Test 3: Test feedback button click
  console.log('Test 3: Feedback button clicked');
  const response3 = await agent.processMessage('👍 Great experience!');
  console.log('Response:', response3.message);
  console.log('Should complete session\n---\n');

  // Test 4: Try to interact after feedback - should be blocked
  console.log('Test 4: Try to give feedback again');
  const response4 = await agent.processMessage('👎 Could be better');
  console.log('Response:', response4.message);
  console.log('Should say already completed\n---\n');

  console.log('✅ All tests completed!');
}

testImprovedFeedback().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
