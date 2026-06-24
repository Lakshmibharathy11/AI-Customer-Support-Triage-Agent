# src/agent/nodes/eval_node.py

import json
import time

from langchain_groq import ChatGroq

from src.config.settings import settings
from src.agent.state import AgentState
from src.agent.nodes.draft_node import format_context


JUDGE_PROMPT = """You are evaluating a customer support agent's response
for quality and accuracy.

TICKET:
{ticket_text}

GROUNDING CONTEXT PROVIDED TO THE AGENT:
{context}

AGENT'S RESPONSE:
{response}

Score the response on two dimensions:

1. FAITHFULNESS (0.0 to 1.0): Is every factual claim in the response
   actually supported by the grounding context? A response that
   states facts NOT present in the context (even if true-sounding)
   should score LOW. A response that only uses information from the
   context, or appropriately defers/refuses when context is missing
   or irrelevant, should score HIGH.

2. RELEVANCE (0.0 to 1.0): Does the response actually address what
   the customer asked? A response that is factually grounded but
   answers the wrong question should score LOW on relevance.

Respond with ONLY valid JSON, no other text:
{{"faithfulness": 0.0, "relevance": 0.0, "reasoning": "<one sentence>"}}
"""


def build_judge_context(state: AgentState) -> str:
    """
    Builds the grounding context the judge should evaluate against —
    mirroring draft_node's own branching logic exactly, so the judge
    sees the SAME grounding source the drafting LLM was given.
    """
    retrieved_parents = state.get("retrieved_parents") or []
    tier_restricted_match = state.get("tier_restricted_match")

    if retrieved_parents:
        return format_context(retrieved_parents)

    elif tier_restricted_match:
        required_tier = tier_restricted_match["tier_visibility"][0]
        return (
            f"NOTE: No customer-accessible content was found. However, "
            f"the system confirmed that '{tier_restricted_match['section_title']}' "
            f"is a real feature restricted to the {required_tier} tier. "
            f"A response stating this feature requires {required_tier} tier, "
            f"and offering to connect the customer with sales, is considered "
            f"fully grounded and appropriate."
        )

    else:
        return (
            "NOTE: No relevant knowledge base content was found at all. "
            "A response that acknowledges the ticket and defers to a "
            "human specialist (without inventing technical details) is "
            "considered fully grounded and appropriate."
        )


def eval_node(state: AgentState) -> AgentState:
    """
    LLM-as-Judge: scores the drafted response for faithfulness
    (grounded in the SAME context draft_node actually used — which
    may be retrieved_parents, a tier-restriction notice, or a
    no-match deferral notice) and relevance.
    """
    start_time = time.time()

    llm = ChatGroq(
        model=settings.JUDGE_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.0,
    )

    context = build_judge_context(state)

    prompt = JUDGE_PROMPT.format(
        ticket_text=state["ticket_text"],
        context=context,
        response=state["drafted_response"],
    )

    response = llm.invoke(prompt)
    raw_output = response.content.strip()

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").replace("json", "", 1).strip()

    try:
        parsed = json.loads(raw_output)
        faithfulness = float(parsed.get("faithfulness", 0.5))
        relevance = float(parsed.get("relevance", 0.5))
        reasoning = parsed.get("reasoning", "")
    except (json.JSONDecodeError, AttributeError, ValueError):
        faithfulness = 0.5
        relevance = 0.5
        reasoning = "Judge output could not be parsed — defaulted to neutral score"

    elapsed_ms = int((time.time() - start_time) * 1000)
    usage = response.response_metadata.get("token_usage", {})

    state["faithfulness_score"] = faithfulness
    state["relevance_score"] = relevance
    state["judge_reasoning"] = reasoning
    state["judge_input_tokens"] = usage.get("prompt_tokens", 0)
    state["judge_output_tokens"] = usage.get("completion_tokens", 0)
    state["llm_latency_ms"] = (state.get("llm_latency_ms") or 0) + elapsed_ms

    return state