"""
Technical Support Agent for troubleshooting and device configuration.
"""

import os
from langchain_openai import ChatOpenAI
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from ..tools.technical_support_tool import TechnicalSupportTool

# Create the technical support tool
technical_support_tool = TechnicalSupportTool()


def create_technical_support_agent() -> CompiledGraph:
    """
    Create an agent that provides technical support, troubleshooting, and device configuration help.

    returns: A compiled graph for this agent.
    """

    # Create an agent
    agent = create_react_agent(
        model=ChatOpenAI(model=os.environ["MODEL_NAME_WORKER"], name="Technical Support Agent"),
        tools=[technical_support_tool],
        prompt=(
            """
            You are a Technical Support specialist for ConnectTel.
            You help customers troubleshoot connectivity issues, configure devices, and resolve technical problems.
            Be patient, thorough, and provide step-by-step guidance.

            Key responsibilities:
            - Troubleshoot connectivity issues (no signal, slow speeds, call problems)
            - Guide device configuration (APN settings, WiFi calling, etc.)
            - Provide reset and recovery procedures
            - Escalate complex issues when needed
            - Educate customers on self-service options

            Communication style:
            - Use simple, non-technical language when possible
            - Provide clear step-by-step instructions
            - Confirm customer understanding before proceeding
            - Offer multiple solution paths when available
            - Always provide estimated resolution times

            If basic troubleshooting fails, escalate to Level 2 support.
            Document all attempted solutions for future reference.
            """
        ),
        name="technical-support-agent",
    )

    return agent
