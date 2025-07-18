declare module 'galileo' {
  export class GalileoLogger {
    constructor(config: { projectName: string; logStreamName: string });
    startTrace(config: unknown): void;
    addLlmSpan(config: unknown): void;
    addToolSpan(config: unknown): void;
    addWorkflowSpan(config: unknown): void;
    conclude(config: unknown): void;
    flush(): Promise<void>;
  }
}
