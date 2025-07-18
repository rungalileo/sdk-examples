"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const StripeAgent_1 = require("./agents/StripeAgent");
const GalileoLogger_1 = require("./utils/GalileoLogger");
const environment_1 = require("./config/environment");
const readline = __importStar(require("readline"));
class GalileoGizmosCustomerService {
    agent;
    galileoLogger;
    rl;
    sessionId = null;
    constructor() {
        this.agent = new StripeAgent_1.StripeAgent();
        this.galileoLogger = new GalileoLogger_1.GalileoAgentLogger();
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: '🚀 You: '
        });
    }
    displayWelcome() {
        console.log('\n🌟✨ Welcome to Galileo\'s Gizmos - Your Space Commerce Headquarters! ✨🌟');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('🛸 Hello! I\'m Gizmo, your AI-powered space commerce assistant!');
        console.log('🌌 I can help you with anything related to our cosmic product catalog:');
        console.log('');
        console.log('   💳 Create payment links for space gadgets');
        console.log('   👥 Manage customer records for space explorers');
        console.log('   📦 Set up product listings for cosmic inventions');
        console.log('   🔄 Handle subscriptions for monthly space boxes');
        console.log('   💰 Process invoices for interstellar orders');
        console.log('   📊 List products, customers, and pricing');
        console.log('');
        console.log('💬 Just tell me what you\'d like to do in plain English!');
        console.log('🆘 Type "help" for examples, or "quit" to exit');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('');
    }
    displayHelp() {
        console.log('\n🆘 Galileo\'s Gizmos - Help & Examples');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('');
        console.log('💡 Here are some things you can try:');
        console.log('');
        console.log('📦 PRODUCT MANAGEMENT:');
        console.log('   • "Create a product called Mars Rock Collection for $89.99"');
        console.log('   • "Show me all our space products"');
        console.log('   • "List our current product catalog"');
        console.log('');
        console.log('💳 PAYMENT LINKS:');
        console.log('   • "Create a payment link for the Astronaut Training Kit at $299"');
        console.log('   • "I need a checkout link for our Zero Gravity Simulator"');
        console.log('');
        console.log('👥 CUSTOMER MANAGEMENT:');
        console.log('   • "Add customer Jane Spacewalker with email jane@cosmos.com"');
        console.log('   • "Show me our customer list"');
        console.log('   • "Find customer with email buzz@moonbase.com"');
        console.log('');
        console.log('🔄 SUBSCRIPTIONS:');
        console.log('   • "Set up a monthly Cosmic Discovery Box for $49.99/month"');
        console.log('   • "Create a subscription service for Space Snacks"');
        console.log('');
        console.log('💰 INVOICING:');
        console.log('   • "Create an invoice for customer cus_123456"');
        console.log('   • "Send a 30-day invoice to our Mars expedition client"');
        console.log('');
        console.log('🔧 COMMANDS:');
        console.log('   • "help" - Show this help menu');
        console.log('   • "quit" or "exit" - End the session');
        console.log('   • "clear" - Clear the conversation history');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('');
    }
    async handleSpecialCommands(input) {
        const command = input.toLowerCase().trim();
        switch (command) {
            case 'help':
                this.displayHelp();
                return true;
            case 'quit':
            case 'exit':
                console.log('\n🌟 Thank you for visiting Galileo\'s Gizmos!');
                console.log('🚀 Your session data has been logged to Galileo for analysis.');
                console.log('🛸 Safe travels through the cosmos! ✨');
                await this.concludeSession();
                process.exit(0);
                return true;
            case 'clear':
                console.clear();
                this.displayWelcome();
                console.log('🔄 Conversation history cleared. Starting fresh!');
                return true;
            case '':
                return true; // Just ignore empty input
            default:
                return false; // Not a special command
        }
    }
    async startSession() {
        try {
            this.sessionId = await this.galileoLogger.startSession('Galileo Gizmos Customer Service Session');
            console.log(`📊 Started Galileo session: ${this.sessionId}`);
            console.log(`📈 Project: ${environment_1.env.galileo.projectName} | Stream: ${environment_1.env.galileo.logStream}`);
        }
        catch (error) {
            console.log('⚠️  Warning: Could not start Galileo session, but continuing...');
        }
    }
    async concludeSession() {
        if (this.sessionId) {
            try {
                const conversationHistory = this.agent.getConversationHistory();
                await this.galileoLogger.logConversation(conversationHistory);
                await this.galileoLogger.concludeSession();
                console.log('📊 Session data successfully logged to Galileo dashboard');
            }
            catch (error) {
                console.log('⚠️  Warning: Could not conclude Galileo session');
            }
        }
    }
    async processUserInput(input) {
        try {
            console.log('🤖 Gizmo: Processing your request...');
            const startTime = Date.now();
            const response = await this.agent.processMessage(input);
            const endTime = Date.now();
            if (response.success) {
                console.log(`🌟 Gizmo: ${response.message}`);
                if (response.data) {
                    console.log(`⏱️  Processing time: ${endTime - startTime}ms`);
                    if (response.data.toolsUsed && response.data.toolsUsed.length > 0) {
                        console.log(`🔧 Stripe operations: ${response.data.toolsUsed.join(', ')}`);
                    }
                }
            }
            else {
                console.log(`❌ Gizmo: I apologize, but I encountered an issue: ${response.message}`);
                if (response.error) {
                    console.log(`🔧 Technical details: ${response.error}`);
                }
            }
        }
        catch (error) {
            console.log(`💥 Gizmo: Oops! Something unexpected happened. Let me try to help you another way.`);
            console.log(`🔧 Error details: ${error}`);
        }
    }
    async start() {
        console.log('🚀 Initializing Galileo\'s Gizmos Customer Service...');
        console.log(`📊 Connecting to Galileo monitoring...`);
        // Start Galileo session
        await this.startSession();
        // Display welcome message
        this.displayWelcome();
        // Handle graceful shutdown
        this.rl.on('SIGINT', async () => {
            console.log('\n\n🌟 Goodbye! Thanks for visiting Galileo\'s Gizmos!');
            await this.concludeSession();
            process.exit(0);
        });
        // Main conversation loop
        this.rl.prompt();
        this.rl.on('line', async (input) => {
            const trimmedInput = input.trim();
            // Handle special commands
            const isSpecialCommand = await this.handleSpecialCommands(trimmedInput);
            if (isSpecialCommand) {
                this.rl.prompt();
                return;
            }
            // Process normal user input
            if (trimmedInput) {
                await this.processUserInput(trimmedInput);
            }
            console.log(''); // Add some spacing
            this.rl.prompt();
        });
        this.rl.on('close', async () => {
            console.log('\n🌟 Session ended. Safe travels! ✨');
            await this.concludeSession();
            process.exit(0);
        });
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
// Start the interactive customer service
async function main() {
    const customerService = new GalileoGizmosCustomerService();
    await customerService.start();
}
// Run the interactive version
if (require.main === module) {
    main().catch(error => {
        console.error('💥 Fatal error:', error);
        process.exit(1);
    });
}
//# sourceMappingURL=interactive.js.map