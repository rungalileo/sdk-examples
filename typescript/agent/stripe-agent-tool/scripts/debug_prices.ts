import Stripe from 'stripe';
import { env } from '../src/config/environment';

const stripe = new Stripe(env.stripe.secretKey, {
  apiVersion: '2025-06-30.basil',
});

async function debugPrices() {
  console.log('🔍 Debugging Stripe price creation...\n');
  
  try {
    // First, let's check what products exist
    console.log('📦 Checking existing products...');
    const products = await stripe.products.list({ limit: 10 });
    console.log(`Found ${products.data.length} products`);
    
    if (products.data.length > 0) {
      const firstProduct = products.data[0];
      console.log(`\n🔍 Examining first product: ${firstProduct.name}`);
      console.log(`Product ID: ${firstProduct.id}`);
      console.log(`Active: ${firstProduct.active}`);
      
      // Check if this product has prices
      console.log('\n💰 Checking prices for this product...');
      const prices = await stripe.prices.list({ 
        product: firstProduct.id,
        active: true 
      });
      
      console.log(`Found ${prices.data.length} active prices`);
      
      if (prices.data.length > 0) {
        const firstPrice = prices.data[0];
        console.log(`\n📊 Price details:`);
        console.log(`Price ID: ${firstPrice.id}`);
        console.log(`Amount: ${firstPrice.unit_amount}`);
        console.log(`Currency: ${firstPrice.currency}`);
        console.log(`Active: ${firstPrice.active}`);
        console.log(`Type: ${firstPrice.type}`);
        console.log(`Recurring: ${JSON.stringify(firstPrice.recurring)}`);
      } else {
        console.log('❌ No active prices found for this product');
        
        // Try to create a price for this product
        console.log('\n🛠️ Attempting to create a price...');
        try {
          const newPrice = await stripe.prices.create({
            product: firstProduct.id,
            unit_amount: 9999, // $99.99
            currency: 'usd',
            active: true
          });
          
          console.log(`✅ Successfully created price:`);
          console.log(`Price ID: ${newPrice.id}`);
          console.log(`Amount: ${newPrice.unit_amount}`);
          console.log(`Active: ${newPrice.active}`);
          
        } catch (priceError) {
          console.error('❌ Failed to create price:', priceError);
        }
      }
    }
    
    // Test creating a new product with price
    console.log('\n🧪 Testing new product creation...');
    try {
      const testProduct = await stripe.products.create({
        name: 'Test Product - Debug',
        description: 'Testing price creation',
        active: true
      });
      
      console.log(`✅ Created test product: ${testProduct.id}`);
      
      const testPrice = await stripe.prices.create({
        product: testProduct.id,
        unit_amount: 5000, // $50.00
        currency: 'usd',
        active: true
      });
      
      console.log(`✅ Created test price: ${testPrice.id}`);
      console.log(`Amount: ${testPrice.unit_amount} ($${(testPrice.unit_amount! / 100).toFixed(2)})`);
      
      // Clean up - delete the test product
      await stripe.products.del(testProduct.id);
      console.log('🧹 Cleaned up test product');
      
    } catch (testError) {
      console.error('❌ Test failed:', testError);
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  }
}

debugPrices().catch(console.error); 