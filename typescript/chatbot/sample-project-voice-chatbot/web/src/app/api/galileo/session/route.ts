import { NextResponse } from "next/server";
import { startGalileoSession, endGalileoSession } from "@/lib/galileo/logger";

export async function POST(request: Request) {
  try {
    const { sessionId, name } = await request.json();

    if (!sessionId) {
      return NextResponse.json(
        { error: "sessionId is required" },
        { status: 400 }
      );
    }

    await startGalileoSession(sessionId, name);

    return NextResponse.json({
      success: true,
      sessionId,
      message: "Session started",
    });
  } catch (error) {
    console.error("Error starting Galileo session:", error);
    return NextResponse.json(
      { error: "Failed to start session", details: String(error) },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (!sessionId) {
      return NextResponse.json(
        { error: "sessionId is required" },
        { status: 400 }
      );
    }

    await endGalileoSession(sessionId);

    return NextResponse.json({
      success: true,
      sessionId,
      message: "Session ended",
    });
  } catch (error) {
    console.error("Error ending Galileo session:", error);
    return NextResponse.json(
      { error: "Failed to end session", details: String(error) },
      { status: 500 }
    );
  }
}
