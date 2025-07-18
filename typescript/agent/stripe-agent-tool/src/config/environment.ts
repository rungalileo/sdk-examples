import { config } from 'dotenv';

// Load environment variables
config();

export interface EnvironmentConfig {
  stripe: {
    secretKey: string;
  };
  openai: {
    apiKey: string;
  };
  galileo: {
    apiKey: string;
    projectName: string;
    logStream: string;
  };
  agent: {
    name: string;
    description: string;
  };
}

function validateEnvironment(): EnvironmentConfig {
  const requiredVars = [
    'STRIPE_SECRET_KEY',
    'OPENAI_API_KEY',
    'GALILEO_API_KEY',
    'GALILEO_PROJECT',
    'GALILEO_LOG_STREAM',
    'AGENT_NAME',
    'AGENT_DESCRIPTION'
  ];

  const missing = requiredVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }

  return {
    stripe: {
      secretKey: process.env.STRIPE_SECRET_KEY!,
    },
    openai: {
      apiKey: process.env.OPENAI_API_KEY!,
    },
    galileo: {
      apiKey: process.env.GALILEO_API_KEY!,
      projectName: process.env.GALILEO_PROJECT!,
      logStream: process.env.GALILEO_LOG_STREAM!,
    },
    agent: {
      name: process.env.AGENT_NAME!,
      description: process.env.AGENT_DESCRIPTION!,
    },
  };
}

export const env = validateEnvironment();