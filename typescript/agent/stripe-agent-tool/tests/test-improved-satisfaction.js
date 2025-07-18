const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testImprovedSatisfaction() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing improved satisfaction system...\n');

  // Test 1: Normal interaction without satisfaction trigger (should NOT trigger feedback)
  console.log('Test 1: Normal interaction with "great" keyword');
  const response1 = await agent.processMessage('I need a great birthday gift for an astronaut');
  console.log('Response:', response1.message);
  console.log('Should NOT contain feedback prompt\n---\n');

  // Test 2: Purchase intent detection
  console.log('Test 2: Purchase intent detection');
  const response2 = await agent.processMessage('I want to buy a space telescope');
  console.log('Response:', response2.message);
  console.log('Should contain purchase prompt\n---\n');

  // Test 3: Proper closing statement should trigger feedback prompt
  console.log('Test 3: Proper closing statement triggers feedback prompt');
  const response3 = await agent.processMessage('Thanks, that\'s all I needed!');
  console.log('Response:', response3.message);
  console.log('Should contain clickable feedback buttons\n---\n');

  // Test 4: Thumbs up feedback from button click
  console.log('Test 4: Thumbs up feedback from button');
  const response4 = await agent.processMessage('👍 Great experience!');
  console.log('Response:', response4.message);
  console.log('Should conclude session\n---\n');

  // Test 5: Try to use satisfaction tool again (should be blocked)
  console.log('Test 5: Try satisfaction tool again (should be blocked)');
  try {
    const response5 = await agent.processMessage('👎 Could be better');
    console.log('Response:', response5.message);
    console.log('Should say already completed\n---\n');
  } catch (error) {
    console.log('Error (expected):', error.message);
  }

  // Test 6: Standalone "great" should trigger feedback
  console.log('Test 6: Reset and test standalone "great"');
  agent.clearConversationHistory();
  const response6 = await agent.processMessage('Great!');
  console.log('Response:', response6.message);
  console.log('Should contain feedback prompt\n---\n');

  console.log('✅ All tests completed!');
}

testImprovedSatisfaction().catch(console.error);
