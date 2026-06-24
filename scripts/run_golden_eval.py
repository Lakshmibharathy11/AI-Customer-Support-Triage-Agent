# scripts/run_golden_eval.py

import json
import uuid
from pathlib import Path

from langgraph.types import Command

from src.agent.graph import agent_graph
from tests.golden_dataset import GOLDEN_TICKETS


def run_ticket(ticket: dict) -> dict:
    """
    Runs a single golden ticket through the full agent graph.
    Auto-approves any HITL interrupt (offline eval doesn't have
    a live human — we assume the draft is acceptable to proceed,
    since we're measuring RETRIEVAL/GENERATION quality here, not
    HITL behavior itself).
    """
    thread_id = f"golden-{ticket['ticket_id']}-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    state = {
        "ticket_id": ticket["ticket_id"],
        "ticket_text": ticket["ticket_text"],
        "tier": ticket["tier"],
    }

    result = agent_graph.invoke(state, config=config)

    # If the graph paused for HITL, auto-approve to let it finish
    if "__interrupt__" in result:
        result = agent_graph.invoke(
            Command(resume={"decision": "approved", "notes": "auto-approved for offline eval"}),
            config=config,
        )

    retrieved_parents = result.get("retrieved_parents") or []
    contexts = [p["text"] for p in retrieved_parents]

    # If no parents were retrieved (tier-restricted or no-match path),
    # fall back to whatever grounding context actually existed
    if not contexts:
        tier_restricted = result.get("tier_restricted_match")
        if tier_restricted:
            contexts = [tier_restricted["text"]]
        else:
            contexts = ["(no relevant context found)"]

    return {
        "ticket_id": ticket["ticket_id"],
        "question": ticket["ticket_text"],
        "answer": result.get("final_response") or result.get("drafted_response") or "",
        "contexts": contexts,
        "ground_truth": ticket["ground_truth_answer"],
        "expected_category": ticket["expected_category"],
        "actual_category": result.get("category"),
        "expected_outcome": ticket["expected_outcome"],
        "actual_outcome": result.get("outcome"),
        "faithfulness_score": result.get("faithfulness_score"),
        "relevance_score": result.get("relevance_score"),
    }


def main():
    results = []

    for i, ticket in enumerate(GOLDEN_TICKETS, 1):
        print(f"[{i}/{len(GOLDEN_TICKETS)}] Running {ticket['ticket_id']}...")
        try:
            result = run_ticket(ticket)
            results.append(result)
        except Exception as e:
            print(f"  ERROR on {ticket['ticket_id']}: {e}")
            results.append({
                "ticket_id": ticket["ticket_id"],
                "question": ticket["ticket_text"],
                "answer": "",
                "contexts": ["(error during run)"],
                "ground_truth": ticket["ground_truth_answer"],
                "error": str(e),
            })

    output_dir = Path("eval_results")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "golden_run_results.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nDone. {len(results)} tickets processed.")
    print(f"Results saved to {output_path}")

    # Quick classification accuracy check
    correct_category = sum(
        1 for r in results
        if r.get("actual_category") == r.get("expected_category")
    )
    correct_outcome = sum(
        1 for r in results
        if r.get("actual_outcome") == r.get("expected_outcome")
    )
    print(f"\nCategory accuracy: {correct_category}/{len(results)}")
    print(f"Outcome accuracy: {correct_outcome}/{len(results)}")


if __name__ == "__main__":
    main()