# src/agent/graph.py

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.agent.state import AgentState
from src.agent.nodes.classify_node import classify_node
from src.agent.nodes.tier_lookup_node import tier_lookup_node
from src.agent.nodes.retrieve_node import retrieve_node
from src.agent.nodes.draft_node import draft_node
from src.agent.nodes.eval_node import eval_node
from src.agent.nodes.hitl_node import hitl_node
from src.agent.nodes.resolution_router import resolution_router
from src.agent.nodes.sla_node import sla_node
from src.agent.nodes.escalation_node import escalation_node
from src.agent.nodes.log_node import log_node
from src.config.tier_matrix import needs_hitl


def route_after_eval(state: AgentState) -> str:
    """
    Conditional edge after eval_node: decides whether this ticket
    needs human review based on category, priority, and the real
    faithfulness score now available.
    """
    hitl_needed = needs_hitl(
        category=state["category"],
        priority=state["priority"],
        faithfulness=state["faithfulness_score"],
    )
    return "hitl_node" if hitl_needed else "resolution_router"


def route_after_resolution(state: AgentState) -> str:
    """
    Conditional edge after resolution_router: escalated tickets
    fire a Slack alert, resolved tickets skip straight to logging.
    """
    return "escalation_node" if state["outcome"] == "escalated" else "sla_node"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_node", classify_node)
    graph.add_node("tier_lookup_node", tier_lookup_node)
    graph.add_node("retrieve_node", retrieve_node)
    graph.add_node("draft_node", draft_node)
    graph.add_node("eval_node", eval_node)
    graph.add_node("hitl_node", hitl_node)
    graph.add_node("resolution_router", resolution_router)
    graph.add_node("sla_node", sla_node)
    graph.add_node("escalation_node", escalation_node)
    graph.add_node("log_node", log_node)

    graph.set_entry_point("classify_node")
    graph.add_edge("classify_node", "tier_lookup_node")
    graph.add_edge("tier_lookup_node", "retrieve_node")
    graph.add_edge("retrieve_node", "draft_node")
    graph.add_edge("draft_node", "eval_node")

    graph.add_conditional_edges(
        "eval_node",
        route_after_eval,
        {
            "hitl_node": "hitl_node",
            "resolution_router": "resolution_router",
        },
    )

    # After HITL resolves (approved or rejected), still run through
    # resolution_router — a HITL-rejected draft must be escalated,
    # and resolution_router already encodes that exact rule
    graph.add_edge("hitl_node", "resolution_router")

    graph.add_conditional_edges(
        "resolution_router",
        route_after_resolution,
        {
            "escalation_node": "escalation_node",
            "sla_node": "sla_node",
        },
    )

    # Escalated tickets still need SLA deadlines tracked
    graph.add_edge("escalation_node", "sla_node")
    graph.add_edge("sla_node", "log_node")
    graph.add_edge("log_node", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


agent_graph = build_graph()