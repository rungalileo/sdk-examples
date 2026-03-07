import dotenv from "dotenv";

// Load .env BEFORE initializing tracing so env vars are available
dotenv.config();

import { initTracing, shutdownTracing } from "./tracing.js";
import { runSession } from "./agent.js";

async function main(): Promise<void> {
  initTracing();

  const useRealLLM = process.env.USE_REAL_LLM === "true";

  if (useRealLLM && !process.env.OPENAI_API_KEY) {
    console.error("Error: OPENAI_API_KEY is required when USE_REAL_LLM=true");
    process.exit(1);
  }

  console.log("OpenTelemetry Collector Demo for Galileo");
  console.log("========================================");
  console.log(
    `Collector: ${process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318"}`,
  );
  console.log(`LLM mode: ${useRealLLM ? "Real OpenAI" : "Simulated (mock)"}`);

  try {
    await runSession(useRealLLM);
    console.log("Session complete. Flushing telemetry...");
  } catch (err) {
    console.error("Error during session:", err);
  } finally {
    // Give BatchSpanProcessor time to flush before shutdown
    await new Promise((resolve) => setTimeout(resolve, 3000));
    try {
      await shutdownTracing();
    } catch {
      console.warn(
        "[tracing] Shutdown encountered errors (collector may not be running)",
      );
    }
    console.log(
      "Done. Check Jaeger at http://localhost:16686 and Galileo for traces.",
    );
  }
}

main();
