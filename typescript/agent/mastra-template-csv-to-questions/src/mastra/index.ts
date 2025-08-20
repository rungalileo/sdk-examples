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
    serviceName: "openinference-mastra-agent", // you can rename this to whatever you want to appear in the Phoenix UI
    enabled: true,
    sampling: {
      type: "always_on",
    },
    export: {
      type: "custom",
      exporter: new OpenInferenceOTLPTraceExporter({
        url: `${(env.GALILEO_CONSOLE_URL ?? "https://app.galileo.ai")}/api/galileo/otel/traces`,
        headers: {
          "Galileo-API-Key": env.GALILEO_API_KEY ?? "your-galileo-api-key",
          "Galileo-Project": env.GALILEO_PROJECT ?? "your-galileo-project",
          "Galileo-Log-Stream": env.GALILEO_LOG_STREAM ?? "default",
          "project": env.GALILEO_PROJECT ?? "your-galileo-project",
          "logstream": env.GALILEO_LOG_STREAM ?? "default",
        },
        spanFilter: isOpenInferenceSpan,
      }),
    },
  },
});
