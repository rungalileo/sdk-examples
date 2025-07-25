# Stripe Agents SDK Example

A self-contained TypeScript agent using Stripe Agent Toolkit with Galileo monitoring.

## Features

- **Stripe Integration**: Complete payment processing capabilities
- **AI Agent**: Powered by OpenAI GPT-4o-mini for intelligent customer interactions
- **Loop Prevention**: Advanced circular tool usage detection prevents infinite loops
- **Conversation Memory**: 5-minute product/price caching reduces redundant API calls
- **Buffered Logging**: Galileo traces are buffered and flushed efficiently
- **Galileo Monitoring**: Comprehensive logging and analytics
- **Interactive Modes**: CLI and web server options
- **Self-contained**: All dependencies and assets included

## Prerequisites

- Node.js 18+
- npm or yarn
- Stripe account with API keys
- OpenAI API key
- Galileo account 

## Setup

1. **Install dependencies**:

   ```bash
   npm install
   ```

2. **Configure environment**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with the keys for your project

   - `STRIPE_SECRET_KEY`: Your Stripe secret key (create a free developer account at https://dashboard.stripe.com/register)
   - `OPENAI_API_KEY`: Your OpenAI API key (create a developer account at https://platform.openai.com/signup)
   - `GALILEO_API_KEY`: Your Galileo API key (create a free developer account at https://galileo.ai/signup)
   - `GALILEO_PROJECT`: Your Galileo project name (create a free developer account at https://galileo.ai/signup)
   - `GALILEO_LOG_STREAM`: Your Galileo log stream name
   # Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
   # GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo
  

3. **Build the project**:

   ```bash
   npm run build
   ```

## Usage

### Interactive CLI Mode

```bash
npm run interactive
```

### Web Server Mode

```bash
npm run web
```

### Run Tests

```bash
npm test
```

## Agent Improvements

### Loop Prevention

The agent now includes advanced circular tool usage detection that:
- Monitors the last 4 tool calls for repeated patterns
- Detects when tools are being called in loops (e.g., A → B → A → B)
- Gracefully handles circular calls with appropriate error messages
- Prevents runaway loops that could exhaust API quotas

### Conversation Memory

Improved memory system with:
- **5-minute caching** of product and price data
- **Conversation history** maintained across interactions
- **Context awareness** using the last 6 messages for better responses
- **Reduced API calls** through intelligent caching

### Buffered Logging

Galileo logging improvements:
- **Buffered traces** are queued and flushed efficiently
- **Developer override** command `!end` to force flush during testing
- **Session management** with proper cleanup and error handling
- **Performance optimized** logging reduces response times

### Developer Commands

When using interactive mode, these special commands are available:

- `help` - Show available commands and examples
- `quit` or `exit` - Exit the application gracefully
- `clear` - Clear the terminal screen
- `!end` - **Developer command**: Force flush all buffered Galileo traces

### API Signature Changes

**AgentExecutor Configuration:**
```typescript
// Previous configuration
maxIterations: 6

// Updated configuration
maxIterations: 8  // Increased to handle complex interactions
earlyStoppingMethod: 'generate'  // Stop when agent decides it's complete
```

**New Caching Methods:**
```typescript
// Cache management
private isCacheValid(): boolean
private updateCache(products: any[]): void
private clearCache(): void

// Memory properties
private cachedProducts: any[] = []
private cachedPrices: any[] = []
private cacheTimestamp: number = 0
private readonly CACHE_DURATION = 5 * 60 * 1000 // 5 minutes
```

## Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm run start` - Run the compiled application
- `npm run dev` - Run in development mode with ts-node
- `npm run interactive` - Start interactive CLI mode
- `npm run web` - Start web server mode
- `npm run test` - Run test suite
- `npm run setup-products` - Set up space-themed product catalog in Stripe
- `npm run debug-prices` - Debug Stripe price creation and retrieval
- `npm run test-agent` - Test agent price reading capabilities

## Product Catalog Setup

This project includes a comprehensive space-themed product catalog for "Galileo's Gizmos". To set up the product catalog:

1. **Ensure your Stripe API key is configured** in your `.env` file
2. **Run the setup script**:

   ```bash
   npm run setup-products
   ```

This will create 20 space-themed products including:

- **Astronomical Equipment**: Telescopes, binoculars, camera adapters
- **Space Exploration Gear**: Training suits, VR helmets, Mars rovers
- **Educational Items**: Mars rocks, star maps, mission patches
- **Space Food**: Astronaut meals, energy bars, freeze-dried treats
- **Home & Lifestyle**: Nebula projectors, space bedding, cosmic art

### Product Categories

**🔭 Astronomical Equipment** ($29.99 - $1,299.99)

- Galileo's Premium Telescope
- Stellar Binoculars Pro
- Cosmic Camera Adapter
- Planetary Filter Set

**👨‍🚀 Space Exploration Gear** ($199.99 - $2,499.99)

- Astronaut Training Suit
- Zero Gravity Simulator
- Space Helmet VR
- Mars Rover Remote Control

**📚 Educational & Collectibles** ($29.99 - $89.99)

- Mars Rock Collection
- Cosmic Discovery Box
- Galileo's Star Map
- Space Mission Patch Set

**🍽️ Space Food & Nutrition** ($19.99 - $79.99)

- Astronaut Food Pack
- Cosmic Energy Bars
- Zero-G Coffee Mug
- Space Ice Cream

**🏠 Home & Lifestyle** ($44.99 - $159.99)

- Nebula Projector
- Space-Themed Bedding Set
- Cosmic Wall Art
- Astronaut Alarm Clock

## Project Structure

```
stripe-agents-sdk-example/
├── src/
│   ├── agents/           # Agent implementation
│   ├── config/           # Configuration files
│   ├── errors/           # Custom error classes
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   ├── index.ts          # Main entry point
│   ├── interactive.ts    # Interactive CLI mode
│   └── server.ts         # Web server mode
├── tests/                # Test files
├── public/               # Static assets
├── dist/                 # Compiled JavaScript output
├── package.json          # Dependencies and scripts
└── tsconfig.json         # TypeScript configuration
```

## Built Output

All compiled JavaScript files are output to the `dist/` directory, making the project ready for deployment.
