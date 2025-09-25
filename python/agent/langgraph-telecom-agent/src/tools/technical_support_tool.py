"""
Mock technical support tool for telecom demo system.
Provides troubleshooting steps and device configuration assistance.
"""

from typing import Optional
from langchain.tools import BaseTool
from datetime import datetime, timedelta
import random


class TechnicalSupportTool(BaseTool):
    """Tool for troubleshooting and technical support."""

    name: str = "technical_support"
    description: str = "Troubleshoot connectivity issues, configure devices, and provide technical solutions"

    def _run(self, issue_type: Optional[str] = None, action: str = "help") -> str:
        """
        Provide technical support.

        Args:
            issue_type: Type of issue (no_signal, slow_internet, calls, wifi_calling)
            action: Action to take (help, troubleshoot, configure, escalate)
        """

        # Troubleshooting guides
        guides = {
            "no_signal": """
No Signal Troubleshooting:
1. Toggle Airplane Mode on/off
2. Restart device
3. Check SIM card
4. Reset network settings
5. Update carrier settings
Time: 5-10 minutes
""",
            "slow_internet": """
Slow Internet Fix:
1. Check network type (5G/4G)
2. Run speed test
3. Clear cache
4. Disable background apps
5. Reset APN settings
Time: 10-15 minutes
""",
            "calls": """
Call Issues Fix:
1. Check Do Not Disturb
2. Verify blocked numbers
3. Enable VoLTE/HD Voice
4. Reset network settings
5. Check account status
Time: 5-8 minutes
""",
            "wifi_calling": """
WiFi Calling Setup:
1. Settings > Phone > Wi-Fi Calling
2. Toggle ON
3. Update E911 address
4. Ensure stable WiFi
5. Wait 2-3 minutes
Time: 3-5 minutes
"""
        }

        if action == "escalate":
            ticket_id = f"TECH-{random.randint(1000, 9999)}"
            return f"""
Support Ticket Created: {ticket_id}
Priority: High
Response Time: Within 2 hours
Callback: {(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M')}
24/7 Support: 1-800-TELECOM
"""

        if action == "configure":
            return """
Device Configuration:
iPhone: Settings > Cellular > Cellular Data Options
- APN: wholesale
- Leave username/password blank

Android: Settings > Network > Mobile > APN
- APN: fast.t-mobile.com
- APN Type: default,supl,mms

Restart device after changes.
"""

        if issue_type and issue_type in guides:
            return guides[issue_type]

        # Default help menu
        return """
Technical Support Options:
- no_signal: Fix service issues
- slow_internet: Improve speeds
- calls: Voice call problems
- wifi_calling: Setup guide

Actions:
- configure: Device setup
- escalate: Create ticket

Quick Codes:
- Signal info: *3001#12345#*
- Network reset: *#*#72786#*#*
"""