# src/agent/nodes/retrieve_node.py

import time

from src.retrieval.faiss_retriever import retriever
from src.agent.state import AgentState


def retrieve_node(state: AgentState) -> AgentState:
    """
    Searches the FAISS child index using the ticket text as the query,
    follows parent_id links, and returns full parent context filtered
    by the customer's tier visibility.

    If the best semantic match exists but is restricted to a higher
    tier than the customer's own, that's captured separately so
    draft_node can write a polite "this is a [tier] feature" response
    instead of either hallucinating or returning nothing.
    """
    start_time = time.time()

    result = retriever.retrieve(
        query=state["ticket_text"],
        tier=state["tier"],
    )

    elapsed_ms = int((time.time() - start_time) * 1000)

    state["retrieved_parents"] = result["parents"]
    state["chunks_retrieved"] = len(result["parents"])
    state["parent_docs_used"] = len(result["parents"])
    state["tier_restricted_match"] = result["tier_restricted_match"]
    state["retrieval_latency_ms"] = elapsed_ms

    return state