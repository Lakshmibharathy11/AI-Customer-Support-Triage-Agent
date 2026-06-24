from langgraph.types import Command
from src.agent.graph import agent_graph

print("=" * 60)
print("SCENARIO 1: Auto-resolvable (password reset)")
print("=" * 60)
config1 = {"configurable": {"thread_id": "full-test-1"}}
state1 = {
    "ticket_id": "TKT-FULL-001",
    "ticket_text": "How do I reset my password?",
    "tier": "Gold",
}
result1 = agent_graph.invoke(state1, config=config1)
print("Outcome:", result1.get("outcome"))
print("Auto resolved:", result1.get("auto_resolved"))
print("Cost USD:", result1.get("cost_usd"))
print()

print("=" * 60)
print("SCENARIO 2: Engineering bug (should escalate, no HITL)")
print("=" * 60)
config2 = {"configurable": {"thread_id": "full-test-2"}}
state2 = {
    "ticket_id": "TKT-FULL-002",
    "ticket_text": "Our PDF export has been failing for the past hour, getting a 500 error.",
    "tier": "Diamond",
}
result2 = agent_graph.invoke(state2, config=config2)
print("Outcome:", result2.get("outcome"))
print("Escalation target:", result2.get("escalation_target"))
print("HITL required:", result2.get("hitl_required"))
print()

print("=" * 60)
print("SCENARIO 3: Cancellation risk (HITL pause + resume + escalate)")
print("=" * 60)
config3 = {"configurable": {"thread_id": "full-test-3"}}
state3 = {
    "ticket_id": "TKT-FULL-003",
    "ticket_text": "This is too expensive, I want to cancel my account.",
    "tier": "Platinum",
}
result3 = agent_graph.invoke(state3, config=config3)
print("Paused. Next node:", agent_graph.get_state(config3).next)

final3 = agent_graph.invoke(
    Command(resume={"decision": "approved", "notes": "retention message looks good"}),
    config=config3,
)
print("Final outcome:", final3.get("outcome"))
print("HITL decision:", final3.get("hitl_decision"))
print("Escalation target:", final3.get("escalation_target"))