const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testSatisfactionOnce() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing satisfaction tool single-use enforcement...\n');

  // Test 1: Normal conversation flow
  console.log('Test 1: Normal conversation');
  const response1 = await agent.processMessage('Hello, I want to buy something');
  console.log('Response 1 Success:', response1.success);
  console.log('Response 1 Length:', response1.message.length);
  console.log('---\n');

  // Test 2: Indicate done to trigger feedback
  console.log('Test 2: Indicate done to trigger feedback');
  const response2 = await agent.processMessage('Thanks, that\'s all I need');
  console.log('Response 2 Success:', response2.success);
  console.log('Response 2 contains feedback buttons:', response2.message.includes('📋'));
  console.log('---\n');

  // Test 3: Click feedback button - should work once
  console.log('Test 3: Click feedback button (should work once)');
  const response3 = await agent.processMessage('👍 Great experience!');
  console.log('Response 3 Success:', response3.success);
  console.log('Response 3 Message:', response3.message);
  console.log('Tools used:', response3.data?.toolsUsed);
  console.log('Should conclude session successfully');
  console.log('---\n');

  // Test 4: Try to use satisfaction tool again - should be blocked
  console.log('Test 4: Try to use satisfaction tool again');
  const response4 = await agent.processMessage('👎 Could be better');
  console.log('Response 4 Success:', response4.success);
  console.log('Response 4 Message:', response4.message);
  console.log('Tools used:', response4.data?.toolsUsed);
  console.log('Should start new session or block duplicate satisfaction');
  console.log('---\n');

  // Test 5: Continue normal conversation in new session
  console.log('Test 5: Continue normal conversation');
  const response5 = await agent.processMessage('Actually, I have another question');
  console.log('Response 5 Success:', response5.success);
  console.log('Response 5 Message:', response5.message);
  console.log('Should work normally in new session');
  console.log('---\n');

  console.log('✅ Satisfaction single-use test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- Test 3: Satisfaction tool should work once and conclude session');
  console.log('- Test 4: Should NOT call satisfaction tool again');
  console.log('- No backend disconnection or multiple tool calls');
  console.log('- Clean session management throughout');
}

testSatisfactionOnce().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
