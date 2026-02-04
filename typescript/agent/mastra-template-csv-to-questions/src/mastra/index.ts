import { Mastra } from '@mastra/core/mastra';
import { LibSQLStore } from '@mastra/libsql';
import { PinoLogger } from '@mastra/loggers';
import {
  Observability,
  SamplingStrategyType
} from '@mastra/observability';
import { OtelExporter } from "@mastra/otel-exporter";
import 'dotenv/config';
import { env } from 'node:process';
import { csvQuestionAgent } from './agents/csv-question-agent';
import { csvSummarizationAgent } from './agents/csv-summarization-agent';
import { textQuestionAgent } from './agents/text-question-agent';
import { csvToQuestionsWorkflow } from './workflows/csv-to-questions-workflow';

// The endpoint can be configured via environment variable or defaults to the Galileo production endpoint
const ObservabilityEndpoint = env.GALILEO_API_URL || "https://api.galileo.ai";

export const mastra = new Mastra({
  workflows: { csvToQuestionsWorkflow },
  agents: {
    textQuestionAgent,
    csvQuestionAgent,
    csvSummarizationAgent,
  },
  storage: new LibSQLStore({
    // stores telemetry, evals, ... into memory storage, if it needs to persist, change to file:../mastra.db
    url: ':memory:',
    id: 'libsql-storage',
  }),
  logger: new PinoLogger({
    name: 'Mastra',
    level: 'info',
  }),
  observability: new Observability({
    configs: {
      otel: {
        sampling: { type: SamplingStrategyType.ALWAYS },
        serviceName: 'galileo-mastra-agent',
        exporters: [
          new OtelExporter({
            provider: {
              custom: {
                endpoint: `${ObservabilityEndpoint}/otel/v1/traces`,
                headers: {
                  'Galileo-API-Key': process.env.GALILEO_API_KEY ?? '',
                  'project': env.GALILEO_PROJECT ?? '',
                  'logstream': env.GALILEO_LOG_STREAM ?? '',
                },
                protocol: 'http/protobuf',
              }
            },
          }),
        ]
      }
    }
  }),
});
