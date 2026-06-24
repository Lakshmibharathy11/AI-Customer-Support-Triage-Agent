from src.agent.nodes.log_node import log_node
from src.observability.logger import get_connection

state = {
    "ticket_id": "TKT-LOG-TEST-001",
    "ticket_text": "How do I reset my password?",
    "tier": "Gold",
    "category": "password_reset",
    "priority": "low",
    "drafted_response": "You can reset your password from the login page.",
    "outcome": "resolved",
    "auto_resolved": True,
    "hitl_required": False,
    "faithfulness_score": 0.95,
    "relevance_score": 0.93,
    "chunks_retrieved": 2,
    "parent_docs_used": 2,
    "input_tokens": 300,
    "output_tokens": 80,
    "judge_input_tokens": 200,
    "judge_output_tokens": 40,
    "total_latency_ms": 1500,
    "retrieval_latency_ms": 60,
    "llm_latency_ms": 900,
    "first_reply_sent_at": "2026-06-22T18:00:00",
    "resolved_at": "2026-06-22T18:00:00",
}

result = log_node(state)
print("Cost USD:", result["cost_usd"])

with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = 'TKT-LOG-TEST-001'")
    row = cursor.fetchone()
    print(dict(row) if row else "No row found")