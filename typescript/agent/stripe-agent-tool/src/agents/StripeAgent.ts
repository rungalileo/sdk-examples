/**
 * STRIPE AGENT WITH GALILEO TRACING
 * 
 * This is a complete example of building an AI agent that can interact with Stripe (payment processing)
 * while using Galileo for observability and tracing. Here's what this agent does:
 * 
 * 🤖 AGENT CAPABILITIES:
 * - Lists Stripe products and prices
 * - Creates payment links for customers
 * - Manages customer data
 * - Handles conversations with memory
 * 
 * 📊 GALILEO INTEGRATION:
 * - Tracks all agent conversations and tool usage
 * - Provides debugging and performance metrics
 * - Logs errors and execution times
 * - Enables session-based tracing
 * 
 * 🛠️ TECHNICAL STACK:
 * - LangChain: AI agent framework
 * - OpenAI GPT-4: Language model
 * - Stripe: Payment processing
 * - Galileo: AI observability platform
 */

// Enable LangChain callbacks for Galileo integration
// These environment variables tell LangChain to send tracing data to Galileo
process.env.LANGCHAIN_LOGGING = 'info';     // Log informational messages
process.env.LANGCHAIN_VERBOSE = 'false';    // Don't show verbose debug output
process.env.LANGCHAIN_CALLBACKS = 'true';   // Enable callback handlers (like Galileo)

import { StripeAgentToolkit } from '@stripe/agent-toolkit/langchain';
import { ChatOpenAI } from '@langchain/openai';
import { AgentExecutor, createStructuredChatAgent } from 'langchain/agents';
import { ChatPromptTemplate } from '@langchain/core/prompts';
import { pull } from 'langchain/hub';
import { DynamicTool } from '@langchain/core/tools';
import { z } from 'zod';
import Stripe from 'stripe';
import { env } from '../config/environment';
import { GalileoCallbackHandler } from '../callbacks/handlers/GalileoCallbackHandler';
import { CircularToolError } from '../errors/CircularToolError';
import { 
  AgentMessage, 
  AgentResponse, 
  PaymentRequest, 
  PaymentLinkRequest, 
  CustomerRequest,
  AgentMetrics 
} from '../types';

/**
 * STRIPE AGENT CLASS
 * 
 * This class represents a complete AI agent that can:
 * 1. Process natural language requests about Stripe operations
 * 2. Use Stripe tools to interact with the Stripe API
 * 3. Track all interactions through Galileo for observability
 * 4. Maintain conversation memory and context
 * 
 * For first-time agent builders, here's what each component does:
 */
export class StripeAgent {
  // 🔧 CORE AGENT COMPONENTS
  private stripeToolkit!: StripeAgentToolkit;    // Provides Stripe API tools (list products, create payments, etc.)
  private llm!: ChatOpenAI;                      // The AI language model (GPT-4) that powers conversations
  private agentExecutor!: AgentExecutor;         // LangChain's agent executor that coordinates tool usage
  
  // 💬 CONVERSATION MANAGEMENT
  private conversationHistory: AgentMessage[] = [];  // Stores all messages in the current session
  private sessionId: string | null = null;            // Unique identifier for the current conversation
  private sessionActive: boolean = false;             // Whether we're currently tracking a session
  private conversationEnded: boolean = false;         // Flag to indicate if user has ended the conversation
  
  // 📊 GALILEO OBSERVABILITY
  private galileoCallbackHandler: GalileoCallbackHandler;  // Handles all Galileo tracking and logging
  
  // ⚡ PERFORMANCE OPTIMIZATION (CACHING)
  private cachedProducts: any[] = [];                      // Cache Stripe products to avoid repeated API calls
  private cachedPrices: any[] = [];                        // Cache pricing data
  private cacheTimestamp: number = 0;                      // When the cache was last updated
  private readonly CACHE_DURATION = 5 * 60 * 1000;        // Cache expires after 5 minutes

