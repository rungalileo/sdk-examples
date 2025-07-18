import { StripeAgentToolkit } from '@stripe/agent-toolkit/langchain';
import { ChatOpenAI } from '@langchain/openai';
import { AgentExecutor, createStructuredChatAgent } from 'langchain/agents';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { pull } from 'langchain/hub';
import { DynamicTool } from '@langchain/core/tools';
import { z } from 'zod';
import Stripe from 'stripe';
import { env } from '../config/environment';
import { GalileoAgentLogger } from '../utils/GalileoLogger';
import { CircularToolError } from '../errors/CircularToolError';
import { 
  AgentMessage, 
  AgentResponse, 
  PaymentRequest, 
  PaymentLinkRequest, 
  CustomerRequest,
  AgentMetrics 
} from '../types';

export class StripeAgent {
  private stripeToolkit!: StripeAgentToolkit;
  private llm!: ChatOpenAI;
  private agentExecutor!: AgentExecutor;
  private conversationHistory: AgentMessage[] = [];
  private galileoLogger: GalileoAgentLogger;
  private sessionId: string | null = null;
  private sessionActive: boolean = false;

  constructor() {
    this.galileoLogger = new GalileoAgentLogger();
    this.initializeStripeToolkit();
    this.initializeLLM();
  }

  async init() {
    await this.initializeAgent();
  }

  private initializeStripeToolkit(): void {
    this.stripeToolkit = new StripeAgentToolkit({
      secretKey: env.stripe.secretKey,
      configuration: {
        actions: {
          paymentLinks: {
            create: true,
          },
          customers: {
            create: true,
            read: true,
          },
          products: {
            create: true,
            read: true,
          },
          prices: {
            create: true,
            read: true,
          },
          invoices: {
            create: true,
            update: true,
          }, 
        },
      },
    });
  }

  private initializeLLM(): void {
    this.llm = new ChatOpenAI({
      openAIApiKey: env.openai.apiKey,
      modelName: 'gpt-4o-mini',
      temperature: 0.1,
      maxRetries: 3,
      timeout: 30000, // 30 second timeout
    });
  }





  private async initializeAgent(): Promise<void> {
    // Initialize Stripe client for the atomic tool
    const stripe = new Stripe(env.stripe.secretKey, {
      apiVersion: '2025-02-24.acacia',
    });
    
    // Create atomic helper tool for getting price and creating payment link
    const getPriceAndCreateLink = new DynamicTool({
      name: 'get_price_and_create_payment_link',
      description: 'Provide product name and quantity; returns ready-to-share Stripe payment link URL',
      func: async (input: string) => {
        const params = JSON.parse(input);
        const { product_name, quantity } = params;
        const products = await stripe.products.list({limit: 100});
        const product = products.data.find(p => p.name.toLowerCase() === product_name.toLowerCase());
        if (!product) throw new Error('Product not found');
        const prices = await stripe.prices.list({product: product.id, active: true});
        if (!prices.data.length) throw new Error('No active price');
        const link = await stripe.paymentLinks.create({line_items:[{price: prices.data[0].id, quantity}]});
        return link.url;
      },
    });
    
    const stripeTools = this.stripeToolkit.getTools();
    const tools = [getPriceAndCreateLink, ...stripeTools];
    
    // Use the pre-built structured chat agent prompt from LangChain Hub
    const prompt = await pull('hwchase17/structured-chat-agent') as any;
    
    // Add custom instructions for better tool usage
    const customInstructions = `
CRITICAL: ONLY OFFER REAL PRODUCTS FROM STRIPE INVENTORY

INVENTORY RULES:
- ALWAYS use list_products to check actual inventory before suggesting products
- NEVER suggest fictional, made-up, or non-existent products
- ONLY offer products that actually exist in your Stripe account
- If a user asks for something not in inventory, check list_products first, then explain what's actually available

SESSION CONCLUSION RULES:
- When customer indicates they are done (says "thanks", "nope", "that's all", etc.), conclude the conversation politely
- Do NOT continue asking "Is there anything else I can help you with?" after customer indicates they're done
- Session should end naturally when customer signals completion

STRIPE WORKFLOW FOR PAYMENT LINKS:
When user is ready to purchase, call 'get_price_and_create_payment_link' instead of manually chaining list_products + list_prices + create_payment_link.

The get_price_and_create_payment_link tool is atomic and handles:
1. Finding the product by name
2. Getting the active price for that product
3. Creating the payment link with the specified quantity
4. Returning the ready-to-share URL

For product inquiries:
- ALWAYS use list_products to show what's actually available
- NEVER suggest products that don't exist in your inventory
- When user wants to buy, use get_price_and_create_payment_link directly

For complex calculations (like "how many X can I buy for $Y"):
1. Get product info with list_products
2. Get price info with list_prices
3. Calculate quantity (divide budget by unit price)
4. Use get_price_and_create_payment_link with calculated quantity

Example flow:
1. "What do you offer?" → list_products (shows REAL inventory)
2. "I want the telescope" → get_price_and_create_payment_link with product_name and quantity

REMEMBER: Customer trust depends on only offering real products that exist!
`;

    // Prepend custom instructions to the original prompt
    if (prompt.template) {
      prompt.template = customInstructions + '\n\n' + prompt.template;
    }

    // @ts-ignore
    const agent = await createStructuredChatAgent({
      llm: this.llm,
      tools,
      prompt,
    });

    this.agentExecutor = new AgentExecutor({
      agent,
      tools,
      verbose: true,
      maxIterations: 4, // Lowered to prevent runaway loops
      returnIntermediateSteps: true, // This helps with error handling
    });
  }

