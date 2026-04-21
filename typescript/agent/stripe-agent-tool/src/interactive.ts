import { StripeAgent } from './agents/StripeAgent';
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
    console.log('   • "!end" - **Developer command**: Force flush Galileo traces');
    console.log('\n🚀 Agent Features:');
    console.log('   • Loop Prevention - Prevents infinite tool calls');
    console.log('   • Memory Cache - 5-minute product/price caching');
    console.log('   • Context Awareness - Remembers recent conversation');
    console.log('   • Buffered Logging - Efficient Galileo trace collection');
    console.log('   • Auto-Flush - Traces are automatically flushed after each interaction');
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
      
      case '!end':
        // Developer command: Force flush all buffered Galileo traces
        try {
          await this.agent.endConversation();
          this.agent.restartConversation();
          console.log('📊 Manual flush completed - traces sent to Galileo');
        } catch (error) {
          console.error('Error during manual flush:', error);
        }
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
      // Session will be started automatically when the first message is processed
      // console.log('🚀 Session ready - Galileo tracing will be activated on first message');
    } catch (error) {
      console.error('Error preparing session:', error);
    }
  }

  private async concludeSession() {
    if (this.sessionId) {
      try {
        // Final flush of any remaining traces
        await this.agent.endConversation();
        // console.log('📊 Session concluded and final traces flushed to Galileo');
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
    } finally {
      // Galileo traces are automatically flushed by the agent
      // No need to manually end/restart conversation after every input
      // This prevents the flush messages from appearing
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
