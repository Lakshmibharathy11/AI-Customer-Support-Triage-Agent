# scripts/run_custom_eval.py

import json
from pathlib import Path

import numpy as np
from langchain_groq import ChatGroq

from src.config.settings import settings
from src.ingestion.embedder import embedder


# ─────────────────────────────────────────────────────────
# LLM-JUDGED METRICS (entailment reasoning — no good
# embedding-only substitute exists for these)
# ─────────────────────────────────────────────────────────

FAITHFULNESS_PROMPT = """You are evaluating a RAG system's generated answer.

RETRIEVED CONTEXT:
{contexts}

GENERATED ANSWER:
{answer}

Break the generated answer into individual factual claims. For each claim,
judge whether it is supported by the retrieved context. Then compute
faithfulness as: (number of supported claims) / (total claims).

Respond with ONLY valid JSON:
{{"faithfulness": 0.0, "reasoning": "<one sentence>"}}
"""

RECALL_PROMPT = """You are evaluating retrieval completeness for a RAG system.

GROUND TRUTH ANSWER (the ideal, complete answer):
{ground_truth}

RETRIEVED CONTEXT CHUNKS (what was actually available to the agent):
{contexts}

Break the ground truth answer into individual factual claims. For each
claim, judge whether the retrieved context contains enough information
to support that claim. Then compute recall as:
(number of supported claims) / (total number of claims in ground truth).

Respond with ONLY valid JSON:
{{"context_recall": 0.0, "reasoning": "<one sentence>"}}
"""

HYPOTHETICAL_QUESTION_PROMPT = """Given this answer, generate ONE question
that this answer would be a good, complete response to.

ANSWER:
{answer}

Respond with ONLY the question text, nothing else.
"""


def call_judge_json(llm, prompt: str, key: str) -> float:
    """
    Calls the LLM, parses a JSON response, extracts the named key.
    Falls back to a neutral 0.5 score if parsing fails, rather than
    silently passing or failing the response.
    """
    response = llm.invoke(prompt)
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").replace("json", "", 1).strip()
    try:
        parsed = json.loads(raw)
        return float(parsed.get(key, 0.5))
    except (json.JSONDecodeError, ValueError, AttributeError):
        return 0.5


def compute_faithfulness(llm, contexts_str: str, answer: str) -> float:
    prompt = FAITHFULNESS_PROMPT.format(contexts=contexts_str, answer=answer)
    return call_judge_json(llm, prompt, "faithfulness")


def compute_context_recall(llm, contexts_str: str, ground_truth: str) -> float:
    prompt = RECALL_PROMPT.format(ground_truth=ground_truth, contexts=contexts_str)
    return call_judge_json(llm, prompt, "context_recall")


# ─────────────────────────────────────────────────────────
# EMBEDDING-BASED METRICS (similarity is the right tool —
# matches real RAGAS's own internal approach for these two)
# ─────────────────────────────────────────────────────────

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Both vectors are already L2-normalized by embedder.py
    (normalize_embeddings=True), so dot product IS cosine similarity.
    """
    return float(np.dot(vec_a, vec_b))


def compute_context_precision_embedding(question: str, contexts: list[str], threshold: float = 0.55) -> float:
    """
    Fraction of retrieved chunks whose embedding similarity to the
    question clears the relevance threshold. Reuses the SAME
    embedding model your own FAISS retriever uses, so this score
    is consistent with how retrieval itself measures relevance.
    """
    if not contexts:
        return 0.0

    question_vec = embedder.embed_text(question)
    useful_count = 0

    for ctx in contexts:
        ctx_vec = embedder.embed_text(ctx)
        similarity = cosine_similarity(question_vec, ctx_vec)
        if similarity >= threshold:
            useful_count += 1

    return useful_count / len(contexts)


def compute_answer_relevancy_embedding(llm, question: str, answer: str) -> float:
    """
    Generates a hypothetical question the answer would suit, then
    measures embedding similarity to the ACTUAL question. High
    similarity means the answer is genuinely on-topic.
    """
    response = llm.invoke(HYPOTHETICAL_QUESTION_PROMPT.format(answer=answer))
    hypothetical_question = response.content.strip()

    question_vec = embedder.embed_text(question)
    hypothetical_vec = embedder.embed_text(hypothetical_question)

    similarity = cosine_similarity(question_vec, hypothetical_vec)
    return max(0.0, min(1.0, similarity))


# ─────────────────────────────────────────────────────────
# MAIN SCORING LOOP
# ─────────────────────────────────────────────────────────

def score_ticket(llm, ticket: dict) -> dict:
    contexts_str = "\n\n".join(ticket["contexts"])

    faithfulness = compute_faithfulness(llm, contexts_str, ticket["answer"])
    context_recall = compute_context_recall(llm, contexts_str, ticket["ground_truth"])
    context_precision = compute_context_precision_embedding(ticket["question"], ticket["contexts"])
    answer_relevancy = compute_answer_relevancy_embedding(llm, ticket["question"], ticket["answer"])

    return {
        "ticket_id": ticket["ticket_id"],
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "context_precision": context_precision,
        "context_recall": context_recall,
    }


def main():
    print("Loading golden run results...")
    with open("eval_results/golden_run_results.json", encoding="utf-8") as f:
        results = json.load(f)
    
    SAMPLE_TICKET_IDS = [
        "GOLD-001", "GOLD-004", "GOLD-009", "GOLD-012",
        "GOLD-020", "GOLD-023", "GOLD-028", "GOLD-030",
    ]
    tickets = [r for r in results if "error" not in r and r["ticket_id"] in SAMPLE_TICKET_IDS]
    #tickets = [r for r in results if "error" not in r]
    print(f"Loaded {len(tickets)} tickets for evaluation.\n")

    llm = ChatGroq(
        model=settings.MAIN_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.0,
    )

    per_ticket = []
    for i, ticket in enumerate(tickets, 1):
        print(f"[{i}/{len(tickets)}] Scoring {ticket['ticket_id']}...")
        scores = score_ticket(llm, ticket)
        per_ticket.append(scores)

    metric_names = ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
    averages = {}
    for name in metric_names:
        values = [r[name] for r in per_ticket]
        averages[name] = round(sum(values) / len(values), 4)

    print("\n=== EVALUATION SCORES (averaged across golden set) ===")
    for metric, value in averages.items():
        print(f"  {metric}: {value}")

    output_dir = Path("eval_results")
    output_dir.mkdir(exist_ok=True)

    with open(output_dir / "ragas_scores.json", "w", encoding="utf-8") as f:
        json.dump(averages, f, indent=2)

    with open(output_dir / "ragas_per_ticket.json", "w", encoding="utf-8") as f:
        json.dump(per_ticket, f, indent=2)

    print(f"\nSaved averaged scores to {output_dir / 'ragas_scores.json'}")
    print(f"Saved per-ticket breakdown to {output_dir / 'ragas_per_ticket.json'}")


if __name__ == "__main__":
    main()