# src/agent/state.py

from typing import TypedDict, Optional


class AgentState(TypedDict):
    """
    Shared state passed between every node in the LangGraph agent.
    Each node reads what it needs and writes its own outputs back
    into this same dict — LangGraph merges updates automatically.
    """

    # ── Input (set when ticket is submitted) ──────────────
    ticket_id: str
    ticket_text: str
    tier: str
    created_at: str

    # ── classify_node output ──────────────────────────────
    category: Optional[str]
    initial_priority: Optional[str]

    # ── tier_lookup_node output ────────────────────────────
    priority: Optional[str]              # final priority after overrides
    sla_hours: Optional[float]
    resolution_hours: Optional[float]
    escalation_target: Optional[str]
    first_reply_deadline: Optional[str]
    resolution_deadline: Optional[str]

    # ── retrieve_node output ───────────────────────────────
    retrieved_parents: Optional[list[dict]]
    chunks_retrieved: Optional[int]
    parent_docs_used: Optional[int]
    retrieval_latency_ms: Optional[int]
    tier_restricted_match: Optional[dict]   # parent found but excluded by tier

    # ── draft_node output ──────────────────────────────────
    drafted_response: Optional[str]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    llm_latency_ms: Optional[int]

    # ── eval_node output (LLM-as-Judge) ────────────────────
    faithfulness_score: Optional[float]
    relevance_score: Optional[float]
    judge_reasoning: Optional[str]
    judge_input_tokens: Optional[int]
    judge_output_tokens: Optional[int]

    # ── routing decision ───────────────────────────────────
    hitl_required: Optional[bool]
    hitl_reason: Optional[str]

    # ── hitl_node output ────────────────────────────────────
    hitl_decision: Optional[str]          # "approved" | "rejected" | None
    hitl_notes: Optional[str]

    # ── resolution_router output ───────────────────────────
    outcome: Optional[str]                # "resolved" | "escalated"
    auto_resolved: Optional[bool]

    # ── escalation_node output ─────────────────────────────
    escalated: Optional[bool]

    # ── final / observability ──────────────────────────────
    final_response: Optional[str]
    total_latency_ms: Optional[int]
    cost_usd: Optional[float]
    resolved_at: Optional[str]
    first_reply_sent_at: Optional[str]