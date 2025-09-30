"""
Mock billing tool for telecom demo system.
Returns simulated customer billing and usage data.
"""

from typing import Optional
from langchain.tools import BaseTool
from datetime import datetime, timedelta
import random


class BillingTool(BaseTool):
    """Tool for retrieving customer billing and usage information."""

    name: str = "billing_account"
    description: str = "Check account balance, data usage, plan details, and billing history"

    def _run(self, customer_id: Optional[str] = None, query_type: str = "summary") -> str:
        """
        Get billing and usage information.

        Args:
            customer_id: Customer account number (uses default if not provided)
            query_type: Type of query (summary, usage, plan, history)
        """
        # Simple mock customer data
        customer = {
            "name": "John Doe",
            "account": customer_id or "ACC-2024-789456",
            "plan": "Premium Unlimited 5G",
            "monthly_charge": 85.00,
            "data_used": random.uniform(20, 80),
            "data_limit": "Unlimited",
            "due_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
        }

        if query_type == "usage":
            return f"""
Usage Summary for {customer['name']}:
- Data: {customer['data_used']:.1f} GB used ({customer['data_limit']})
- Minutes: {random.randint(300, 800)} (Unlimited)
- Texts: {random.randint(500, 2000)} (Unlimited)
- Average daily: {customer['data_used'] / 15:.2f} GB
"""

        elif query_type == "plan":
            return f"""
Current Plan: {customer['plan']}
- Monthly Cost: ${customer['monthly_charge']:.2f}
- Data: {customer['data_limit']}
- Talk & Text: Unlimited
- 5G Access: Included

Available Upgrades:
- Business Elite ($120/month)
- International Plus ($95/month)
"""

        elif query_type == "history":
            history = []
            for i in range(3):
                date = (datetime.now() - timedelta(days=30 * (i + 1))).strftime("%Y-%m-%d")
                amount = customer["monthly_charge"] + random.uniform(-5, 15)
                history.append(f"- {date}: ${amount:.2f} (Paid)")

            return f"""
Billing History:
{chr(10).join(history)}

Auto-pay: Enabled
"""

        # Default summary
        return f"""
Account Summary for {customer['name']}:
- Account: {customer['account']}
- Plan: {customer['plan']}
- Amount Due: ${customer['monthly_charge']:.2f}
- Due Date: {customer['due_date']}
- Data Used: {customer['data_used']:.1f} GB ({customer['data_limit']})
"""
