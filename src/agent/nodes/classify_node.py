# src/agent/nodes/classify_node.py

import json
import time

from langchain_groq import ChatGroq

from src.config.settings import settings
from src.agent.state import AgentState


VALID_CATEGORIES = [
    "password_reset",
    "how_to_question",
    "account_info_request",
    "billing_question",
    "feature_request",
    "export_bug",
    "login_crash",
    "integration_failure",
    "billing_dispute",
    "cancellation_risk",
]

VALID_PRIORITIES = ["low", "medium", "high", "critical"]


CLASSIFY_PROMPT = """You are a support ticket classifier for Stacklytics,
a B2B product-analytics SaaS company.

Classify the following customer support ticket into exactly one category
and one priority level.

VALID CATEGORIES:
{categories}

VALID PRIORITIES:
- low: minor inconvenience, no urgency
- medium: standard issue, normal handling
- high: significant impact, customer is blocked but not losing revenue
- critical: production down, revenue impact, or imminent churn risk

TICKET:
{ticket_text}

Respond with ONLY valid JSON, no other text, no markdown formatting:
{{"category": "<one of the valid categories>", "priority": "<one of the valid priorities>", "reasoning": "<one sentence explanation>"}}
"""


def classify_node(state: AgentState) -> AgentState:
    """
    Calls the main LLM to classify the ticket into a category
    and initial priority level. Pure LLM judgment — no business
    rules here (those come later in tier_lookup_node).
    """
    start_time = time.time()

    llm = ChatGroq(
        model=settings.MAIN_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.0,  # deterministic classification, no creativity needed
    )

    prompt = CLASSIFY_PROMPT.format(
        categories="\n".join(f"- {c}" for c in VALID_CATEGORIES),
        ticket_text=state["ticket_text"],
    )

    response = llm.invoke(prompt)
    raw_output = response.content.strip()

    # Strip markdown code fences if the model added them anyway
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`").replace("json", "", 1).strip()

    try:
        parsed = json.loads(raw_output)
        category = parsed.get("category", "how_to_question")
        priority = parsed.get("priority", "medium")
    except (json.JSONDecodeError, AttributeError):
        # Fail safe: if the LLM returns malformed JSON, default to
        # a safe middle-ground classification rather than crashing
        category = "how_to_question"
        priority = "medium"

    # Guard against the LLM inventing categories/priorities not in our list
    if category not in VALID_CATEGORIES:
        category = "how_to_question"
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    elapsed_ms = int((time.time() - start_time) * 1000)

    state["category"] = category
    state["initial_priority"] = priority
    state["llm_latency_ms"] = elapsed_ms

    # Token usage from the response metadata (Groq returns this)
    usage = response.response_metadata.get("token_usage", {})
    state["input_tokens"] = usage.get("prompt_tokens", 0)
    state["output_tokens"] = usage.get("completion_tokens", 0)

    return state