const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testPaymentLinkFix() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing payment link schema fix...\n');

  // Test 1: Ask what they offer (should list products, not try to create payment link)
  console.log('Test 1: General product inquiry');
  const response1 = await agent.processMessage('what do you offer that would be a good fit');
  console.log('Response 1:', response1.message);
  console.log('Success:', response1.success);
  console.log('Should list products without schema error\n---\n');

  // Test 2: Specific purchase intent (should guide to proper format)
  console.log('Test 2: Purchase intent with specific item');
  const response2 = await agent.processMessage('I want to buy a telescope for $299');
  console.log('Response 2:', response2.message);
  console.log('Success:', response2.success);
  console.log('---\n');

  // Test 3: Try to create payment link with proper format
  console.log('Test 3: Request payment link with proper details');
  const response3 = await agent.processMessage('Create a payment link for a Space Telescope that costs $299');
  console.log('Response 3:', response3.message);
  console.log('Success:', response3.success);
  console.log('---\n');

  console.log('✅ All tests completed!');
}

testPaymentLinkFix().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
