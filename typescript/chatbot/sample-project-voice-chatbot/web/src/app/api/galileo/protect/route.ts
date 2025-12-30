import { NextResponse } from "next/server";
import { checkInputGuardrail, checkOutputGuardrail } from "@/lib/galileo/protect";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { type, text } = body;

    if (!text) {
      return NextResponse.json(
        { error: "text is required" },
        { status: 400 }
      );
    }

    if (type !== "input" && type !== "output") {
      return NextResponse.json(
        { error: "type must be 'input' or 'output'" },
        { status: 400 }
      );
    }

    // Check if protect is enabled
    if (process.env.GALILEO_PROTECT_ENABLED !== "true") {
      return NextResponse.json({
        enabled: false,
        blocked: false,
        status: "not_triggered",
        message: "Protect is not enabled",
      });
    }

    const result = type === "input"
      ? await checkInputGuardrail(text)
      : await checkOutputGuardrail(text);

    console.log(`Protect ${type} guardrail result:`, result.status,
      result.triggeredRules.length > 0 ? `(${result.triggeredRules.map(r => r.metric).join(", ")})` : "");

    return NextResponse.json({
      enabled: true,
      ...result,
    });
  } catch (error) {
    console.error("Error checking guardrail:", error);
    return NextResponse.json(
      { error: "Failed to check guardrail", details: String(error) },
      { status: 500 }
    );
  }
}
