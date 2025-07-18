"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const StripeAgent_1 = require("./agents/StripeAgent");
const GalileoLogger_1 = require("./utils/GalileoLogger");
async function main() {
    console.log('🚀 Stripe Agent Demo');
    try {
        // Initialize the agent
        const agent = new StripeAgent_1.StripeAgent();
        await agent.init(); // Ensure agent is fully initialized
        const galileoLogger = new GalileoLogger_1.GalileoAgentLogger();
        // Example interactions
        const examples = [
            {
                description: "Create a payment link for a digital product",
                message: "Create a payment link for a digital course called 'TypeScript Mastery' priced at $99 USD"
            },
            {
                description: "Create a customer record",
                message: "Create a new customer with email john.doe@example.com and name John Doe"
            },
            {
                description: "List existing products",
                message: "Show me all the products in my Stripe account"
            },
            {
                description: "Create a subscription product",
                message: "Create a monthly subscription product called 'Premium Plan' for $29.99 USD"
            }
        ];
        console.log('🤖 Running example interactions...\n');
        for (let i = 0; i < examples.length; i++) {
            const example = examples[i];
            console.log(`\n📝 ${example.description}`);
            console.log(`💬 ${example.message}`);
            try {
                const response = await agent.processMessage(example.message);
                if (response.success) {
                    console.log(`🤖 ${response.message}`);
                    if (response.data) {
                        console.log(`⏱️  Time: ${response.data.executionTime}ms | 🔧 Tools: ${response.data.toolsUsed.join(', ') || 'None'}`);
                    }
                }
                else {
                    console.log(`❌ Agent Error: ${response.message}`);
                    if (response.error) {
                        console.log(`🐛 ${response.error}`);
                    }
                }
            }
            catch (error) {
                console.error(`💥 Unexpected error:`, error);
            }
            // Add a small delay between examples
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        // Optionally, you can log conversation history to Galileo or generate reports here if needed.
    }
    catch (error) {
        console.error('💥 Unexpected error in main:', error);
    }
}
// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down gracefully...');
    process.exit(0);
});
process.on('SIGTERM', () => {
    console.log('\n👋 Received SIGTERM, shutting down...');
    process.exit(0);
});
// Run the main function
if (require.main === module) {
    main().catch(error => {
        console.error('💥 Unhandled error:', error);
        process.exit(1);
    });
}
//# sourceMappingURL=index.js.map