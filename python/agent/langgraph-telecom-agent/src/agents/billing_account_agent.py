"""
Billing and Account Management Agent for handling customer billing inquiries.
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from ..tools.billing_tool import BillingTool

# Create the billing tool
billing_tool = BillingTool()


def create_billing_account_agent() -> CompiledGraph:
    """
    Create an agent that handles billing inquiries, usage tracking, and account management.

    returns: A compiled graph for this agent.
    """

    # Create an agent
    agent = create_react_agent(
        model=ChatOpenAI(model=os.environ["MODEL_NAME_WORKER"], name="Billing Account Agent"),
        tools=[billing_tool],
        prompt=("""
            You are a Billing and Account specialist for ConnectTel.
            You help customers with billing inquiries, usage tracking, plan details, and payment issues.
            Be helpful, accurate, and proactive in identifying potential savings.

            Key responsibilities:
            - Check account balances and payment due dates
            - Track data, voice, and text usage
            - Explain charges and fees clearly
            - Suggest plan optimizations based on usage
            - Process payment-related inquiries
            - Review billing history

            When discussing charges:
            - Break down costs clearly
            - Highlight any unusual charges
            - Suggest ways to reduce bills if usage patterns show opportunity
            - Always mention auto-pay discounts if not enrolled

            Be empathetic about high bills and offer solutions.
            """),
        name="billing-account-agent",
    )

    return agent
