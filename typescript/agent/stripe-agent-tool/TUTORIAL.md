# Building a Stripe AI Agent with Galileo Agent Reliability

This cookbook demonstrates how to set up and run a complete AI agent that integrates with Stripe's payment processing API via the [Stripe Agent Toolkit](https://github.com/stripe/agent-toolkit) while using [Galileo](https://galileo.ai) for AI Agent Reliability.

## Overview

By the end of this tutorial, you'll have a fully functional AI agent that can:
- List products and prices from Stripe
- Create payment links for customers
- Manage customer data
- Handle natural language conversations
- Track all interactions with Galileo observability

## Prerequisites
- Basic familiarity with TypeScript, Node.js, and the command line
- Node.js 18+
- npm or yarn
- A code editor (VS Code recommended)
- API Keys for the following services:
  - Stripe (free [developer sandbox](https://docs.stripe.com/sandboxes) account)
  - Galileo (free [developer account](https://app.galileo.ai/sign-up) available)
  - OpenAI API Key (this app should cost less that $5.00 total to run)

Before you start, you'll need to create a new project in Galileo, as well as create Stripe developer sandbox account. 

Instructions are below on how to do each of these actions. 

### Create a Galileo [Project](https://v2docs.galileo.ai/concepts/projects)
1. Go to [Galileo Dashboard](https://app.galileo.ai)
2. Click on "New Project"
3. Name your project "Stripe Agent"
4. Click on "Create Project"
5. Copy the project ID
6. Paste it into the .env file as GALILEO_PROJECT

### Create a Stripe Developer Sandbox Account
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/register)
2. Sign up for a free account
3. Navigate to the Developers section
4. Copy your test secret key (starts with `sk_test_`)
5. Paste it into the .env file as STRIPE_SECRET_KEY

## Getting Started

### Step 1: Clone the Repository

```bash
git clone https://github.com/rungalileo/sdk-examples
cd typescript/agent/stripe-agent-tool
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Rename this to `.env` , and add your own API keys:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Galileo Configuration
GALILEO_API_KEY=your_galileo_api_key_here
GALILEO_PROJECT=stripe-agent-demo
GALILEO_LOG_STREAM=production

# Agent Configuration
AGENT_NAME=StripePaymentAgent
AGENT_DESCRIPTION=An AI agent that helps with Stripe payment operations
```

**Important**: Replace the placeholder values with your actual API keys and be sure to have your .gitignore file updated to exclude the .env file.

### Step 4: Build the Project

```bash
npm run build
```

## Running Your Agent

### Interactive CLI Mode

Start the interactive command-line interface:

```bash
npm run interactive
```

This will:
- Initialize the agent with Galileo agent reliability.
- Start a conversation session
- Allow you to interact with the agent using natural language

**Example interactions:**
```
🚀 You: Show me your products
🤖 Assistant: Here are some of our products...

🚀 You: I want to buy a telescope
🤖 Assistant: I'll help you purchase a telescope...
```

**Available Commands:**
- `help` - Show available commands and examples
- `quit` or `exit` - Exit the application
- `clear` - Clear the terminal screen
- `!end` - Force flush Galileo traces (developer command)

### Web Server Mode

Start the web server for API access:

```bash
npm run web
```

The application will run on `http://localhost:3000`

**API Endpoint:**
```bash
POST /chat
Content-Type: application/json

{
  "message": "Show me your products",
  "sessionId": "optional-session-id"
}
```

### Automated Demo Mode
Run the automated demo script to see the agent in action: 

```bash
npm run dev
```

This demonstrates:
- Payment link creation
- Customer creation
- Product listing
- Subscription creation

## Understanding the Code Structure

### Core Components

```
src/
├── agents/
│   └── StripeAgent.ts          # Main agent implementation
├── config/
│   └── environment.ts          # Environment configuration
├── errors/
│   └── CircularToolError.ts    # Custom error handling
├── types/
│   └── index.ts               # TypeScript type definitions
├── interactive.ts             # CLI interface
└── server.ts                 # Web server
```

### Key Features

#### 1. Direct Galileo Integration

The agent uses direct Galileo integration (no wrapper):

```typescript
// Direct Galileo imports
const { init, flush, GalileoCallback } = require('galileo');

// Initialize in agent
async init() {
  try {
    await init();
    this.galileoCallback = new GalileoCallback();
    this.galileoEnabled = true;
    console.log('✅ Galileo initialized successfully.');
  } catch (error: any) {
    console.warn(`⚠️ Galileo initialization failed: ${error.message}`);
    this.galileoEnabled = false;
    this.galileoCallback = null;
  }
}
```

#### 2. Loop Prevention

Advanced circular tool usage detection:

```typescript
private detectCircularToolUsage(intermediateSteps: any[]): void {
  if (!intermediateSteps || intermediateSteps.length < 4) return;

  const recentTools = intermediateSteps
    .slice(-4)
    .map(step => step.action?.tool)
    .filter(tool => tool);

  const [tool1, tool2, tool3, tool4] = recentTools;
  
  if (tool1 === tool3 && tool2 === tool4 && tool1 !== tool2) {
    const pattern = [tool1, tool2];
    throw new CircularToolError(
      `Circular tool invocation detected: ${pattern.join(' -> ')} pattern repeated.`,
      pattern
    );
  }
}
```

#### 3. Conversation Memory

5-minute caching system:

```typescript
private cachedProducts: any[] = [];
private cacheTimestamp: number = 0;
private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

private isCacheValid(): boolean {
  return Date.now() - this.cacheTimestamp < this.CACHE_DURATION;
}
```

#### 4. Session Management

Integrated session tracking:

```typescript
private sessionContext: SessionContext | null = null;

interface SessionContext {
  sessionId: string;
  startTime: Date;
  conversationHistory: AgentMessage[];
  isActive: boolean;
  lastActivity: Date;
  messageCount: number;
  toolsUsed: Set<string>;
  metrics: {
    totalExecutionTime: number;
    successfulOperations: number;
    failedOperations: number;
    averageResponseTime?: number;
  };
}
```

## Galileo Observability

### What's Tracked

Your agent automatically tracks:
- All conversations and tool usage
- Performance metrics and response times
- Error rates and failure patterns
- Session information and user interactions
-[Tool selection quality](https://v2docs.galileo.ai/concepts/metrics/agentic/tool-selection-quality) and accuracy

### Viewing Your Data

1. Go to your [Galileo Dashboard](https://app.galileo.ai)
2. Navigate to your project
3. View traces, sessions, and metrics
4. Monitor agent performance over time

### Recommended Metrics

Based on the [Galileo documentation](https://v2docs.galileo.ai/concepts/metrics/overview), consider tracking:

- **[Tool Error](https://v2docs.galileo.ai/concepts/metrics/agentic/tool-error)**: Detects errors during tool execution
- **[Tool Selection Quality](https://v2docs.galileo.ai/concepts/metrics/agentic/tool-selection-quality)**: Determines if the agent selected the correct tool and arguments
- **[Context Adherence](https://v2docs.galileo.ai/concepts/metrics/response-quality/context-adherence)**: Measures closed-domain hallucinations

## Customization

### Adding New Tools

To add new Stripe tools, modify the agent initialization:

```typescript
private async initializeAgent(): Promise<void> {
  // Get tools from Stripe toolkit
  const tools = await this.stripeToolkit.getTools();
  
  // Add custom tools if needed
  const customTool = new DynamicTool({
    name: 'custom_tool',
    description: 'Your custom tool description',
    func: async (input: string) => {
      // Your custom logic here
      return 'Custom tool result';
    },
  });
  
  const allTools = [...tools, customTool];
  
  // Create the agent
  const prompt = await pull("hwchase17/structured-chat-zero-shot-react");
  
  this.agentExecutor = await createStructuredChatAgent({
    llm: this.llm,
    tools: allTools,
    prompt,
  });
}
```

### Modifying Prompts

To customize the agent's behavior, modify the prompt template:

```typescript
const customPrompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful Stripe assistant. Always be polite and professional."],
  ["human", "{input}"],
  ["human", "Chat History: {chat_history}"],
]);
```

### Environment Variables

Additional configuration options:

```
# Verbose logging
VERBOSE=true

# Custom Galileo console URL (for enterprise deployments — if you're using app.galileo.ai, there is no need to set this )
#GALILEO_CONSOLE_URL=https://console.galileo.ai

# Agent configuration
AGENT_NAME=MyCustomAgent
AGENT_DESCRIPTION=Custom agent description
```

## Troubleshooting

### Common Issues

#### 1. "Missing environment variables"
```bash
# Check your .env file exists
ls -la .env

# Verify all required variables are set
cat .env | grep -E "(STRIPE|OPENAI|GALILEO)"
```

#### 2. "Galileo initialization failed"
```bash
# Check your Galileo API key
echo $GALILEO_API_KEY

# Verify internet connection
curl -I https://app.galileo.ai
```

#### 3. "Stripe API errors"
```bash
# Verify your Stripe key format
echo $STRIPE_SECRET_KEY | grep "sk_test_"

# Test Stripe connection
curl -u $STRIPE_SECRET_KEY: https://api.stripe.com/v1/account
```

#### 4. "Agent not responding"
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Test OpenAI connection
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### Debug Mode

Enable verbose logging:

```bash
VERBOSE=true npm run interactive
```

### Manual Trace Flushing

Force flush Galileo traces:

```bash
# In interactive mode, type:
!end
```

## Next Steps

### 1. Extend Functionality
- Add more Stripe operations (refunds, subscriptions, etc.)
- Implement user authentication
- Add payment webhook handling

## Additional Resources

- [Stripe API Documentation](https://stripe.com/docs/api)
- [LangChain Documentation](https://js.langchain.com/)
- [Galileo Documentation](https://v2docs.galileo.ai/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the [Galileo documentation](https://v2docs.galileo.ai/)
3. Open an issue in the repository
4. Reach out to the Galileo developer team at [devrel@galileo.ai](mailto:devrel@galileo.ai)

Happy building! 🚀 