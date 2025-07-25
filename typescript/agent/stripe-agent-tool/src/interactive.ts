// Reduce LangChain logging verbosity
process.env.LANGCHAIN_TRACING_V2 = 'false';
process.env.LANGCHAIN_LOGGING = 'error';
process.env.LANGCHAIN_VERBOSE = 'false';
process.env.LANGCHAIN_CALLBACKS = 'false';

import { StripeAgent } from './agents/StripeAgent';
import { GalileoAgentLogger } from './utils/GalileoLogger';
import { env } from './config/environment';
import * as readline from 'readline';

class GalileoGizmosCustomerService {
  private agent: StripeAgent;
  private galileoLogger: GalileoAgentLogger;
  private rl: readline.Interface;
  private sessionId: string | null = null;

  constructor() {
    this.agent = new StripeAgent();
    this.galileoLogger = new GalileoAgentLogger();
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
    console.log('   • "Show me all our space products"');
    console.log('   • "Create a payment link for the Astronaut Training Kit at $299"');
    console.log('   • "Add customer Jane Spacewalker with email jane@cosmos.com"');
    console.log('   • "help" - Show this menu | "quit" - Exit | "clear" - Clear history');
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
      this.sessionId = await this.galileoLogger.startSession('Galileo Gizmos Customer Service Session');
    } catch (error) {
      // Silent fail - continue without Galileo session
    }
  }

  private async concludeSession() {
    if (this.sessionId) {
      try {
        const conversationHistory = this.agent.getConversationHistory();
        await this.galileoLogger.logConversation(conversationHistory);
        await this.galileoLogger.concludeSession();
      } catch (error) {
        // Silent fail
      }
    }
  }

  private async processUserInput(input: string) {
    try {
      const response = await this.agent.processMessage(input);
      
      if (response.success) {
        console.log(`🤖 Gizmo: ${response.message}`);
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