  async processMessage(userMessage: string): Promise<AgentResponse> {
    if (!this.agentExecutor) {
      throw new Error('Agent is not initialized. Did you forget to call await agent.init()?');
    }
    const startTime = Date.now();
    
    try {
      // Start Galileo session if not already active
      if (!this.sessionActive) {
        this.sessionId = await this.startGalileoSession("Galileo's Gizmos Customer Session");
        this.sessionActive = true;
      }
      
      // Ensure session consistency throughout the conversation
      console.log(`📝 Processing message in session: ${this.sessionId}`);

      // Add user message to conversation history
      this.conversationHistory.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      });

      // Build conversation context for better memory
      const conversationContext = this.buildConversationContext();

      // Process the message with the agent including conversation history
      const result = await this.agentExecutor.invoke({
        input: userMessage,
        chat_history: conversationContext,
      }, {
        timeout: 20000, // 20 seconds timeout
      });
      
      // Check for circular tool usage after execution
      this.detectCircularToolUsage(result.intermediateSteps);
      
      // Add temporary console.trace after every intermediate step for debugging
      if (result.intermediateSteps && result.intermediateSteps.length > 0) {
        console.log('🔍 INTERMEDIATE STEPS DEBUGGING:');
        result.intermediateSteps.forEach((step: any, index: number) => {
          console.log(`\n--- Step ${index + 1} ---`);
          console.log('Action:', step.action);
          console.log('Observation:', step.observation);
          console.trace(`🚨 Step ${index + 1} stack trace:`);
        });
      }

      // Clean up and format the response
      const cleanOutput = this.cleanAndFormatResponse(result.output, result, userMessage);

      // Add assistant response to conversation history
      this.conversationHistory.push({
        role: 'assistant',
        content: cleanOutput,
        timestamp: new Date(),
      });

      const executionTime = Date.now() - startTime;
      
      // Log to Galileo as a trace in the ongoing session
      await this.logTraceToGalileo({
        executionTime,
        success: true,
        toolsUsed: this.extractToolsUsed(result),
      }, userMessage, cleanOutput);

