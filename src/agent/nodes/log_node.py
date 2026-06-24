# src/agent/nodes/log_node.py

from datetime import datetime

from src.agent.state import AgentState
from src.observability.logger import insert_ticket, update_ticket, get_connection


def _ticket_exists(ticket_id: str) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM tickets WHERE ticket_id = ?", (ticket_id,)
        )
        return cursor.fetchone() is not None


def log_node(state: AgentState) -> AgentState:
    """
    Deterministic node — no LLM involved. Final node in the graph.

    Writes (or updates) the complete ticket record to SQLite,
    consolidating every field accumulated by prior nodes:
    classification, tier/SLA info, retrieval stats, drafted
    response, eval scores, cost, latency, and final outcome.
    """
    cost_usd = _estimate_cost(state)

    record = {
        "tier": state["tier"],
        "category": state.get("category"),
        "priority": state.get("priority"),
        "ticket_text": state["ticket_text"],
        "drafted_response": state.get("drafted_response"),
        "outcome": state.get("outcome"),
        "escalation_target": state.get("escalation_target"),
        "auto_resolved": int(state.get("auto_resolved") or False),
        "hitl_required": int(state.get("hitl_required") or False),
        "hitl_decision": state.get("hitl_decision"),
        "faithfulness_score": state.get("faithfulness_score"),
        "relevance_score": state.get("relevance_score"),
        "chunks_retrieved": state.get("chunks_retrieved"),
        "parent_docs_used": state.get("parent_docs_used"),
        "input_tokens": state.get("input_tokens"),
        "output_tokens": state.get("output_tokens"),
        "judge_input_tokens": state.get("judge_input_tokens"),
        "judge_output_tokens": state.get("judge_output_tokens"),
        "cost_usd": cost_usd,
        "total_latency_ms": state.get("total_latency_ms"),
        "retrieval_latency_ms": state.get("retrieval_latency_ms"),
        "llm_latency_ms": state.get("llm_latency_ms"),
        "first_reply_sent_at": state.get("first_reply_sent_at"),
        "resolved_at": state.get("resolved_at"),
    }

    if _ticket_exists(state["ticket_id"]):
        update_ticket(state["ticket_id"], record)
    else:
        record["ticket_id"] = state["ticket_id"]
        record["created_at"] = state.get("created_at", datetime.now().isoformat())
        insert_ticket(record)

    state["cost_usd"] = cost_usd

    return state


def _estimate_cost(state: AgentState) -> float:
    """
    Estimates total LLM cost for this ticket using Groq's published
    per-token pricing from settings, across both main LLM calls
    (classify + draft) and judge calls (eval).
    """
    from src.config.settings import settings

    input_tokens = state.get("input_tokens") or 0
    output_tokens = state.get("output_tokens") or 0
    judge_input_tokens = state.get("judge_input_tokens") or 0
    judge_output_tokens = state.get("judge_output_tokens") or 0

    main_cost = (
        (input_tokens * settings.GROQ_INPUT_COST)
        + (output_tokens * settings.GROQ_OUTPUT_COST)
    ) / 1_000_000

    # Judge model costs less per token; using the same rate here
    # is a simplification — refine later if you pull exact
    # gpt-oss-20b pricing from Groq's pricing page
    judge_cost = (
        (judge_input_tokens * settings.GROQ_INPUT_COST)
        + (judge_output_tokens * settings.GROQ_OUTPUT_COST)
    ) / 1_000_000

    return round(main_cost + judge_cost, 6)
