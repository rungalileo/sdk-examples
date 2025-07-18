import Stripe from 'stripe';
import { env } from '../src/config/environment';

const stripe = new Stripe(env.stripe.secretKey, {
  apiVersion: '2025-06-30.basil',
});

const spaceProducts = [
  // Astronomical Equipment
  {
    name: "Galileo's Premium Telescope",
    description: "High-powered 8-inch reflector telescope with computerized tracking system",
    price: 129999, // $1,299.99 in cents
    currency: 'usd'
  },
  {
    name: "Stellar Binoculars Pro",
    description: "Professional-grade 20x80 astronomy binoculars for deep space viewing",
    price: 29999,
    currency: 'usd'
  },
  {
    name: "Cosmic Camera Adapter",
    description: "Universal camera mount for capturing stunning astrophotography",
    price: 14999,
    currency: 'usd'
  },
  {
    name: "Planetary Filter Set",
    description: "Complete set of color filters for enhanced planetary observation",
    price: 8999,
    currency: 'usd'
  },
  
  // Space Exploration Gear
  {
    name: "Astronaut Training Suit",
    description: "Authentic replica space suit with life support simulation",
    price: 249999,
    currency: 'usd'
  },
  {
    name: "Zero Gravity Simulator",
    description: "Personal anti-gravity chamber for weightless experience",
    price: 89999,
    currency: 'usd'
  },
  {
    name: "Space Helmet VR",
    description: "Virtual reality helmet with immersive space exploration games",
    price: 39999,
    currency: 'usd'
  },
  {
    name: "Mars Rover Remote Control",
    description: "Miniature Mars rover with HD camera and remote operation",
    price: 19999,
    currency: 'usd'
  },
  
  // Educational & Collectibles
  {
    name: "Mars Rock Collection",
    description: "Authentic meteorite fragments from Mars with certificate",
    price: 8999,
    currency: 'usd'
  },
  {
    name: "Cosmic Discovery Box",
    description: "Monthly subscription box with space science experiments",
    price: 4999,
    currency: 'usd'
  },
  {
    name: "Galileo's Star Map",
    description: "Interactive star map showing constellations and deep space objects",
    price: 2999,
    currency: 'usd'
  },
  {
    name: "Space Mission Patch Set",
    description: "Collection of authentic NASA mission patches",
    price: 3999,
    currency: 'usd'
  },
  
  // Space Food & Nutrition
  {
    name: "Astronaut Food Pack",
    description: "Freeze-dried space meals used by real astronauts",
    price: 7999,
    currency: 'usd'
  },
  {
    name: "Cosmic Energy Bars",
    description: "High-protein space nutrition bars for terrestrial adventures",
    price: 2499,
    currency: 'usd'
  },
  {
    name: "Zero-G Coffee Mug",
    description: "Specialized mug that works in microgravity environments",
    price: 3499,
    currency: 'usd'
  },
  {
    name: "Space Ice Cream",
    description: "Freeze-dried ice cream - the classic astronaut treat",
    price: 1999,
    currency: 'usd'
  },
  
  // Home & Lifestyle
  {
    name: "Nebula Projector",
    description: "Home planetarium that projects stunning nebula patterns",
    price: 15999,
    currency: 'usd'
  },
  {
    name: "Space-Themed Bedding Set",
    description: "Comfortable bedding with galaxy and constellation patterns",
    price: 8999,
    currency: 'usd'
  },
  {
    name: "Cosmic Wall Art",
    description: "LED wall art featuring the solar system and deep space",
    price: 12999,
    currency: 'usd'
  },
  {
    name: "Astronaut Alarm Clock",
    description: "Space-themed alarm clock with rocket launch sounds",
    price: 4499,
    currency: 'usd'
  }
];

async function setupProducts() {
  console.log('🚀 Setting up Galileo\'s Gizmos product catalog...\n');
  
  for (const productData of spaceProducts) {
    try {
      // Create the product
      const product = await stripe.products.create({
        name: productData.name,
        description: productData.description,
        metadata: {
          category: 'space-gizmos',
          brand: 'Galileo\'s Gizmos'
        }
      });
      
      // Create the price for the product
      const price = await stripe.prices.create({
        product: product.id,
        unit_amount: productData.price,
        currency: productData.currency
        // One-time purchase (no recurring parameter needed)
      });
      
      console.log(`✅ Created: ${productData.name} - $${(productData.price / 100).toFixed(2)}`);
      console.log(`   Product ID: ${product.id}`);
      console.log(`   Price ID: ${price.id}\n`);
      
    } catch (error) {
      console.error(`❌ Failed to create ${productData.name}:`, error);
    }
  }
  
  console.log('🎉 Product setup complete! Your Galileo\'s Gizmos catalog is ready.');
  console.log('💡 You can now test the agent with commands like:');
  console.log('   • "Show me all our space products"');
  console.log('   • "I want to buy a telescope"');
  console.log('   • "Create a payment link for the Mars Rock Collection"');
}

// Run the setup
setupProducts().catch(console.error); 