  /**
   * CONSTRUCTOR - Sets up the agent's core components
   * 
   * For Galileo users: The callback handler is initialized here and will automatically
   * start tracking your agent's behavior once you begin processing messages.
   */
  constructor() {
    this.galileoCallbackHandler = new GalileoCallbackHandler();
    this.initializeStripeToolkit();
    this.initializeLLM();
  }

  /**
   * INITIALIZATION - Must be called before using the agent
   * 
   * This is separate from the constructor because agent initialization
   * involves async operations (loading prompts from LangChain Hub).
   */
  async init() {
    await this.initializeAgent();
  }

  /**
   * 🔧 STRIPE TOOLKIT INITIALIZATION
   * 
   * This creates a toolkit that provides pre-built tools for interacting with Stripe.
   * Each tool corresponds to a Stripe API operation that the agent can use.
   * 
   * For first-time builders: Think of tools as "superpowers" your agent can use.
   * Instead of the agent having to write code to call Stripe APIs, these tools
   * handle all the API complexity and just need simple parameters.
   * 
   * Available tools this creates:
   * - list_products: Get products from your Stripe catalog
   * - create_product: Add new products to Stripe
   * - list_prices: Get pricing for products
   * - create_price: Set up new pricing
   * - create_payment_link: Generate checkout links
   * - create_customer: Add customers to Stripe
   * - list_customers: View customer data
   * - create_invoice: Generate invoices
   * - update_invoice: Modify existing invoices
   */
  private initializeStripeToolkit(): void {
    this.stripeToolkit = new StripeAgentToolkit({
      secretKey: env.stripe.secretKey,  // Your Stripe secret key from environment variables
      configuration: {
        actions: {  // Enable specific Stripe operations for security
          paymentLinks: {
            create: true,  // Allow creating payment links (checkout URLs)
          },
          customers: {
            create: true,  // Allow creating new customers
            read: true,    // Allow reading customer data
          },
          products: {
            create: true,  // Allow adding new products
            read: true,    // Allow listing/viewing products
          },
          prices: {
            create: true,  // Allow setting up pricing
            read: true,    // Allow viewing price information
          },
          invoices: {
            create: true,  // Allow generating invoices
            update: true,  // Allow modifying invoices
          }, 
        },
      },
    });
  }

