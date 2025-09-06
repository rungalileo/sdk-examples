import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import dotenv from "dotenv";
import dotenvFlow from "dotenv-flow";

// 1) Load a shared file FIRST (lowest precedence among files)
//    Real env vars in process.env always win.
const shared = path.join(os.homedir(), ".config", "secrets", "myapps.env");
if (fs.existsSync(shared)) {
  dotenv.config({ path: shared, override: false });
}

// 2) Let dotenv-flow load the standard cascade for the project:
//    .env -> .env.local -> .env.[NODE_ENV] -> .env.[NODE_ENV].local
dotenvFlow.config({
  node_env: process.env.NODE_ENV, // e.g. "development", "test", "production"
  silent: true,                   // don’t log missing files
});

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
  app: {
    agentVerbose: boolean;
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
    app: {
      agentVerbose: process.env.AGENT_VERBOSE === 'false',
    },
  };
}

export const env = validateEnvironment();