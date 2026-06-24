# src/agent/nodes/draft_node.py

import time

from langchain_groq import ChatGroq

from src.config.settings import settings
from src.agent.state import AgentState


NORMAL_PROMPT = """You are a support agent for Stacklytics, a B2B
product-analytics SaaS company. Write a helpful, professional response
to the customer's ticket using ONLY the knowledge base context provided.
Do not invent facts not present in the context.

CUSTOMER TIER: {tier}

TICKET:
{ticket_text}

KNOWLEDGE BASE CONTEXT:
{context}

Write a clear, concise response (3-6 sentences). Do not include a
greeting or signature — just the body of the response.
"""

TIER_RESTRICTED_PROMPT = """You are a support agent for Stacklytics, a B2B
product-analytics SaaS company. The customer is asking about a feature
that exists, but is only available on a higher plan tier than their own.

CUSTOMER TIER: {tier}
FEATURE REQUIRES TIER: {required_tier}
FEATURE TOPIC: {feature_topic}

TICKET:
{ticket_text}

Write a polite, professional response that:
1. Acknowledges their question
2. Clearly explains this feature is available on the {required_tier} plan
3. Offers to connect them with the sales team to discuss upgrading
Do not include a greeting or signature — just the body of the response.
Keep it to 3-4 sentences.
"""

NO_MATCH_PROMPT = """You are a support agent for Stacklytics, a B2B
product-analytics SaaS company. No relevant knowledge base content
was found for this ticket.

TICKET:
{ticket_text}

Write a brief, professional response acknowledging the ticket and
letting the customer know their request has been forwarded to a
specialist who will follow up. Do not guess at a solution or invent
any technical details. Do not include a greeting or signature — just
the body of the response. Keep it to 2-3 sentences.
"""


def format_context(parents: list[dict]) -> str:
    """
    Formats retrieved parent chunks into a single context block
    for the prompt, preserving section titles and table structure.
    """
    blocks = []
    for p in parents:
        blocks.append(f"[{p['title']} — {p['section_title']}]\n{p['text']}")
    return "\n\n".join(blocks)


def draft_node(state: AgentState) -> AgentState:
    """
    Generates the customer-facing draft response using the main LLM.
    Branches into three modes based on retrieve_node's output:

    1. Normal — retrieved_parents has content, draft grounded in it
    2. Tier-restricted — no accessible content, but a higher-tier
       match exists, draft a polite upsell-style response
    3. No match — nothing found at all, draft a deferral response
    """
    start_time = time.time()

    llm = ChatGroq(
        model=settings.MAIN_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.3,  # slight creativity for natural-sounding prose
    )

    retrieved_parents = state.get("retrieved_parents") or []
    tier_restricted_match = state.get("tier_restricted_match")

    if retrieved_parents:
        context = format_context(retrieved_parents)
        prompt = NORMAL_PROMPT.format(
            tier=state["tier"],
            ticket_text=state["ticket_text"],
            context=context,
        )

    elif tier_restricted_match:
        required_tier = tier_restricted_match["tier_visibility"][0]
        prompt = TIER_RESTRICTED_PROMPT.format(
            tier=state["tier"],
            required_tier=required_tier,
            feature_topic=tier_restricted_match["section_title"],
            ticket_text=state["ticket_text"],
        )

    else:
        prompt = NO_MATCH_PROMPT.format(ticket_text=state["ticket_text"])

    response = llm.invoke(prompt)
    drafted_response = response.content.strip()

    elapsed_ms = int((time.time() - start_time) * 1000)

    usage = response.response_metadata.get("token_usage", {})

    state["drafted_response"] = drafted_response
    state["input_tokens"] = (state.get("input_tokens") or 0) + usage.get("prompt_tokens", 0)
    state["output_tokens"] = (state.get("output_tokens") or 0) + usage.get("completion_tokens", 0)
    state["llm_latency_ms"] = (state.get("llm_latency_ms") or 0) + elapsed_ms

    return state