"""
Supervisor Agent for ConnectTel Telecom Application
"""

import os
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import MemorySaver

from .billing_account_agent import create_billing_account_agent
from .technical_support_agent import create_technical_support_agent
from .plan_advisor_agent import create_plan_advisor_agent

# Define the agents that the supervisor will manage
billing_account_agent = create_billing_account_agent()
technical_support_agent = create_technical_support_agent()
plan_advisor_agent = create_plan_advisor_agent()


def create_supervisor_agent():
    """
    Create a supervisor agent that manages all the agents in the ConnectTel telecom application.
    """
    # Create a memory checkpointer to persist conversation history
    checkpointer = MemorySaver()

    telecom_supervisor_agent = create_supervisor(
        model=ChatOpenAI(model=os.environ["MODEL_NAME_SUPERVISOR"], name="Supervisor"),
        agents=[
            billing_account_agent,
            technical_support_agent,
            plan_advisor_agent,
        ],
        prompt=(
            """
            You are a supervisor managing a team of specialized telecom service agents at ConnectTel.

            Route customer queries to the appropriate agent based on their needs:

            - Billing Account Agent: Bill inquiries, payment issues, usage tracking, account balance, charges, credit card information, credit score, etc.  
            - Technical Support Agent: Device troubleshooting, connectivity issues, configuration help, resets
            - Plan Advisor Agent: Plan recommendations, upgrades, comparing plans, finding savings

            Guidelines:
            - Route queries to the most appropriate specialist agent
            - For complex issues spanning multiple areas, coordinate between agents
            - Be helpful and empathetic to customer concerns
            - If unsure, ask clarifying questions before routing
            - For general greetings, respond warmly before asking how you can help

            If a query doesn't fit any agent's expertise, politely explain our service limitations.
            """
        ),
        add_handoff_back_messages=True,
        output_mode="full_history",
        supervisor_name="connecttel-supervisor-agent",
    ).compile(checkpointer=checkpointer)
    telecom_supervisor_agent.name = "connecttel-supervisor-agent"

    # Uncomment the following lines to print the compiled graph to the console in Mermaid format
    # print("Compiled Telecom Supervisor Agent Graph:")
    # print(telecom_supervisor_agent.get_graph().draw_mermaid())

    return telecom_supervisor_agent
