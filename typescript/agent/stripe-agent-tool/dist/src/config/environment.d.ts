export interface EnvironmentConfig {
    stripe: {
        secretKey: string;
    };
    openai: {
        apiKey: string;
    };
    galileo: {
        apiKey: string;
        projectName: string;
        logStream: string;
    };
    agent: {
        name: string;
        description: string;
    };
}
export declare const env: EnvironmentConfig;
//# sourceMappingURL=environment.d.ts.map