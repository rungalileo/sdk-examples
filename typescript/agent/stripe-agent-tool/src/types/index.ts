export interface AgentMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export interface AgentResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

export interface PaymentRequest {
  amount: number;
  currency: string;
  description?: string;
  customerEmail?: string;
  metadata?: Record<string, string>;
}

export interface PaymentLinkRequest {
  productName: string;
  amount: number;
  currency: string;
  description?: string;
  successUrl?: string;
  cancelUrl?: string;
}

export interface CustomerRequest {
  email: string;
  name?: string;
  phone?: string;
  metadata?: Record<string, string>;
}

export interface AgentMetrics {
  executionTime: number;
  success: boolean;
  toolsUsed: string[];
  errorType?: string;
  cost?: number;
}