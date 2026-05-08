import { diag, DiagConsoleLogger, DiagLogLevel } from '@opentelemetry/api';
import { NodeSDK } from '@opentelemetry/sdk-node';
import { AlwaysOnSampler } from '@opentelemetry/sdk-trace-node';
import { GalileoSpanProcessor } from 'galileo';
import { env } from 'process';

const logLevel = (env.LOG_LEVEL?.toUpperCase() ?? 'INFO') as keyof typeof DiagLogLevel;
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel[logLevel] ?? DiagLogLevel.INFO);

export function setupOtel() {
  const sdk = new NodeSDK({
    spanProcessors: [new GalileoSpanProcessor()],
    sampler: new AlwaysOnSampler(),
  });

  sdk.start();
  console.log('OpenTelemetry initialized with Galileo span processor');
  return sdk;
}
