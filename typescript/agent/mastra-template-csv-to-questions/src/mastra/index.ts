import "../config/env";  // side-effect: loads env vars
import {
  OpenInferenceOTLPTraceExporter,
  isOpenInferenceSpan,
} from "@arizeai/openinference-mastra";
import { Mastra } from '@mastra/core/mastra';
import { LibSQLStore } from '@mastra/libsql';
import { PinoLogger } from '@mastra/loggers';
import { env } from "node:process";
import { csvQuestionAgent } from './agents/csv-question-agent';
import { csvSummarizationAgent } from './agents/csv-summarization-agent';
import { textQuestionAgent } from './agents/text-question-agent';
import { csvToQuestionsWorkflow } from './workflows/csv-to-questions-workflow';

console.log("Starting Mastra...");

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
  }),
  logger: new PinoLogger({
    name: 'Mastra',
    level: 'info',
  }),
  telemetry: {
    serviceName: "openinference-mastra-agent",
    enabled: true, // enable telemetry for this project
    sampling: {
      type: "always_on", // this makes it always sample traces so it's easier to test
    },
    export: {
      type: "custom", // we need to use the custom open inference exporter
      exporter: new OpenInferenceOTLPTraceExporter({
        url: `${(env.GALILEO_CONSOLE_URL ?? "https://app.galileo.ai")}/api/galileo/otel/traces`,// this is the endpoint for the otel traces
        headers: {
          "Galileo-API-Key": env.GALILEO_API_KEY ?? "your-galileo-api-key", // your galileo api key
          "project": env.GALILEO_PROJECT ?? "your-galileo-project", // your galileo project
          "logstream": env.GALILEO_LOG_STREAM ?? "default", // your galileo log stream
        },
        spanFilter: isOpenInferenceSpan,
      }),
    },
  },
});