  /**
   * 🤖 LANGUAGE MODEL INITIALIZATION
   * 
   * This sets up the AI "brain" that will understand user requests and decide
   * which tools to use. We're using OpenAI's GPT-4o-mini model.
   * 
   * Key settings explained:
   * - temperature: How "creative" the AI is (0.1 = very focused, 1.0 = very creative)
   * - maxRetries: How many times to retry if the API call fails
   * - timeout: Maximum time to wait for a response
   * 
   * For Galileo users: All LLM calls will be automatically tracked, including
   * token usage, latency, and the reasoning process.
   */
  private initializeLLM(): void {
    this.llm = new ChatOpenAI({
      openAIApiKey: env.openai.apiKey,  // Your OpenAI API key
      modelName: 'gpt-4o-mini',         // The specific model to use
      temperature: 0.1,                 // Low temperature for consistent, focused responses
      maxRetries: 3,                    // Retry failed API calls up to 3 times
      timeout: 30000,                   // 30 second timeout for API calls
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
      description: 'Create payment link for specific product. Input format: {"product_name": "exact product name", "quantity": 1}. Use this ONLY when user explicitly wants to purchase a specific product.',
      func: async (input: string) => {
        try {
          const params = JSON.parse(input);
          const { product_name, quantity = 1 } = params;
          
          if (!product_name) {
            return 'Error: Product name is required. Please specify which product the customer wants to purchase.';
          }
          
          // Search for products with fuzzy matching
          const products = await stripe.products.list({limit: 100});
          let product = products.data.find(p => p.name.toLowerCase() === product_name.toLowerCase());
          
          // If exact match not found, try partial matching
          if (!product) {
            product = products.data.find(p => 
              p.name.toLowerCase().includes(product_name.toLowerCase()) ||
              product_name.toLowerCase().includes(p.name.toLowerCase())
            );
          }
          
          if (!product) {
            const availableProducts = products.data.slice(0, 5).map(p => p.name).join(', ');
            return `Product "${product_name}" not found in inventory. Available products include: ${availableProducts}. Please check the product name and try again.`;
          }
          
          const prices = await stripe.prices.list({product: product.id, active: true});
          if (!prices.data.length) {
            return `Product "${product.name}" found but has no active pricing. Please contact support or try a different product.`;
          }
          
          const link = await stripe.paymentLinks.create({
            line_items: [{price: prices.data[0].id, quantity: Math.max(1, quantity)}]
          });
          
          return link.url;
        } catch (error) {
          if (error instanceof SyntaxError) {
            return 'Error: Invalid input format. Please use {"product_name": "product name", "quantity": 1}';
          }
          return `Error creating payment link: ${error instanceof Error ? error.message : 'Unknown error'}`;
        }
      },
    });
    
    const stripeTools = this.stripeToolkit.getTools();
    const tools = [getPriceAndCreateLink, ...stripeTools];
    
    // Use the pre-built structured chat agent prompt from LangChain Hub
    const prompt = await pull('hwchase17/structured-chat-agent') as any;
    
    // Add custom instructions for better tool usage
    const customInstructions = `
CRITICAL: ALWAYS USE STRIPE TOOLS FOR ACCURATE PRICE INFORMATION

MANDATORY TOOL USAGE RULES:
1. **ALWAYS call list_products with limit: 10** when asked about products, inventory, or what's available
2. **ALWAYS call list_prices with limit: 10** to get accurate pricing information
3. **NEVER make up or guess prices** - only use prices from Stripe API calls
4. **NEVER suggest products without checking inventory first**

PRICE ACCURACY REQUIREMENTS:
- Every product price shown must come from a list_prices API call
- Convert Stripe unit_amount (cents) to dollars by dividing by 100
- Format prices as "$XX.XX" (e.g., unit_amount: 4499 becomes "$44.99")
- If a product has no prices, show "Price not set" or "Contact for pricing"

INVENTORY VERIFICATION:
- Use list_products with limit: 10 to get a manageable list of products
- Only offer products that are returned by the list_products API
- If a user asks for something not in inventory, explain what's actually available

PURCHASE WORKFLOW:
1. **User asks about products** → Call list_products (limit: 10) → Call list_prices (limit: 10) → Show products with accurate prices
2. **User wants to buy** → Use get_price_and_create_payment_link (atomic tool)
3. **User asks for pricing** → Call list_products (limit: 10) → Call list_prices (limit: 10) → Show accurate pricing

RESPONSE FORMATTING:
- Keep responses concise and focused
- Show only the most relevant products (limit to 10)
- Format product listings clearly with prices
- If user asks for "all products", explain you're showing a selection and they can ask for specific items

EXAMPLE RESPONSES:
- "What do you have?" → list_products (limit: 10) + list_prices (limit: 10) → "Here are some of our products: [formatted list with real prices]"
- "How much is the telescope?" → list_products + list_prices → "The telescope costs $X.XX (based on current Stripe pricing)"
- "I want to buy the telescope" → get_price_and_create_payment_link → "Here's your payment link: [URL]"

CRITICAL: Always use limit: 10 for both list_products and list_prices to avoid overwhelming responses. Never skip the list_prices call when showing product information.
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
      verbose: env.app.agentVerbose,
      maxIterations: 8, // Increased to handle more interactions
      returnIntermediateSteps: true, // This helps with error handling
      earlyStoppingMethod: 'force', // Stop when agent decides it's complete
    });
  }

  /**
   * 💬 PROCESS MESSAGE - The Heart of the Agent
   * 
   * This is the main method that handles all user interactions. Here's what happens:
   * 
   * 1. 📊 Galileo Session Management - Start tracking if not already active
   * 2. 📝 Memory Management - Add message to conversation history
   * 3. 🤖 AI Processing - Let the agent decide what to do and which tools to use
   * 4. 🔍 Result Processing - Clean up and format the response
   * 5. 📊 Logging - Track everything in Galileo for observability
   * 
   * For first-time builders: This method orchestrates the entire agent workflow.
   * The agent will automatically choose which Stripe tools to use based on the user's request.
   * 
   * For Galileo users: Every step is automatically logged, giving you complete visibility
   * into how your agent makes decisions and performs.
   */
  async processMessage(userMessage: string): Promise<AgentResponse> {
    // ✅ SAFETY CHECK: Make sure the agent is properly initialized
    if (!this.agentExecutor) {
      throw new Error('Agent is not initialized. Did you forget to call await agent.init()?');
    }
    const startTime = Date.now();  // Start timing for performance metrics
    
    try {
      // 📊 GALILEO SESSION MANAGEMENT
      // Start a new session if this is the first message in a conversation
      // This creates a "session" in Galileo that groups related interactions together
      if (!this.sessionActive) {
        this.sessionId = `session-${Date.now()}`;
        await this.galileoCallbackHandler.startSession(this.sessionId);
        this.sessionActive = true;
      }
      
      // 📊 LOG USER MESSAGE TO GALILEO
      // This tracks the user's input so you can see exactly what triggered each agent response
      this.galileoCallbackHandler.updateSessionWithMessage({
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      });

      // 📝 CONVERSATION MEMORY
      // Add the user's message to our internal conversation history
      // This helps the agent remember what was discussed earlier
      this.conversationHistory.push({
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      });

      // 🧠 BUILD CONVERSATION CONTEXT
      // Create a summary of recent conversation history to give the agent context
      // This helps the agent understand follow-up questions and maintain context
      const conversationContext = this.buildConversationContext();

      // 📊 LOG AGENT START TO GALILEO  
      // This marks the beginning of the agent's processing in Galileo
      const runId = `run-${Date.now()}`;
      this.galileoCallbackHandler.logAgentStart(runId, { input: userMessage });

      // 🤖 CORE AGENT PROCESSING - This is where the magic happens!
      // The agent will:
      // 1. Analyze the user's request using the LLM (GPT-4)
      // 2. Decide which tools to use (list_products, create_payment_link, etc.)
      // 3. Execute those tools with the Stripe API
      // 4. Generate a natural language response
      // 
      // The 'callbacks' parameter ensures Galileo tracks every step of this process
      const result = await this.agentExecutor.invoke({
        input: userMessage,        // The user's request
        chat_history: conversationContext,  // Previous conversation for context
      }, {
        timeout: 20000,            // 20 second timeout to prevent hanging
        callbacks: [this.galileoCallbackHandler.getGalileoCallback()],  // Galileo tracking
      });
      
      // 🔍 ERROR DETECTION: Check for circular tool usage
      // Sometimes agents can get stuck in loops - this detects and prevents that
      this.detectCircularToolUsage(result.intermediateSteps);
      
      // 📊 DEBUG MODE: Show detailed step-by-step execution (optional)
      // When verbose mode is enabled, this shows exactly what the agent did internally
      // Useful for debugging and understanding agent behavior
      if (env.app.agentVerbose) {
        if (result.intermediateSteps && result.intermediateSteps.length > 0) {
          console.log('🔍 INTERMEDIATE STEPS DEBUGGING:');
          result.intermediateSteps.forEach((step: any, index: number) => {
            console.log(`\n--- Step ${index + 1} ---`);
            console.log('Action:', step.action);          // What tool was called
            console.log('Observation:', step.observation); // What the tool returned
            console.trace(`🚨 Step ${index + 1} stack trace:`);
          });
        }
      }

      // ✨ RESPONSE FORMATTING
      // Clean up the raw agent output and format it nicely for users
      // This handles special cases like payment links and purchase flows
      const cleanOutput = await this.cleanAndFormatResponse(result.output, result, userMessage);

      // 📊 LOG AGENT END TO GALILEO
      // Mark the successful completion of agent processing
      this.galileoCallbackHandler.logAgentEnd(runId, { output: cleanOutput });

      // 📊 LOG ASSISTANT RESPONSE TO GALILEO
      // Track the final response that gets sent to the user
      this.galileoCallbackHandler.updateSessionWithMessage({
        role: 'assistant',
        content: cleanOutput,
        timestamp: new Date(),
      });

      // 📝 ADD RESPONSE TO CONVERSATION MEMORY
      // Store the assistant's response for future context
      this.conversationHistory.push({
        role: 'assistant',
        content: cleanOutput,
        timestamp: new Date(),
      });

      // ⏱️ PERFORMANCE TRACKING
      const executionTime = Date.now() - startTime;
      
      // 📊 UPDATE GALILEO METRICS
      // Log performance metrics for this successful interaction
      this.galileoCallbackHandler.updateSessionMetrics(executionTime, true);

      // ✅ RETURN SUCCESS RESPONSE
      // Send back the formatted response with metadata
      return {
        success: true,
        message: cleanOutput,
        data: {
          executionTime,                           // How long processing took
          toolsUsed: this.extractToolsUsed(result), // Which Stripe tools were used
          sessionId: this.sessionId,               // Session identifier for tracking
        },
      };
    } catch (error) {
      // ❌ ERROR HANDLING
      // If anything goes wrong, we handle it gracefully and still log to Galileo
      const executionTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      // 📊 LOG ERROR TO GALILEO
      // Track errors so you can debug issues in your agent
      this.galileoCallbackHandler.logError(`error-${Date.now()}`, error instanceof Error ? error : new Error(errorMessage));
      
      // 📊 UPDATE ERROR METRICS
      // Record that this interaction failed
      this.galileoCallbackHandler.updateSessionMetrics(executionTime, false);
      
      // 🔄 SPECIAL HANDLING: Circular Tool Errors
      // If the agent got stuck in a loop, provide a helpful message
      if (error instanceof CircularToolError) {
        console.error('🔄 CircularToolError caught:', error.message);
        
        return {
          success: false,
          message: 'I seem to be stuck in a loop trying to process your request. Let me try a different approach. Could you please rephrase your question or try asking for something else?',
          error: error.message,
          data: {
            sessionId: this.sessionId,
            toolPattern: error.toolPattern,  // Which tools were looping
          },
        };
      }

      // ❌ GENERIC ERROR RESPONSE
      // For any other errors, provide a friendly fallback message
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

  private async cleanAndFormatResponse(output: string, result: any, userInput?: string): Promise<string> {
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
    
    // Check if user indicates they're done - but only set conversationEnded flag
    if (userInput && this.shouldPromptForFeedback(userInput)) {
      this.conversationEnded = true;
      
      if (this.sessionActive) {
        this.sessionActive = false;
        this.sessionId = null;
      }
      
      return "🌟 Thank you for choosing Galileo's Gizmos! We're glad we could help you today.\n\n🚀 Catch you around the galaxy!";
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
        cleanOutput += '\n\n🛒 **I\'d be happy to help you make a purchase!** Let me show you what\'s available in our inventory:';
        
        // Try to get current inventory from recent tool calls
        const recentProducts = this.getRecentProducts(result);
        if (recentProducts && recentProducts.length > 0) {
          cleanOutput += '\n\n**Available Products (showing first 10):**';
          recentProducts.slice(0, 10).forEach((product: any) => {
            if (product.prices && product.prices.length > 0) {
              const price = product.prices[0];
              const priceDisplay = price.unit_amount ? `$${(price.unit_amount / 100).toFixed(2)}` : 'Price not set';
              cleanOutput += `\n• **${product.name}** - ${priceDisplay}`;
              if (product.description) {
                cleanOutput += `\n  ${product.description}`;
              }
            } else {
              cleanOutput += `\n• **${product.name}** - Price not set (no active prices in Stripe)`;
            }
          });
          if (recentProducts.length > 10) {
            cleanOutput += `\n\n*... and ${recentProducts.length - 10} more products available. Ask for specific items!*`;
          }
          cleanOutput += '\n\nJust let me know which product you\'d like to purchase and I\'ll create a payment link for you!';
        } else {
          cleanOutput += '\n\nLet me check our current inventory for you. What type of product are you looking for?';
        }
      }
      
      // Add standard follow-up if no special conditions and conversation hasn't ended
      if (!cleanOutput.includes('?') && !cleanOutput.toLowerCase().includes('help') && !this.conversationEnded) {
        cleanOutput += '\n\nIs there anything else I can help you with?';
      }
    }

    // Only add "This is the final response." if conversation has explicitly ended
    if (this.conversationEnded) {
      cleanOutput += '\n\nThis is the final response.';
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

  private getRecentProducts(result: any): any[] {
    // First check if we have cached products that are still fresh
    if (this.isCacheValid() && this.cachedProducts.length > 0) {
      return this.cachedProducts;
    }
    
    if (!result.intermediateSteps) return [];
    
    // Look for recent product listings in the conversation
    for (const step of result.intermediateSteps) {
      if (step.action && step.action.tool === 'list_products' && step.observation) {
        try {
          const products = JSON.parse(step.observation);
          if (Array.isArray(products)) {
            // Get the deduplicated products
            const deduplicatedProducts = this.deduplicateProducts(products);
            
            // Try to find price information for these products
            const productsWithPrices = this.enrichProductsWithPrices(deduplicatedProducts, result.intermediateSteps);
            
            // Cache the enriched products
            this.updateCache(productsWithPrices);
            
            return productsWithPrices;
          }
        } catch (e) {
          // Try to extract products from text format
          const productMatch = step.observation.match(/\[([^\]]+)\]/);
          if (productMatch) {
            // This is a simplified fallback - in practice, you'd want more robust parsing
            return [];
          }
        }
      }
    }
    
    return [];
  }

  private isCacheValid(): boolean {
    return Date.now() - this.cacheTimestamp < this.CACHE_DURATION;
  }

  private updateCache(products: any[]): void {
    this.cachedProducts = products;
    this.cacheTimestamp = Date.now();
  }

  private clearCache(): void {
    this.cachedProducts = [];
    this.cachedPrices = [];
    this.cacheTimestamp = 0;
  }

  private enrichProductsWithPrices(products: any[], intermediateSteps: any[]): any[] {
    // Look for price information in the intermediate steps
    const priceData: { [productId: string]: any[] } = {};
    
    for (const step of intermediateSteps) {
      if (step.action && step.action.tool === 'list_prices' && step.observation) {
        try {
          const prices = JSON.parse(step.observation);
          if (Array.isArray(prices)) {
            // Group prices by product ID
            for (const price of prices) {
              if (price.product && !priceData[price.product]) {
                priceData[price.product] = [];
              }
              if (price.product) {
                priceData[price.product].push(price);
              }
            }
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    }
    
    // Enrich products with their prices
    return products.map(product => ({
      ...product,
      prices: priceData[product.id] || []
    }));
  }


  private detectPurchaseIntent(input: string): boolean {
    const lowerInput = input.toLowerCase();
    const purchaseKeywords = [
      // Direct purchase words
      'buy', 'purchase', 'order', 'payment', 'pay', 'checkout',
      'want to buy', 'checkout;', 'would like to buy', 'interested in buying',
      'ready to purchase', 'ready to buy', 'i want', 'i need',
      'add to cart', 'get this', 'take this', "i'm sold", "where do I purchase", "where do I buy", "add to cart,", "place order,",
      'acquire', 'obtain', 'secure', 'procure', 'get my hands on',
      'pick up', 'grab', 'snag', 'score', 'cop', 'hook me up with',
      'charge', 'bill', 'invoice', 'transaction', 'payment link',
      'stripe link', 'checkout link', 'pay now', 'complete purchase',
      'finalize order', 'process payment', 'authorize payment',
      'put in cart', 'shopping cart', 'basket', 'proceed to checkout',
      'go to checkout', 'checkout process', 'submit order', 'confirm purchase',
      'looking to buy', 'thinking of buying', 'planning to purchase',
      'considering buying', 'thinking about getting', 'want to get',
      'would love to have', 'interested in purchasing', 'keen on buying',
      'ready to pay', 'ready to checkout', 'ready to complete',
      'let\'s do this', 'let\'s make it happen', 'sign me up',
      'count me in', 'sold me', 'convinced me',
      'how do I get', 'how can I buy', 'what\'s the process',
      'what\'s next', 'next steps', 'how to proceed', 'how to order'
    ];
    
    return purchaseKeywords.some(keyword => lowerInput.includes(keyword));
  }

  private shouldPromptForFeedback(input: string): boolean {
    const lowerInput = input.toLowerCase().trim();
    
    // More specific closing patterns that indicate conversation is ending
    const strongClosingPatterns = [
      'thank you', 'thanks', 'that\'s all', 'that\'s it', 'all set',
      'i\'m done', 'i\'m all set', 'goodbye', 'bye', 'see you later',
      'talk to you later', 'have a good day', 'have a great day', 'i\'m good', 'i\'m good to go', 'i\'m good to go!', 'no thanks', 'no thank you', 'no thank you!', 'nope', 'thank you', 'thank you!'
    ];
    
    // Simple closing words that need to be at the end or standalone
    const simpleClosingWords = ['done', 'finished', 'perfect', 'great', 'awesome'];
    
    // Check for strong closing patterns anywhere in the input
    const hasStrongClosing = strongClosingPatterns.some(pattern => lowerInput.includes(pattern));
    
    
    // Check for simple closing words only if they're at the end or standalone
    const hasSimpleClosingAtEnd = simpleClosingWords.some(word => {
      const words = lowerInput.split(/\s+/);
      const lastWords = words.slice(-2).join(' '); // Last two words
      return lastWords === word || lastWords.endsWith(` ${word}`) || words.length === 1 && words[0] === word;
    });
    
    // Do NOT trigger feedback for longer negative responses
    const isLongNegativeResponse = lowerInput.length > 20 && (lowerInput.includes('cannot') || lowerInput.includes('help me'));
    
      return (hasStrongClosing || hasSimpleClosingAtEnd) && !isLongNegativeResponse;
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
    this.conversationEnded = false; // Reset conversation state
  }


  // Add method to get session status
  getSessionStatus(): { active: boolean; sessionId: string | null; conversationEnded: boolean } {
    return {
      active: this.sessionActive,
      sessionId: this.sessionId,
      conversationEnded: this.conversationEnded,
    };
  }

  // Add method to explicitly end conversation
  async endConversation(): Promise<void> {
    this.conversationEnded = true;
    
    // End the Galileo session if active
    if (this.sessionActive && this.galileoCallbackHandler) {
      await this.galileoCallbackHandler.endSession();
      this.sessionActive = false;
    }
  }

  // Add method to check if conversation has ended
  isConversationEnded(): boolean {
    return this.conversationEnded;
  }

  // Add method to restart conversation
  restartConversation(): void {
    this.conversationEnded = false;
  }
}