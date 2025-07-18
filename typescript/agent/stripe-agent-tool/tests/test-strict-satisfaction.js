const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testStrictSatisfaction() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing strict satisfaction tool enforcement...\n');

  // Test 1: Normal "nope" should trigger feedback buttons
  console.log('Test 1: Say "nope" - should trigger feedback buttons');
  const response1 = await agent.processMessage('nope');
  console.log('Response 1:', response1.message);
  console.log('Contains feedback buttons:', response1.message.includes('📋'));
  console.log('Tools used:', response1.data?.toolsUsed);
  console.log('---\n');

  // Test 2: "no you cannot help me" should NOT trigger satisfaction tool
  console.log('Test 2: Say "no you cannot help me" - should NOT trigger satisfaction tool');
  const response2 = await agent.processMessage('no you cannot help me');
  console.log('Response 2:', response2.message);
  console.log('Tools used:', response2.data?.toolsUsed);
  console.log('Should NOT use satisfaction_review tool');
  console.log('---\n');

  // Test 3: Clear conversation and try proper feedback
  console.log('Test 3: Clear conversation and try proper feedback flow');
  agent.clearConversationHistory();
  
  const response3a = await agent.processMessage('nope!');
  console.log('Step 3a - "nope!" should show feedback buttons');
  console.log('Contains feedback buttons:', response3a.message.includes('📋'));
  
  const response3b = await agent.processMessage('👍 Great experience!');
  console.log('Step 3b - Valid button click should work');
  console.log('Response 3b:', response3b.message);
  console.log('Tools used:', response3b.data?.toolsUsed);
  console.log('Should use satisfaction_review tool once');
  console.log('---\n');

  // Test 4: Try invalid satisfaction input
  console.log('Test 4: Try invalid satisfaction input');
  agent.clearConversationHistory();
  
  const response4 = await agent.processMessage('I am not satisfied');
  console.log('Response 4:', response4.message);
  console.log('Tools used:', response4.data?.toolsUsed);
  console.log('Should NOT use satisfaction_review tool');
  console.log('---\n');

  console.log('✅ Strict satisfaction test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- "nope" or "nope!" should trigger feedback buttons');
  console.log('- "no you cannot help me" should NOT trigger satisfaction tool');
  console.log('- Only "👍 Great experience!" or "👎 Could be better" should trigger satisfaction tool');
  console.log('- All other text should NOT trigger satisfaction tool');
}

testStrictSatisfaction().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
