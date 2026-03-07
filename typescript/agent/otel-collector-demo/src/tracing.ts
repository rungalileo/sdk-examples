import { diag, DiagConsoleLogger, DiagLogLevel } from "@opentelemetry/api";
import { Resource } from "@opentelemetry/resources";
import { BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} from "@opentelemetry/semantic-conventions";

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

let provider: NodeTracerProvider | null = null;

export function initTracing(): void {
  const collectorUrl =
    process.env.OTEL_EXPORTER_OTLP_ENDPOINT || "http://localhost:4318";

  const exporter = new OTLPTraceExporter({
    url: `${collectorUrl}/v1/traces`,
    // No Galileo headers here — the collector handles authentication
  });

  const resource = new Resource({
    [ATTR_SERVICE_NAME]: "otel-ts-collector-demo",
    [ATTR_SERVICE_VERSION]: "1.0.0",
    "deployment.environment": process.env.DEPLOYMENT_ENV || "development",
  });

  provider = new NodeTracerProvider({ resource });
  provider.addSpanProcessor(new BatchSpanProcessor(exporter));
  provider.register();

  console.log(
    `[tracing] OpenTelemetry initialized, exporting to ${collectorUrl}`,
  );
}

export async function shutdownTracing(): Promise<void> {
  if (provider) {
    await provider.shutdown();
    console.log("[tracing] OpenTelemetry shut down");
  }
}
