# src/agent/nodes/tier_lookup_node.py

from datetime import datetime, timedelta
from src.config.tier_matrix import get_escalation_target
from src.config.settings import settings
from src.config.tier_matrix import (
    get_tier_config,
    get_priority_override,
    get_sla_hours,
    needs_hitl,
)
from src.agent.state import AgentState


def tier_lookup_node(state: AgentState) -> AgentState:
    """
    Deterministic node — no LLM involved.

    Takes the LLM's classification (category, initial_priority) and:
    1. Looks up the customer's tier SLA config
    2. Applies any business-rule priority overrides
    3. Calculates first_reply and resolution deadlines
    4. Determines escalation target

    HITL determination happens here too, but faithfulness_score
    isn't available yet at this point in the graph (it's set by
    eval_node later) — so the faithfulness-based trigger is
    re-checked again after eval_node runs. This node only checks
    the category/priority-based triggers.
    """
    tier_config = get_tier_config(state["tier"])

    category = state["category"]
    initial_priority = state["initial_priority"]

    # Apply deterministic priority override if one exists
    override = get_priority_override(state["tier"], category)
    final_priority = override if override else initial_priority

    # Calculate SLA deadlines based on final priority
    first_reply_hours = get_sla_hours(state["tier"], final_priority)
    resolution_hours = tier_config["resolution_hours"]
    if final_priority == "critical":
        resolution_hours = resolution_hours / 2

    now = datetime.now()
    first_reply_deadline = now + timedelta(hours=first_reply_hours)
    resolution_deadline = now + timedelta(hours=resolution_hours)

    # Check HITL triggers available at this stage (category + priority).
    # faithfulness check happens again after eval_node, since that
    # score doesn't exist yet.
    hitl_required = needs_hitl(
        category=category,
        priority=final_priority,
        faithfulness=1.0,  # placeholder — passes faithfulness check for now
    )
    hitl_reason = None
    if category in settings.HITL_CATEGORIES:
        hitl_reason = f"category={category}"
    elif final_priority in settings.HITL_PRIORITIES:
        hitl_reason = f"priority={final_priority}"

    state["priority"] = final_priority
    state["sla_hours"] = first_reply_hours
    state["resolution_hours"] = resolution_hours
    state["escalation_target"] = get_escalation_target(state["tier"], category)
    state["first_reply_deadline"] = first_reply_deadline.isoformat()
    state["resolution_deadline"] = resolution_deadline.isoformat()
    state["hitl_required"] = hitl_required
    state["hitl_reason"] = hitl_reason

    return state