export interface ElevenLabsConfig {
  apiKey: string;
  agentId: string;
}

export interface GalileoConfig {
  apiKey: string;
  consoleUrl: string;
  projectName: string;
  logStream: string;
  protectEnabled: boolean;
  protectStageId?: string;
}

export interface AppConfig {
  elevenlabs: ElevenLabsConfig;
  galileo: GalileoConfig;
}

function getEnvVar(name: string, required: boolean = true): string {
  const value = process.env[name];
  if (required && !value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value || "";
}

export function getConfig(): AppConfig {
  return {
    elevenlabs: {
      apiKey: getEnvVar("ELEVENLABS_API_KEY"),
      agentId: getEnvVar("ELEVENLABS_AGENT_ID"),
    },
    galileo: {
      apiKey: getEnvVar("GALILEO_API_KEY"),
      consoleUrl: getEnvVar("GALILEO_CONSOLE_URL", false) || "https://app.galileo.ai",
      projectName: getEnvVar("GALILEO_PROJECT_NAME", false) || "voice-chatbot",
      logStream: getEnvVar("GALILEO_LOG_STREAM", false) || "default",
      protectEnabled: getEnvVar("GALILEO_PROTECT_ENABLED", false) === "true",
      protectStageId: getEnvVar("GALILEO_PROTECT_STAGE_ID", false) || undefined,
    },
  };
}

// Client-safe config (no secrets)
export interface ClientConfig {
  galileo: {
    consoleUrl: string;
    projectName: string;
    protectEnabled: boolean;
  };
}

export function getClientConfig(): ClientConfig {
  return {
    galileo: {
      consoleUrl: process.env.NEXT_PUBLIC_GALILEO_CONSOLE_URL || "https://app.galileo.ai",
      projectName: process.env.NEXT_PUBLIC_GALILEO_PROJECT_NAME || "voice-chatbot",
      protectEnabled: process.env.NEXT_PUBLIC_GALILEO_PROTECT_ENABLED === "true",
    },
  };
}
