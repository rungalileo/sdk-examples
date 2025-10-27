import { diag, DiagConsoleLogger, DiagLogLevel } from '@opentelemetry/api';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { AlwaysOnSampler, SimpleSpanProcessor } from '@opentelemetry/sdk-trace-node';
import { OTLPHttpProtoTraceExporter } from '@vercel/otel';
import { env } from 'process';

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG); // set diaglog level to DEBUG when debugging

/**
 * Setup the OpenTelemetry SDK for the application.
 */
export function setupOtel() {
  const galileoConsoleUrl = env.GALILEO_CONSOLE_URL || "https://app.galileo.ai";
  const galileoEndpoint = `${galileoConsoleUrl}/api/galileo/otel/traces`;
  const galileoHeaders = {
    "Galileo-API-Key": env.GALILEO_API_KEY || "your-galileo-api-key", // your galileo api key
    "project": env.GALILEO_PROJECT || "your-galileo-project", // your galileo project
    "logstream": env.GALILEO_LOG_STREAM || "default", // your galileo log stream
  };

  const sdk = new NodeSDK({
    spanProcessors: [new SimpleSpanProcessor(new OTLPHttpProtoTraceExporter({
      url: galileoEndpoint,
      headers: galileoHeaders,
    }))],
    sampler: new AlwaysOnSampler(),
  });

  sdk.start();
}
