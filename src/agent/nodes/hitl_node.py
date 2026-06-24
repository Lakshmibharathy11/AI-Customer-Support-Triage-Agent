# src/agent/nodes/hitl_node.py

from datetime import datetime

from langgraph.types import interrupt

from src.agent.state import AgentState
from src.observability.logger import insert_hitl_queue, update_ticket


def hitl_node(state: AgentState) -> AgentState:
    """
    Pauses graph execution and queues the ticket for human review.
    Uses LangGraph's interrupt() — execution literally stops here
    until the graph is resumed with a human decision.

    Note: LangGraph may re-execute this node's body from the top
    when resuming after an interrupt. insert_hitl_queue() is
    idempotent (INSERT OR IGNORE keyed on ticket_id), so repeated
    calls on re-entry are safe.
    """
    insert_hitl_queue({
        "ticket_id": state["ticket_id"],
        "drafted_response": state["drafted_response"],
        "reason": state.get("hitl_reason", "unspecified"),
        "status": "pending",
        "queued_at": datetime.now().isoformat(),
    })
    update_ticket(state["ticket_id"], {"hitl_required": 1})

    human_decision = interrupt({
        "ticket_id": state["ticket_id"],
        "drafted_response": state["drafted_response"],
        "reason": state.get("hitl_reason"),
        "category": state.get("category"),
        "priority": state.get("priority"),
        "tier": state.get("tier"),
    })

    decision = human_decision.get("decision", "rejected")
    notes = human_decision.get("notes", "")

    state["hitl_decision"] = decision
    state["hitl_notes"] = notes

    if decision == "approved":
        state["final_response"] = state["drafted_response"]
    else:
        state["final_response"] = None

    return state