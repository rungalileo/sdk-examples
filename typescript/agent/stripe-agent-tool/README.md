# Stripe Agents SDK Example

A self-contained TypeScript agent using Stripe Agent Toolkit with Galileo monitoring.

## Features

- **Stripe Integration**: Complete payment processing capabilities
- **AI Agent**: Powered by OpenAI GPT-4o-mini for intelligent customer interactions
- **Galileo Monitoring**: Comprehensive logging and analytics
- **Interactive Modes**: CLI and web server options
- **Self-contained**: All dependencies and assets included

## Prerequisites

- Node.js 18+ 
- npm or yarn
- Stripe account with API keys
- OpenAI API key
- Galileo account (optional, for monitoring)

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your actual API keys:
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GALILEO_API_KEY`: Your Galileo API key (optional)

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

## Scripts

- `npm run build` - Compile TypeScript to JavaScript
- `npm run start` - Run the compiled application
- `npm run dev` - Run in development mode with ts-node
- `npm run interactive` - Start interactive CLI mode
- `npm run web` - Start web server mode
- `npm run test` - Run test suite

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

## License


