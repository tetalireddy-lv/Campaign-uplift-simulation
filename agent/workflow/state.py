"""Campaign Readiness State definition for LangGraph workflow."""
from __future__ import annotations

from typing import TypedDict


class CampaignReadinessState(TypedDict, total=False):
    """Shared state carried across all workflow nodes."""

    session_id: str

    # Stage 1: Brief Parsing
    raw_brief: str
    structured_brief: dict

    # Intent Classification
    campaign_intent: dict
    planner_steps: list

    # Stage 2: Readiness Validation
    gap_report: dict
    compliance_report: dict
    kpi_report: dict
    readiness_score: int

    # Stage 3: Ambiguity Resolution
    clarification_questions: list
    assumptions: list

    # Stage 4: Manager Approval
    manager_answers: dict
    approved_assumptions: list

    # Stage 5: Plan Generation
    channel_strategy: dict
    execution_plan: dict
    asset_checklist: dict
    timeline_plan: dict
    measurement_plan: dict

    # Stage 5b: Simulation
    simulation_report: dict

    # Stage 6: QA
    qa_report: dict
    consistency_report: dict
    final_compliance_report: dict

    # Stage 7: Handoff
    handoff_packet: dict

    # Approval & Audit
    approval_status: str
    audit_trail: list
    current_step: str
