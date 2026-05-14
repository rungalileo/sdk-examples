import dotenv from "dotenv";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { AlwaysOnSampler } from "@opentelemetry/sdk-trace-node";
import { GalileoSpanProcessor } from "galileo";
import { trace } from "@opentelemetry/api";

// Load GALILEO_API_KEY, GALILEO_PROJECT, GALILEO_LOG_STREAM from .env
dotenv.config();

async function main() {
  // 1. Start the OTel SDK with GalileoSpanProcessor
  const sdk = new NodeSDK({
    spanProcessors: [new GalileoSpanProcessor()],
    sampler: new AlwaysOnSampler(),
  });
  sdk.start();

  // 2. Use the tracer to create spans
  const tracer = trace.getTracer("my-app");

  tracer.startActiveSpan("my-workflow", async (span) => {

    // Simulate some work (e.g., an LLM call)

    span.setAttribute("gen_ai.operation.name", "execute_tool")
    span.setAttribute("gen_ai.tool.name", "get_weather")
    span.setAttribute("gen_ai.tool.type", "function")

    span.setAttribute("gen_ai.tool.call.arguments", '{"city":"SF"}')
    span.setAttribute("gen_ai.tool.call.result", '{"temp_f":68}')

    span.end();
  });

  // 3. Shut down to ensure all traces are exported
  await sdk.shutdown();

  console.log("Trace sent to Galileo!");
}

main();