      return {
        success: true,
        message: cleanOutput,
        data: {
          executionTime,
          toolsUsed: this.extractToolsUsed(result),
          sessionId: this.sessionId,
        },
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // Handle circular tool error with a graceful message
      if (error instanceof CircularToolError) {
        console.error('🔄 CircularToolError caught:', error.message);
        
        await this.logTraceToGalileo({
          executionTime,
          success: false,
          toolsUsed: [],
          errorType: 'CircularToolError',
        }, userMessage, error.message);
        
        return {
          success: false,
          message: 'I seem to be stuck in a loop trying to process your request. Let me try a different approach. Could you please rephrase your question or try asking for something else?',
          error: error.message,
          data: {
            sessionId: this.sessionId,
            toolPattern: error.toolPattern,
          },
        };
      }
      
      // Log error trace to Galileo
      await this.logTraceToGalileo({
        executionTime,
        success: false,
        toolsUsed: [],
        errorType: error instanceof Error ? error.constructor.name : 'UnknownError',
      }, userMessage, errorMessage);

      return {
        success: false,
        message: 'I encountered an error while processing your request. Please try again.',
        error: errorMessage,
        data: {
          sessionId: this.sessionId,
        },
      };
    }
  }

  private buildConversationContext(): string {
    if (this.conversationHistory.length === 0) return '';
    
    // Build context from recent conversation history (last 6 messages)
    const recentHistory = this.conversationHistory.slice(-6);
    return recentHistory
      .map(msg => `${msg.role === 'user' ? 'Human' : 'Assistant'}: ${msg.content}`)
      .join('\n');
  }

  private cleanAndFormatResponse(output: string, result: any, userInput?: string): string {
    let paymentLinkUrl: string | null = null;
    let usedAtomicTool = false;
    
    if (result.intermediateSteps) {
      for (const step of result.intermediateSteps) {
        // Check for payment link creation from traditional tool
        if (step.action && step.action.tool === 'create_payment_link' && step.observation) {
          try {
            const observation = JSON.parse(step.observation);
            if (observation.url) {
              paymentLinkUrl = observation.url;
            }
          } catch (e) {
            const urlMatch = step.observation.match(/https:\/\/buy\.stripe\.com\/[^\s"]+/);
            if (urlMatch) {
              paymentLinkUrl = urlMatch[0];
            }
          }
        }
        
        // Check for payment link creation from atomic helper tool
        if (step.action && step.action.tool === 'get_price_and_create_payment_link' && step.observation) {
          usedAtomicTool = true;
          // The atomic tool returns the URL directly as a string
          const observation = step.observation.trim();
          if (observation.startsWith('https://buy.stripe.com/')) {
            paymentLinkUrl = observation;
          } else {
            // Fallback: try to extract URL from the observation
            const urlMatch = observation.match(/https:\/\/buy\.stripe\.com\/[^\s"]+/);
            if (urlMatch) {
              paymentLinkUrl = urlMatch[0];
            }
          }
        }

        // Clean up product listing responses to remove duplicates
        if (step.action && step.action.tool === 'list_products' && step.observation) {
          try {
            const products = JSON.parse(step.observation);
            if (Array.isArray(products)) {
              const deduplicated = this.deduplicateProducts(products);
              // Store the cleaned products for better response formatting
              (step as any).cleanedProducts = deduplicated;
            }
          } catch (e) {
            // Ignore parsing errors
          }
        }
      }
    }

    // Clean up the output and format properly
    let cleanOutput = output.trim();
    
    // Check if user indicates they're done - conclude session naturally
    if (userInput && this.shouldPromptForFeedback(userInput)) {
      console.log("🏁 User indicated they're done - concluding session naturally");
      
      // Log neutral satisfaction and conclude session
      this.galileoLogger.logSatisfaction(true);
      this.galileoLogger.flushAllTraces();
      
      if (this.sessionActive) {
        this.concludeGalileoSession();
      }
      
      return "🌟 Thank you for choosing Galileo's Gizmos! We're glad we could help you today.\n\n🚀 Your session is now complete!";
    }
    
    // If we found a payment link, enhance the response
    if (paymentLinkUrl) {
      // Check if the assistant's output already contains a properly formatted response
      const alreadyFormattedResponse = cleanOutput.includes('✅') && cleanOutput.includes('Perfect!');
      
      if (!alreadyFormattedResponse) {
        // Force-inject the perfect boilerplate to prevent raw JSON from being shown
        cleanOutput = `✅ **Perfect! I've created your payment link.**

🔗 **Click here to complete your purchase:**
${paymentLinkUrl}

💫 Once you complete your payment, you're all set!`;
        // Suppress follow-up question if the atomic tool was used
        if (!usedAtomicTool) {
          cleanOutput += '\n\nIs there anything else I can help you with today?';
        }
      }
    } else {
      // For other responses, ensure proper formatting
      cleanOutput = cleanOutput
        .replace(/\n\n+/g, '\n\n') // Normalize line breaks
        .replace(/^\s+|\s+$/g, ''); // Trim whitespace
      
      // Check if user input indicates purchase intent
      if (userInput && this.detectPurchaseIntent(userInput)) {
        cleanOutput += '\n\n🛒 **Ready to make a purchase?** I can help you create a payment link! Let me first check what products are actually available in our inventory and then I can create a payment link for you.';
      }
      
      // Add standard follow-up if no special conditions
      if (!cleanOutput.includes('?') && !cleanOutput.toLowerCase().includes('help')) {
        cleanOutput += '\n\nIs there anything else I can help you with?';
      }
    }

    return cleanOutput;
  }

  private extractToolsUsed(result: any): string[] {
    const toolsUsed: string[] = [];
    if (result.intermediateSteps) {
      for (const step of result.intermediateSteps) {
        if (step.action && step.action.tool) {
          toolsUsed.push(step.action.tool);
        }
      }
    }
    return toolsUsed;
  }

  private async logTraceToGalileo(metrics: AgentMetrics, input?: string, output?: string): Promise<void> {
    if (input && output) {
      // Generate a descriptive trace name based on the input
      const traceName = this.generateTraceName(input);
      await this.galileoLogger.logAgentExecution(metrics, input, output, traceName);
    }
  }

  private deduplicateProducts(products: any[]): any[] {
    const seen = new Set<string>();
    const deduplicated: any[] = [];
    
    // Keep the most recent version of each product name
    const sortedProducts = products.sort((a, b) => b.created - a.created);
    
    for (const product of sortedProducts) {
      if (!seen.has(product.name)) {
        seen.add(product.name);
        deduplicated.push(product);
      }
    }
    
    return deduplicated;
  }

  private generateTraceName(input: string): string {
    // Generate space-themed trace names for Galileo's Gizmos
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes('payment link')) {
      return "🚀 Galileo's Gizmos - Launch Payment Portal";
    } else if (lowerInput.includes('customer') && lowerInput.includes('create')) {
      return "👨‍🚀 Galileo's Gizmos - Register Space Explorer";
    } else if (lowerInput.includes('products') && (lowerInput.includes('list') || lowerInput.includes('show'))) {
      return "🌌 Galileo's Gizmos - Browse Cosmic Catalog";
    } else if (lowerInput.includes('subscription') && lowerInput.includes('create')) {
      return "📦 Galileo's Gizmos - Setup Stellar Subscription";
    } else if (lowerInput.includes('create') && lowerInput.includes('product')) {
      return "⭐ Galileo's Gizmos - Add New Space Gadget";
    } else if (lowerInput.includes('create') && lowerInput.includes('price')) {
      return "💫 Galileo's Gizmos - Set Cosmic Pricing";
    } else {
      return "🛸 Galileo's Gizmos - Customer Support";
    }
  }

  private detectPurchaseIntent(input: string): boolean {
    const lowerInput = input.toLowerCase();
    const purchaseKeywords = [
      'buy', 'purchase', 'order', 'payment', 'pay', 'checkout',
      'want to buy', 'would like to buy', 'interested in buying',
      'ready to purchase', 'ready to buy', 'i want', 'i need',
      'add to cart', 'get this', 'take this'
    ];
    
    return purchaseKeywords.some(keyword => lowerInput.includes(keyword));
  }

  private shouldPromptForFeedback(input: string): boolean {
    const lowerInput = input.toLowerCase().trim();
    
    // More specific closing patterns that indicate conversation is ending
    const strongClosingPatterns = [
      'thank you', 'thanks', 'that\'s all', 'that\'s it', 'all set',
      'i\'m done', 'i\'m all set', 'goodbye', 'bye', 'see you later',
      'talk to you later', 'have a good day', 'have a great day'
    ];
    
    // Simple closing words that need to be at the end or standalone
    const simpleClosingWords = ['done', 'finished', 'perfect', 'great', 'awesome'];
    
    // ONLY these specific dismissive responses should trigger feedback
    const dismissiveResponses = ['nope', 'nope!', 'no', 'nah'];
    
    // Check for strong closing patterns anywhere in the input
    const hasStrongClosing = strongClosingPatterns.some(pattern => lowerInput.includes(pattern));
    
    // Check for dismissive responses (exact matches ONLY)
    const isDismissive = dismissiveResponses.some(response => lowerInput === response);
    
    // Check for simple closing words only if they're at the end or standalone
    const hasSimpleClosingAtEnd = simpleClosingWords.some(word => {
      const words = lowerInput.split(/\s+/);
      const lastWords = words.slice(-2).join(' '); // Last two words
      return lastWords === word || lastWords.endsWith(` ${word}`) || words.length === 1 && words[0] === word;
    });
    
    // Do NOT trigger feedback for longer negative responses
    const isLongNegativeResponse = lowerInput.length > 20 && (lowerInput.includes('cannot') || lowerInput.includes('help me'));
    
      return (hasStrongClosing || isDismissive || hasSimpleClosingAtEnd) && !isLongNegativeResponse;
  }

  /**
   * Detects circular tool usage patterns in intermediate steps
   * Keeps a sliding window of the last 3 tool calls and checks for repeated patterns
   */
  private detectCircularToolUsage(intermediateSteps: any[]): void {
    if (!intermediateSteps || intermediateSteps.length < 4) {
      return; // Need at least 4 steps to detect a 2-tool cycle repeated twice
    }

    // Extract tool names from the last 4 steps
    const recentTools = intermediateSteps
      .slice(-4)
      .map(step => step.action?.tool)
      .filter(tool => tool); // Filter out undefined/null

    if (recentTools.length < 4) {
      return;
    }

    // Check if we have a two-tool pattern that repeats
    const [tool1, tool2, tool3, tool4] = recentTools;
    
    if (tool1 === tool3 && tool2 === tool4 && tool1 !== tool2) {
      const pattern = [tool1, tool2];
      const errorMessage = `Circular tool invocation detected: ${pattern.join(' -> ')} pattern repeated twice. This suggests the agent is stuck in a loop.`;
      
      console.error('🔄 Circular tool usage detected:', {
        pattern,
        recentTools,
        totalSteps: intermediateSteps.length
      });
      
      throw new CircularToolError(errorMessage, pattern);
    }
  }

  // Convenience methods for common operations
  async createPaymentLink(request: PaymentLinkRequest): Promise<AgentResponse> {
    const message = `Create a payment link for "${request.productName}" with amount ${request.amount} ${request.currency.toUpperCase()}`;
    return this.processMessage(message);
  }

  async createCustomer(request: CustomerRequest): Promise<AgentResponse> {
    const message = `Create a new customer with email ${request.email}${request.name ? ` and name ${request.name}` : ''}`;
    return this.processMessage(message);
  }

  getConversationHistory(): AgentMessage[] {
    return [...this.conversationHistory];
  }

  clearConversationHistory(): void {
    this.conversationHistory = [];
  }

  async startGalileoSession(sessionName: string): Promise<string> {
    const sessionId = await this.galileoLogger.startSession(sessionName);
    this.sessionActive = true;
    console.log(`🚀 Started Galileo session: ${sessionId}`);
    return sessionId;
  }

  async logConversationToGalileo(): Promise<void> {
    await this.galileoLogger.logConversation(this.conversationHistory);
  }

  async concludeGalileoSession(): Promise<void> {
    if (this.sessionActive) {
      console.log(`🏁 Concluding Galileo session: ${this.sessionId}`);
      await this.galileoLogger.concludeSession();
      this.sessionActive = false;
      this.sessionId = null;
      console.log('✅ Galileo session concluded successfully');
    }
  }

  // Add method to get session status
  getSessionStatus(): { active: boolean; sessionId: string | null } {
    return {
      active: this.sessionActive,
      sessionId: this.sessionId,
    };
  }
}