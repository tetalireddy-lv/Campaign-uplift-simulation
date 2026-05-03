"""LangGraph workflow graph definition for Campaign Readiness Copilot."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from .nodes import (
    await_manager_approval_node,
    final_approval_node,
    generate_plan_node,
    parse_brief_node,
    qa_and_handoff_node,
    resolve_ambiguity_node,
    validate_readiness_node,
)
from .state import CampaignReadinessState


def should_skip_ambiguity(state: CampaignReadinessState) -> str:
    """Route based on readiness score — skip ambiguity if brief is high quality."""
    score = state.get("readiness_score", 0)
    if score >= 85:
        return "generate_plan"
    return "resolve_ambiguity"


def should_proceed_after_qa(state: CampaignReadinessState) -> str:
    """Route based on QA results — loop back if critical misalignments."""
    qa_report = state.get("qa_report", {})
    critical = qa_report.get("critical_misalignments", [])
    if critical:
        return "generate_plan"
    return "final_approval"


def build_campaign_graph() -> StateGraph:
    """Build and compile the Campaign Readiness workflow graph."""
    graph = StateGraph(CampaignReadinessState)

    # Add nodes
    graph.add_node("parse_brief", parse_brief_node)
    graph.add_node("validate_readiness", validate_readiness_node)
    graph.add_node("resolve_ambiguity", resolve_ambiguity_node)
    graph.add_node("await_manager_approval", await_manager_approval_node)
    graph.add_node("generate_plan", generate_plan_node)
    graph.add_node("qa_and_handoff", qa_and_handoff_node)
    graph.add_node("final_approval", final_approval_node)

    # Define edges
    graph.set_entry_point("parse_brief")
    graph.add_edge("parse_brief", "validate_readiness")

    # Conditional: skip ambiguity if brief is high quality
    graph.add_conditional_edges(
        "validate_readiness",
        should_skip_ambiguity,
        {
            "resolve_ambiguity": "resolve_ambiguity",
            "generate_plan": "generate_plan",
        },
    )

    graph.add_edge("resolve_ambiguity", "await_manager_approval")
    graph.add_edge("await_manager_approval", "generate_plan")
    graph.add_edge("generate_plan", "qa_and_handoff")

    # Conditional: loop back if QA fails
    graph.add_conditional_edges(
        "qa_and_handoff",
        should_proceed_after_qa,
        {
            "generate_plan": "generate_plan",
            "final_approval": "final_approval",
        },
    )

    graph.add_edge("final_approval", END)

    return graph


def get_compiled_graph():
    """Return the compiled workflow ready for execution."""
    graph = build_campaign_graph()
    return graph.compile()
