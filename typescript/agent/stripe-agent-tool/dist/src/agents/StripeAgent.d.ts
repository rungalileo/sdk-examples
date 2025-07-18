import { AgentMessage, AgentResponse, PaymentLinkRequest, CustomerRequest } from '../types';
export declare class StripeAgent {
    private stripeToolkit;
    private llm;
    private agentExecutor;
    private conversationHistory;
    private galileoLogger;
    private sessionId;
    private sessionActive;
    constructor();
    init(): Promise<void>;
    private initializeStripeToolkit;
    private initializeLLM;
    private initializeAgent;
    processMessage(userMessage: string): Promise<AgentResponse>;
    private buildConversationContext;
    private cleanAndFormatResponse;
    private extractToolsUsed;
    private logTraceToGalileo;
    private deduplicateProducts;
    private getRecentProducts;
    private generateTraceName;
    private detectPurchaseIntent;
    private shouldPromptForFeedback;
    /**
     * Detects circular tool usage patterns in intermediate steps
     * Keeps a sliding window of the last 3 tool calls and checks for repeated patterns
     */
    private detectCircularToolUsage;
    createPaymentLink(request: PaymentLinkRequest): Promise<AgentResponse>;
    createCustomer(request: CustomerRequest): Promise<AgentResponse>;
    getConversationHistory(): AgentMessage[];
    clearConversationHistory(): void;
    startGalileoSession(sessionName: string): Promise<string>;
    logConversationToGalileo(): Promise<void>;
    concludeGalileoSession(): Promise<void>;
    getSessionStatus(): {
        active: boolean;
        sessionId: string | null;
    };
}
//# sourceMappingURL=StripeAgent.d.ts.map