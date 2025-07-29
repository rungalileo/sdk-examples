// Enable LangChain callbacks for Galileo integration
process.env.LANGCHAIN_LOGGING = 'info';
process.env.LANGCHAIN_VERBOSE = 'false';
process.env.LANGCHAIN_CALLBACKS = 'true';

import { StripeAgent } from './agents/StripeAgent';
import { env } from './config/environment';
import * as readline from 'readline';

class GalileoGizmosCustomerService {
  private agent: StripeAgent;
  private rl: readline.Interface;
  private sessionId: string | null = null;

  constructor() {
    this.agent = new StripeAgent();
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '🚀 You: '
    });
  }

  private displayWelcome() {
    console.log('\n🛸 Hello! I\'m Gizmo, your AI-powered space commerce assistant!');
    console.log('💬 Just tell me what you\'d like to do in plain English!');
    console.log('🆘 Type "help" for examples, or "quit" to exit');
    console.log('');
  }

  private displayHelp() {
    console.log('\n💡 Examples:');
    console.log('   • "What do you have for sale?" - Browse our cosmic catalog');
    console.log('   • "I want to buy Space Ice Cream" - Purchase with payment link');
    console.log('   • "How much is the telescope?" - Get current pricing');
    console.log('   • "Create a payment link for the Astronaut Training Kit at $299"');
    console.log('   • "Add customer Jane Spacewalker with email jane@cosmos.com"');
    console.log('\n🔧 Commands:');
    console.log('   • "help" - Show this menu');
    console.log('   • "quit" - Exit gracefully');
    console.log('   • "clear" - Clear screen');
    console.log('\n🚀 Agent Features:');
    console.log('   • Loop Prevention - Prevents infinite tool calls');
    console.log('   • Memory Cache - 5-minute product/price caching');
    console.log('   • Context Awareness - Remembers recent conversation');
    console.log('   • Buffered Logging - Efficient Galileo trace collection');
  }

  private async handleSpecialCommands(input: string): Promise<boolean> {
    const command = input.toLowerCase().trim();
    
    switch (command) {
      case 'help':
        this.displayHelp();
        return true;
      
      case 'quit':
      case 'exit':
        await this.concludeSession();
        process.exit(0);
        return true;
      
      case 'clear':
        console.clear();
        return true;
      
      
      case '':
        return true; // Just ignore empty input
      
      default:
        return false; // Not a special command
    }
  }

  private async startSession() {
    try {
      this.sessionId = `session-${Date.now()}`;
      // The session will be started automatically when the first message is processed
      console.log('🚀 Session ready - Galileo logging will start with first message');
    } catch (error) {
      console.error('Error starting session:', error);
    }
  }

  private async concludeSession() {
    if (this.sessionId) {
      try {
        // End the conversation and flush traces
        await this.agent.endConversation();
        console.log('📊 Session concluded and buffered traces flushed');
      } catch (error) {
        console.error('Error concluding session:', error);
      }
    }
  }

  private async processUserInput(input: string) {
    try {
      const response = await this.agent.processMessage(input);
      
      if (response.success) {
        console.log(`🤖 Gizmo: ${response.message}`);
        
        // Check if conversation has ended and handle gracefully
        if (this.agent.isConversationEnded()) {
          console.log('\n📊 Conversation concluded. Type a new message to start fresh, or "quit" to exit.');
          // Reset the conversation state for potential new interaction
          this.agent.restartConversation();
        }
      } else {
        console.log(`❌ Error: ${response.message}`);
      }
    } catch (error) {
      console.log(`💥 Unexpected error: ${error}`);
    }
  }

  public async start() {
    // Initialize the agent
    await this.agent.init();
    
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
    
    this.rl.on('line', async (input: string) => {
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
