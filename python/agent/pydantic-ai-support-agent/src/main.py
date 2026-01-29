"""Enterprise customer support agent with Galileo observability."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from galileo.otel import GalileoSpanProcessor, add_galileo_span_processor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

# Set up Galileo observability
provider = TracerProvider()
trace.set_tracer_provider(provider)
add_galileo_span_processor(
    tracer_provider=provider,
    processor=GalileoSpanProcessor(project="pydantic-ai-support", logstream="default"),
)

# Enable instrumentation on all PydanticAI agents
Agent.instrument_all()


# --- Mock Database Models ---
@dataclass
class Customer:
    id: str
    name: str
    email: str
    tier: str  # "standard", "premium", "enterprise"
    account_created: datetime


@dataclass
class Order:
    id: str
    customer_id: str
    product: str
    amount: float
    status: str  # "pending", "shipped", "delivered", "cancelled"
    created_at: datetime


@dataclass
class SupportTicket:
    id: str
    customer_id: str
    subject: str
    priority: str
    status: str


# --- Mock Database ---
CUSTOMERS_DB: dict[str, Customer] = {
    "C001": Customer(
        "C001",
        "Alice Johnson",
        "alice@example.com",
        "enterprise",
        datetime(2022, 1, 15),
    ),
    "C002": Customer(
        "C002", "Bob Smith", "bob@example.com", "premium", datetime(2023, 6, 20)
    ),
    "C003": Customer(
        "C003", "Carol White", "carol@example.com", "standard", datetime(2024, 3, 10)
    ),
}

ORDERS_DB: dict[str, Order] = {
    "ORD-1001": Order(
        "ORD-1001",
        "C001",
        "Enterprise License",
        5000.00,
        "delivered",
        datetime(2024, 11, 1),
    ),
    "ORD-1002": Order(
        "ORD-1002",
        "C001",
        "Support Package",
        1200.00,
        "shipped",
        datetime(2024, 12, 15),
    ),
    "ORD-1003": Order(
        "ORD-1003",
        "C002",
        "Premium Subscription",
        299.99,
        "pending",
        datetime(2025, 1, 5),
    ),
}

TICKETS_DB: dict[str, SupportTicket] = {}
TICKET_COUNTER = 1000


# --- Agent Dependencies ---
@dataclass
class SupportDeps:
    customer_id: str


# --- Response Model ---
class SupportResponse(BaseModel):
    message: str
    ticket_id: Optional[str] = None
    refund_processed: bool = False


# --- Support Agent ---
support_agent = Agent(
    "openai:gpt-4o",
    deps_type=SupportDeps,
    output_type=SupportResponse,
    system_prompt=(
        "You are an enterprise customer support agent. "
        "Help customers with their inquiries by looking up their information, "
        "checking order status, creating support tickets, and processing refunds when appropriate. "
        "Always be professional and helpful. For enterprise customers, prioritize their requests."
    ),
)


@support_agent.tool
async def get_customer_info(ctx: RunContext[SupportDeps]) -> str:
    """Retrieve customer information including their tier and account details."""
    customer = CUSTOMERS_DB.get(ctx.deps.customer_id)
    if not customer:
        return "Customer not found."
    return (
        f"Customer: {customer.name}\n"
        f"Email: {customer.email}\n"
        f"Tier: {customer.tier}\n"
        f"Account since: {customer.account_created.strftime('%Y-%m-%d')}"
    )


@support_agent.tool
async def get_order_status(ctx: RunContext[SupportDeps], order_id: str) -> str:
    """Check the status of a specific order.

    Args:
        order_id: The order ID to look up (e.g., ORD-1001).
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        return f"Order {order_id} not found."
    if order.customer_id != ctx.deps.customer_id:
        return "You don't have access to this order."
    return (
        f"Order ID: {order.id}\n"
        f"Product: {order.product}\n"
        f"Amount: ${order.amount:.2f}\n"
        f"Status: {order.status}\n"
        f"Order date: {order.created_at.strftime('%Y-%m-%d')}"
    )


@support_agent.tool
async def list_customer_orders(ctx: RunContext[SupportDeps]) -> str:
    """List all orders for the current customer."""
    customer_orders = [
        o for o in ORDERS_DB.values() if o.customer_id == ctx.deps.customer_id
    ]
    if not customer_orders:
        return "No orders found for this customer."
    lines = ["Your orders:"]
    for order in customer_orders:
        lines.append(
            f"  - {order.id}: {order.product} (${order.amount:.2f}) - {order.status}"
        )
    return "\n".join(lines)


@support_agent.tool
async def create_support_ticket(
    ctx: RunContext[SupportDeps], subject: str, priority: str = "medium"
) -> str:
    """Create a new support ticket for the customer.

    Args:
        subject: Brief description of the issue.
        priority: Ticket priority - 'low', 'medium', 'high', or 'urgent'.
    """
    global TICKET_COUNTER
    customer = CUSTOMERS_DB.get(ctx.deps.customer_id)

    # Enterprise customers get priority boost
    if customer and customer.tier == "enterprise" and priority == "medium":
        priority = "high"

    TICKET_COUNTER += 1
    ticket_id = f"TKT-{TICKET_COUNTER}"
    ticket = SupportTicket(
        id=ticket_id,
        customer_id=ctx.deps.customer_id,
        subject=subject,
        priority=priority,
        status="open",
    )
    TICKETS_DB[ticket_id] = ticket
    return f"Support ticket created: {ticket_id} (Priority: {priority})"


@support_agent.tool
async def process_refund(
    ctx: RunContext[SupportDeps], order_id: str, reason: str
) -> str:
    """Process a refund for an order. Only available for delivered or shipped orders.

    Args:
        order_id: The order ID to refund.
        reason: Reason for the refund request.
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        return f"Order {order_id} not found."
    if order.customer_id != ctx.deps.customer_id:
        return "You don't have access to this order."
    if order.status not in ("delivered", "shipped"):
        return f"Cannot process refund for order with status: {order.status}"

    # Update order status
    order.status = "refunded"
    return f"Refund of ${order.amount:.2f} processed for order {order_id}. Reason: {reason}"


if __name__ == "__main__":
    # Simulate a customer support interaction
    deps = SupportDeps(customer_id="C001")

    # Invoke the support agent with a sample customer query
    result = support_agent.run_sync(
        "Hi, I need help with my recent order ORD-1002. It shows as shipped but I haven't "
        "received it yet. Can you check the status and create a support ticket for this issue?",
        deps=deps,
    )
    print(f"Response: {result.output.message}")
    if result.output.ticket_id:
        print(f"Ticket ID: {result.output.ticket_id}")
