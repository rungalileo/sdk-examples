const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testPaymentLinkLoop() {
  console.log('🧪 Testing payment link loop issue...\n');
  
  const agent = new StripeAgent();
  await agent.init();

  // Test sequence to reproduce the "infinite list_products / list_prices" loop
  console.log('📝 Step 1: List products (should work normally)');
  const response1 = await agent.processMessage('list products');
  console.log('✅ Response 1:', response1.success);
  console.log('---\n');

  console.log('📝 Step 2: Pick an item (should trigger loop)');
  const response2 = await agent.processMessage('pick item');
  console.log('✅ Response 2:', response2.success);
  console.log('---\n');

  console.log('📝 Step 3: Buy X (should trigger loop)');
  const response3 = await agent.processMessage('buy X');
  console.log('✅ Response 3:', response3.success);
  console.log('---\n');

  console.log('🏁 Test completed');
}

testPaymentLinkLoop().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
