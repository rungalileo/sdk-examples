const { StripeAgent } = require('../dist/agents/StripeAgent');

async function testRealInventory() {
  const agent = new StripeAgent();
  await agent.init();

  console.log('🧪 Testing real inventory enforcement...\n');

  // Test 1: Ask what's available - should check real inventory
  console.log('Test 1: Ask what products are available');
  const response1 = await agent.processMessage('What products do you have available?');
  console.log('Response:', response1.message);
  console.log('Should list real products from Stripe inventory\n---\n');

  // Test 2: Ask for specific product - should check if it exists
  console.log('Test 2: Ask for specific product');
  const response2 = await agent.processMessage('Do you have a space helmet?');
  console.log('Response:', response2.message);
  console.log('Should check inventory first before responding\n---\n');

  // Test 3: Ask for product that might not exist
  console.log('Test 3: Ask for product that might not exist');
  const response3 = await agent.processMessage('I want to buy a rocket ship');
  console.log('Response:', response3.message);
  console.log('Should check inventory and explain what\'s actually available\n---\n');

  // Test 4: General purchase intent - should check inventory first
  console.log('Test 4: General purchase intent');
  const response4 = await agent.processMessage('I want to buy something cool');
  console.log('Response:', response4.message);
  console.log('Should check actual inventory before suggesting anything\n---\n');

  // Test 5: Ask for recommendations
  console.log('Test 5: Ask for product recommendations');
  const response5 = await agent.processMessage('What would you recommend for a space enthusiast?');
  console.log('Response:', response5.message);
  console.log('Should only recommend products that actually exist in inventory\n---\n');

  console.log('✅ Real inventory test completed!');
  console.log('\n🎯 Expected behavior:');
  console.log('- Agent should ALWAYS check list_products before suggesting products');
  console.log('- Agent should NEVER suggest fictional or made-up products');
  console.log('- Agent should only offer products that actually exist in Stripe');
  console.log('- Agent should explain what\'s actually available if requested item doesn\'t exist');
}

testRealInventory().catch(error => {
  console.error('❌ Test failed:', error.message);
  console.error('Full error:', error);
});
