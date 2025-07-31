import Stripe from 'stripe';
import { env } from '../src/config/environment';

const stripe = new Stripe(env.stripe.secretKey, {
  apiVersion: '2025-06-30.basil',
});

async function debugPrices() {
  try {
    // First, let's check what products exist
    const products = await stripe.products.list({ limit: 10 });
    console.log(`Found ${products.data.length} products`);
    
    if (products.data.length > 0) {
      const firstProduct = products.data[0];
      
      // Check if this product has prices
      const prices = await stripe.prices.list({ 
        product: firstProduct.id,
        active: true 
      });
      
      console.log(`Found ${prices.data.length} active prices for ${firstProduct.name}`);
      
      if (prices.data.length === 0) {
        // Try to create a price for this product
        try {
          const newPrice = await stripe.prices.create({
            product: firstProduct.id,
            unit_amount: 9999, // $99.99
            currency: 'usd',
            active: true
          });
          
          console.log(`✅ Successfully created price for ${firstProduct.name}`);
          
        } catch (priceError) {
          console.error('❌ Failed to create price:', priceError);
        }
      }
    }
    
    // Test creating a new product with price
    try {
      const testProduct = await stripe.products.create({
        name: 'Test Product - Debug',
        description: 'Testing price creation',
        active: true
      });
      
      const testPrice = await stripe.prices.create({
        product: testProduct.id,
        unit_amount: 5000, // $50.00
        currency: 'usd',
        active: true
      });
      
      console.log(`✅ Created test product with price: $${(testPrice.unit_amount! / 100).toFixed(2)}`);
      
      // Clean up - delete the test product and its prices
      try {
        // First deactivate the price
        await stripe.prices.update(testPrice.id, { active: false });
        console.log('  - Deactivated test price');
        
        // Then delete the product
        await stripe.products.del(testProduct.id);
        console.log('  ✅ Deleted test product');
        
      } catch (cleanupError) {
        console.error('⚠️ Failed to clean up test product:', cleanupError);
        console.log('  💡 Run "npm run cleanup-test-products" to clean up manually');
      }
      
    } catch (testError) {
      console.error('❌ Test failed:', testError);
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  }
}

debugPrices().catch(console.error); 