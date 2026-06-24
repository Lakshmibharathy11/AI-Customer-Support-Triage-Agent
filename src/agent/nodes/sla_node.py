# src/agent/nodes/sla_node.py

from datetime import datetime

from src.agent.state import AgentState
from src.observability.logger import insert_sla_log, get_connection


def sla_node(state: AgentState) -> AgentState:
    """
    Deterministic node — no LLM involved.

    Writes the SLA deadline record to SQLite (first_reply_deadline
    and resolution_deadline were already calculated by
    tier_lookup_node). Marks breach flags if applicable based on
    whether the ticket was resolved/replied to before or after
    those deadlines.
    """
    now = datetime.now()

    first_reply_deadline = datetime.fromisoformat(state["first_reply_deadline"])
    resolution_deadline = datetime.fromisoformat(state["resolution_deadline"])

    first_reply_sent_at = state.get("first_reply_sent_at")
    resolved_at = state.get("resolved_at")

    # For auto-resolved tickets, first_reply_sent_at is already set
    # by resolution_router. For escalated tickets, the agent's draft
    # (once HITL-approved or auto-passed) still counts as the first
    # reply — the ticket just isn't RESOLVED yet.
    if not first_reply_sent_at and state.get("final_response"):
        first_reply_sent_at = now.isoformat()
        state["first_reply_sent_at"] = first_reply_sent_at

    first_reply_breached = False
    if first_reply_sent_at:
        sent_at = datetime.fromisoformat(first_reply_sent_at)
        first_reply_breached = sent_at > first_reply_deadline
    else:
        # No reply sent at all yet (e.g. HITL rejected, no final
        # response) — breached only if we're already past deadline
        first_reply_breached = now > first_reply_deadline

    resolution_breached = False
    if resolved_at:
        resolved_dt = datetime.fromisoformat(resolved_at)
        resolution_breached = resolved_dt > resolution_deadline
    else:
        resolution_breached = now > resolution_deadline

    insert_sla_log({
        "ticket_id": state["ticket_id"],
        "tier": state["tier"],
        "created_at": state.get("created_at", now.isoformat()),
        "first_reply_deadline": state["first_reply_deadline"],
        "resolution_deadline": state["resolution_deadline"],
        "first_reply_sent_at": first_reply_sent_at,
        "resolved_at": resolved_at,
        "first_reply_breached": int(first_reply_breached),
        "resolution_breached": int(resolution_breached),
    })

    state["total_latency_ms"] = (
        (state.get("llm_latency_ms") or 0)
        + (state.get("retrieval_latency_ms") or 0)
    )

    return state