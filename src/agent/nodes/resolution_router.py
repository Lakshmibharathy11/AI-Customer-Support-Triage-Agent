# src/agent/nodes/resolution_router.py

from datetime import datetime

from src.agent.state import AgentState


# Categories the agent is allowed to fully resolve on its own,
# IF the response is well-grounded (faithfulness check still applies)
AUTO_RESOLVABLE_CATEGORIES = [
    "password_reset",
    "how_to_question",
    "account_info_request",
    "billing_question",
]

# Categories that always require a human team to actually fix —
# the agent's job is first-response only, never full resolution
ALWAYS_ESCALATE_CATEGORIES = [
    "export_bug",
    "login_crash",
    "integration_failure",
    "billing_dispute",
    "cancellation_risk",
    "feature_request",
]

AUTO_RESOLVE_FAITHFULNESS_MIN = 0.85


def resolution_router(state: AgentState) -> AgentState:
    """
    Deterministic node — no LLM involved.

    Decides the ticket's outcome:
      - "resolved": category is self-service-eligible AND the
        response is well-grounded (faithfulness >= 0.85)
      - "escalated": category requires human ownership, OR the
        response wasn't confident enough to auto-resolve

    This runs AFTER the HITL gate (if HITL rejected the draft,
    final_response is None and this node treats it as escalated
    regardless of category).
    """
    category = state["category"]
    faithfulness = state.get("faithfulness_score", 0.0)
    hitl_decision = state.get("hitl_decision")

    # If HITL was involved and rejected, always escalate —
    # a human already said the draft wasn't good enough
    if hitl_decision == "rejected":
        outcome = "escalated"
        auto_resolved = False

    elif category in AUTO_RESOLVABLE_CATEGORIES and faithfulness >= AUTO_RESOLVE_FAITHFULNESS_MIN:
        outcome = "resolved"
        auto_resolved = True

    else:
        outcome = "escalated"
        auto_resolved = False

    state["outcome"] = outcome
    state["auto_resolved"] = auto_resolved

    if outcome == "resolved":
        now_iso = datetime.now().isoformat()
        state["first_reply_sent_at"] = now_iso
        state["resolved_at"] = now_iso
        if not state.get("final_response"):
            # No HITL occurred for this ticket (auto-resolved path
            # never goes through HITL) — final_response = draft
            state["final_response"] = state["drafted_response"]
    else:
        state["escalated"] = True

    return state