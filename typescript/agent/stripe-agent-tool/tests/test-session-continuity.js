const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testSessionContinuity() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing Galileo session continuity...\n');

  // Track session throughout conversation
  let sessionStatus = agent.getSessionStatus();
  console.log('Initial session status:', sessionStatus);

  // Step 1: Start conversation
  console.log('Step 1: Starting conversation');
  const response1 = await agent.processMessage('Hello, I need help');
  sessionStatus = agent.getSessionStatus();
  console.log('After first message - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('---\n');

  // Step 2: Continue conversation
  console.log('Step 2: Continuing conversation');
  const response2 = await agent.processMessage('What products do you have?');
  sessionStatus = agent.getSessionStatus();
  console.log('After second message - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('---\n');

  // Step 3: Make a purchase
  console.log('Step 3: Making a purchase');
  const response3 = await agent.processMessage('I want to buy the Cosmic Explorer Monthly Box');
  sessionStatus = agent.getSessionStatus();
  console.log('After purchase request - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('---\n');

  // Step 4: Provide customer info
  console.log('Step 4: Providing customer info');
  const response4 = await agent.processMessage('My name is Test User and email is test@example.com');
  sessionStatus = agent.getSessionStatus();
  console.log('After customer info - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('---\n');

  // Step 5: Indicate conversation is done
  console.log('Step 5: Indicating conversation is done');
  const response5 = await agent.processMessage('thanks, that\'s all');
  sessionStatus = agent.getSessionStatus();
  console.log('After indicating done - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('Should show feedback buttons');
  console.log('---\n');

  // Step 6: Provide feedback (this should conclude the session)
  console.log('Step 6: Providing feedback');
  const response6 = await agent.processMessage('👍 Great experience!');
  sessionStatus = agent.getSessionStatus();
  console.log('After feedback - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('Should conclude session');
  console.log('---\n');

  // Step 7: Try to continue after session ended
  console.log('Step 7: Trying to continue after session ended');
  const response7 = await agent.processMessage('Actually, I have another question');
  sessionStatus = agent.getSessionStatus();
  console.log('After trying to continue - Session:', sessionStatus.sessionId);
  console.log('Session active:', sessionStatus.active);
  console.log('Should start new session');
  console.log('---\n');

  console.log('✅ Session continuity test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- Steps 1-6 should all be in the SAME session');
  console.log('- Session should only conclude after step 6 (feedback)');
  console.log('- Step 7 should start a NEW session');
}

testSessionContinuity().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
