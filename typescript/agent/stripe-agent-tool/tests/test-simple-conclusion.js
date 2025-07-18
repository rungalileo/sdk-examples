const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testSimpleConclusion() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing simple session conclusion...\n');

  // Test 1: Normal conversation
  console.log('Test 1: Normal conversation');
  const response1 = await agent.processMessage('Hello, what do you offer?');
  console.log('Response 1:', response1.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('---\n');

  // Test 2: Purchase something
  console.log('Test 2: Purchase request');
  const response2 = await agent.processMessage('I want to buy a telescope');
  console.log('Response 2:', response2.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('---\n');

  // Test 3: User indicates they're done - should conclude session
  console.log('Test 3: User says "thanks" - should conclude session');
  const response3 = await agent.processMessage('Thanks, that\'s all I need!');
  console.log('Response 3:', response3.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('Should conclude session naturally');
  console.log('---\n');

  // Test 4: Try to continue after session concluded
  console.log('Test 4: Try to continue after session concluded');
  const response4 = await agent.processMessage('Actually, I have another question');
  console.log('Response 4:', response4.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('Should start new session');
  console.log('---\n');

  // Test 5: Try "nope" - should also conclude session
  console.log('Test 5: User says "nope" - should conclude session');
  const response5 = await agent.processMessage('nope');
  console.log('Response 5:', response5.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('Should conclude session naturally');
  console.log('---\n');

  // Test 6: Try problematic input that was causing issues
  console.log('Test 6: Try "no you cannot help me" - should conclude session');
  const response6 = await agent.processMessage('no you cannot help me');
  console.log('Response 6:', response6.message);
  console.log('Session active:', agent.getSessionStatus().active);
  console.log('Should handle gracefully without tool errors');
  console.log('---\n');

  console.log('✅ Simple conclusion test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- Normal conversation should continue');
  console.log('- "Thanks", "nope", and other closing indicators should conclude session');
  console.log('- No satisfaction tool errors or backend disconnections');
  console.log('- Clean session management throughout');
}

testSimpleConclusion().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
