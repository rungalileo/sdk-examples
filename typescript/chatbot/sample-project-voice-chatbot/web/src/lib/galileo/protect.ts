// Galileo Protect client
// Supports two modes:
// 1. Direct REST API (Protect Status shows N/A in console)
// 2. Python microservice (Protect Status shows correctly)

// Configuration
const PYTHON_SERVICE_URL = process.env.GALILEO_PYTHON_SERVICE_URL;
const USE_PYTHON_SERVICE = !!PYTHON_SERVICE_URL;

export interface ProtectPayload {
  input?: string;
  output?: string;
  metadata?: Record<string, string>;
}

export interface RuleResult {
  status: "TRIGGERED" | "PASSED";
  metric: string;
  value: number;
  target_value: number;
  operator: string;
}

export interface RulesetResult {
  rule_results: RuleResult[];
}

export interface ProtectResponse {
  text: string;
  status: "triggered" | "not_triggered";
  action_result?: {
    type: "OVERRIDE" | "PASSTHROUGH";
    value?: string;
  };
  ruleset_results?: RulesetResult[];
  execution_time_ms?: number;
}

export interface GuardrailResult {
  blocked: boolean;
  status: "triggered" | "not_triggered";
  overrideMessage?: string;
  triggeredRules: Array<{
    metric: string;
    value: number;
    threshold: number;
    operator: string;
  }>;
  executionTimeMs?: number;
}

export async function invokeProtect(
  payload: ProtectPayload,
  stageId: string,
  projectName: string
): Promise<GuardrailResult> {
  const consoleUrl = process.env.GALILEO_CONSOLE_URL || "https://app.galileo.ai";
  // The API endpoint uses 'api.' instead of 'console.' in the hostname
  const apiUrl = consoleUrl.replace("://console.", "://api.");
  const apiKey = process.env.GALILEO_API_KEY;

  if (!apiKey) {
    throw new Error("GALILEO_API_KEY is not configured");
  }

  if (!stageId) {
    throw new Error("GALILEO_PROTECT_STAGE_ID is not configured");
  }

  const response = await fetch(`${apiUrl}/v2/protect/invoke`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Galileo-API-Key": apiKey,
    },
    body: JSON.stringify({
      payload,
      stage_id: stageId,
      project_name: projectName,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Protect API error: ${response.status} - ${errorText}`);
  }

  const result: ProtectResponse = await response.json();

  // Extract triggered rules
  const triggeredRules: GuardrailResult["triggeredRules"] = [];
  if (result.ruleset_results) {
    for (const ruleset of result.ruleset_results) {
      for (const rule of ruleset.rule_results) {
        if (rule.status === "TRIGGERED") {
          triggeredRules.push({
            metric: rule.metric,
            value: rule.value,
            threshold: rule.target_value,
            operator: rule.operator,
          });
        }
      }
    }
  }

  // Normalize status to lowercase for comparison (API may return uppercase)
  const normalizedStatus = result.status?.toLowerCase() as "triggered" | "not_triggered";

  return {
    blocked: normalizedStatus === "triggered",
    status: normalizedStatus,
    overrideMessage: result.action_result?.value,
    triggeredRules,
    executionTimeMs: result.execution_time_ms,
  };
}

/**
 * Invoke Protect via Python microservice.
 * This properly logs the Protect span so Protect Status shows in Galileo console.
 */
async function invokeProtectViaPython(
  payload: ProtectPayload,
  stageId: string,
  projectName: string,
  sessionId: string
): Promise<GuardrailResult> {
  if (!PYTHON_SERVICE_URL) {
    throw new Error("GALILEO_PYTHON_SERVICE_URL is not configured");
  }

  const response = await fetch(`${PYTHON_SERVICE_URL}/invoke-protect`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      input_text: payload.input,
      output_text: payload.output,
      stage_id: stageId,
      project_name: projectName,
      metadata: payload.metadata,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Python Protect service error: ${response.status} - ${errorText}`);
  }

  const result = await response.json();

  return {
    blocked: result.blocked,
    status: result.status,
    overrideMessage: result.override_message,
    triggeredRules: result.triggered_rules.map((rule: { metric: string; value: number; threshold: number; operator: string }) => ({
      metric: rule.metric,
      value: rule.value,
      threshold: rule.threshold,
      operator: rule.operator,
    })),
  };
}

export async function checkInputGuardrail(
  userTranscript: string,
  sessionId?: string
): Promise<GuardrailResult> {
  const stageId = process.env.GALILEO_PROTECT_STAGE_ID;
  const projectName = process.env.GALILEO_PROJECT_NAME || "voice-chatbot";

  if (!stageId) {
    console.log("Protect stage ID not configured, skipping guardrail check");
    return {
      blocked: false,
      status: "not_triggered",
      triggeredRules: [],
    };
  }

  const payload: ProtectPayload = {
    input: userTranscript,
    metadata: { role: "user", type: "input_guardrail" },
  };

  // Use Python service if available (for proper Protect Status logging)
  if (USE_PYTHON_SERVICE && sessionId) {
    console.log("[Protect] Using Python service for proper Protect Status logging");
    return invokeProtectViaPython(payload, stageId, projectName, sessionId);
  }

  // Fall back to direct REST API (Protect Status will show N/A)
  return invokeProtect(payload, stageId, projectName);
}

export async function checkOutputGuardrail(
  agentResponse: string,
  sessionId?: string
): Promise<GuardrailResult> {
  const stageId = process.env.GALILEO_PROTECT_STAGE_ID;
  const projectName = process.env.GALILEO_PROJECT_NAME || "voice-chatbot";

  if (!stageId) {
    console.log("Protect stage ID not configured, skipping guardrail check");
    return {
      blocked: false,
      status: "not_triggered",
      triggeredRules: [],
    };
  }

  const payload: ProtectPayload = {
    output: agentResponse,
    metadata: { role: "assistant", type: "output_guardrail" },
  };

  // Use Python service if available (for proper Protect Status logging)
  if (USE_PYTHON_SERVICE && sessionId) {
    console.log("[Protect] Using Python service for proper Protect Status logging");
    return invokeProtectViaPython(payload, stageId, projectName, sessionId);
  }

  // Fall back to direct REST API (Protect Status will show N/A)
  return invokeProtect(payload, stageId, projectName);
}
