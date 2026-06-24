# src/observability/slack_notifier.py

import httpx
from src.config.settings import settings


def send_escalation_alert(
    ticket_id: str,
    tier: str,
    category: str,
    priority: str,
    escalation_target: str,
    ticket_text: str,
    sla_deadline: str
) -> bool:
    """
    Sends a Slack notification when a ticket is escalated
    to a human team. Returns True if sent successfully.
    """

    if not settings.SLACK_WEBHOOK_URL:
        print("⚠️  SLACK_WEBHOOK_URL not set — skipping notification")
        return False

    color_map = {
        "critical": "#FF0000",
        "high": "#FF8C00",
        "medium": "#FFD700",
        "low": "#36A64F"
    }

    payload = {
        "text": f"🚨 Ticket Escalated: {ticket_id}",
        "attachments": [
            {
                "color": color_map.get(priority, "#808080"),
                "fields": [
                    {"title": "Ticket ID", "value": ticket_id, "short": True},
                    {"title": "Tier", "value": tier, "short": True},
                    {"title": "Category", "value": category, "short": True},
                    {"title": "Priority", "value": priority, "short": True},
                    {"title": "Routed To", "value": escalation_target, "short": True},
                    {"title": "SLA Deadline", "value": sla_deadline, "short": True},
                    {"title": "Ticket Content", "value": ticket_text[:300], "short": False},
                ]
            }
        ]
    }

    try:
        response = httpx.post(
            settings.SLACK_WEBHOOK_URL,
            json=payload,
            timeout=5.0
        )
        if response.status_code == 200:
            print("✅ Slack notification sent successfully")
            return True
        else:
            print(f"❌ Slack returned status {response.status_code}: {response.text}")
            return False
    except httpx.RequestError as e:
        print(f"❌ Slack request failed: {e}")
        return False