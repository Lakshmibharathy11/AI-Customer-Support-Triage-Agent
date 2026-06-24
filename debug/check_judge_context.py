from src.agent.nodes.retrieve_node import retrieve_node
from src.agent.nodes.draft_node import draft_node
from src.agent.nodes.eval_node import build_judge_context

state = {
    "ticket_id": "DEBUG-001",
    "ticket_text": "I forgot my password and the reset email isn't arriving.",
    "tier": "Gold",
}
state = retrieve_node(state)
state = draft_node(state)

context = build_judge_context(state)
print("=== CONTEXT GIVEN TO JUDGE ===")
print(context)
print()
print("=== DRAFTED RESPONSE ===")
print(state["drafted_response"])