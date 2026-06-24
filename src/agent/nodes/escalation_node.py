# src/agent/nodes/escalation_node.py

from src.agent.state import AgentState
from src.observability.slack_notifier import send_escalation_alert
from src.observability.logger import update_ticket


def escalation_node(state: AgentState) -> AgentState:
    """
    Deterministic node — no LLM involved.

    Fires a Slack notification to the responsible team when a
    ticket's outcome is "escalated". This is the hand-off point:
    the agent's automated work ends here, and a human team now
    owns resolving the underlying issue.
    """
    send_escalation_alert(
        ticket_id=state["ticket_id"],
        tier=state["tier"],
        category=state["category"],
        priority=state["priority"],
        escalation_target=state["escalation_target"],
        ticket_text=state["ticket_text"],
        sla_deadline=state["resolution_deadline"],
    )

    update_ticket(state["ticket_id"], {
        "outcome": "escalated",
        "escalation_target": state["escalation_target"],
    })

    return state