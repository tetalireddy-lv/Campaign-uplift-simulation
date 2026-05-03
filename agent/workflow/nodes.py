"""LangGraph workflow nodes for Campaign Readiness Copilot."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from agent.tools.campaign_uplift_simulator_tool import simulate_uplift
from agent.tools.kpi_measurement_plan_tool import generate_measurement_plan
from agent.tools.stakeholder_handoff_packet_tool import generate_handoff_packet

from .llm_utils import call_llm_json
from .prompt_renderer import render_prompt
from .state import CampaignReadinessState


def parse_brief_node(state: CampaignReadinessState) -> dict:
    """Stage 1: Parse raw brief into structured format."""
    prompt = render_prompt(
        "parse_brief/brief_parser.j2",
        raw_brief=state["raw_brief"],
    )
    structured_brief = call_llm_json(prompt)

    # Classify intent
    intent_prompt = render_prompt(
        "classify_intent/classify_campaign_intent.j2",
        raw_brief=state["raw_brief"],
    )
    campaign_intent = call_llm_json(intent_prompt)

    return {
        "structured_brief": structured_brief,
        "campaign_intent": campaign_intent,
        "current_step": "BRIEF_PARSED",
        "audit_trail": state.get("audit_trail", [])
        + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "parse_brief",
                "status": "completed",
            }
        ],
    }


def validate_readiness_node(state: CampaignReadinessState) -> dict:
    """Stage 2: Validate brief readiness — gaps, compliance, KPIs."""
    structured_brief = state["structured_brief"]

    # Gap detection
    gap_prompt = render_prompt(
        "readiness/gap_detector.j2",
        structured_brief=structured_brief,
    )
    gap_report = call_llm_json(gap_prompt)

    # Compliance review
    compliance_prompt = render_prompt(
        "readiness/compliance_risk_review.j2",
        structured_brief=structured_brief,
    )
    compliance_report = call_llm_json(compliance_prompt)

    # KPI review
    kpi_prompt = render_prompt(
        "readiness/kpi_measurement_review.j2",
        structured_brief=structured_brief,
    )
    kpi_report = call_llm_json(kpi_prompt)

    readiness_score = gap_report.get("readiness_score", 0)

    return {
        "gap_report": gap_report,
        "compliance_report": compliance_report,
        "kpi_report": kpi_report,
        "readiness_score": readiness_score,
        "current_step": "READINESS_VALIDATED",
        "audit_trail": state.get("audit_trail", [])
        + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "validate_readiness",
                "status": "completed",
                "readiness_score": readiness_score,
            }
        ],
    }


def resolve_ambiguity_node(state: CampaignReadinessState) -> dict:
    """Stage 3: Generate clarification questions and assumptions."""
    # Clarification questions
    q_prompt = render_prompt(
        "ambiguity/clarification_questions.j2",
        structured_brief=state["structured_brief"],
        gap_report=state["gap_report"],
        compliance_report=state["compliance_report"],
        kpi_report=state["kpi_report"],
    )
    questions_result = call_llm_json(q_prompt)

    # Assumption register
    a_prompt = render_prompt(
        "ambiguity/assumption_register.j2",
        structured_brief=state["structured_brief"],
        gap_report=state["gap_report"],
        clarification_questions=questions_result.get("questions", []),
    )
    assumptions_result = call_llm_json(a_prompt)

    return {
        "clarification_questions": questions_result.get("questions", []),
        "assumptions": assumptions_result.get("assumptions", []),
        "current_step": "AWAITING_MANAGER_APPROVAL",
        "audit_trail": state.get("audit_trail", [])
        + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "resolve_ambiguity",
                "status": "completed",
                "questions_count": len(questions_result.get("questions", [])),
                "assumptions_count": len(assumptions_result.get("assumptions", [])),
            }
        ],
    }


def await_manager_approval_node(state: CampaignReadinessState) -> dict:
    """Stage 4: Human-in-the-loop approval checkpoint.

    In production, this node pauses the workflow and waits for manager input.
    The state at this point contains clarification_questions and assumptions
    that need manager review.
    """
    # This is a passthrough in automated mode.
    # In production, LangGraph's interrupt mechanism pauses here.
    return {
        "current_step": "AWAITING_MANAGER_APPROVAL",
    }


def generate_plan_node(state: CampaignReadinessState) -> dict:
    """Stage 5: Generate execution plan, channel strategy, and simulate uplift."""
    structured_brief = state["structured_brief"]
    manager_answers = state.get("manager_answers", {})
    approved_assumptions = state.get("approved_assumptions", [])

    # Orchestration plan
    orch_prompt = render_prompt(
        "planning/campaign_orchestrator_plan.j2",
        structured_brief=structured_brief,
        manager_answers=manager_answers,
        approved_assumptions=approved_assumptions,
    )
    orchestration_plan = call_llm_json(orch_prompt)

    # Channel strategy
    channel_prompt = render_prompt(
        "planning/channel_strategy.j2",
        structured_brief=structured_brief,
        orchestration_plan=orchestration_plan,
    )
    channel_strategy = call_llm_json(channel_prompt)

    # Execution plan
    exec_prompt = render_prompt(
        "planning/execution_plan_generator.j2",
        structured_brief=structured_brief,
        channel_strategy=channel_strategy,
    )
    execution_plan = call_llm_json(exec_prompt)

    # Asset checklist
    asset_prompt = render_prompt(
        "planning/asset_checklist.j2",
        channel_strategy=channel_strategy,
        execution_plan=execution_plan,
    )
    asset_checklist = call_llm_json(asset_prompt)

    # Timeline workback
    timeline_prompt = render_prompt(
        "planning/timeline_workback.j2",
        structured_brief=structured_brief,
        execution_plan=execution_plan,
    )
    timeline_plan = call_llm_json(timeline_prompt)

    measurement_plan = generate_measurement_plan(
        structured_brief=structured_brief,
        execution_plan=execution_plan,
        channel_strategy=channel_strategy,
    )

    simulation_report = simulate_uplift(
        structured_brief=structured_brief,
        execution_plan=execution_plan,
        gap_report=state["gap_report"],
        approved_assumptions=approved_assumptions,
        measurement_plan=measurement_plan,
        campaign_id=structured_brief.get("campaign_id"),
    )

    return {
        "channel_strategy": channel_strategy,
        "execution_plan": execution_plan,
        "asset_checklist": asset_checklist,
        "timeline_plan": timeline_plan,
        "measurement_plan": measurement_plan,
        "simulation_report": simulation_report,
        "current_step": "PLAN_GENERATED",
        "audit_trail": state.get("audit_trail", [])
        + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "generate_plan",
                "status": "completed",
            }
        ],
    }


def qa_and_handoff_node(state: CampaignReadinessState) -> dict:
    """Stage 6: QA validation and handoff packet generation."""
    # Brief-to-plan QA
    qa_prompt = render_prompt(
        "qa/brief_to_plan_qa.j2",
        structured_brief=state["structured_brief"],
        execution_plan=state["execution_plan"],
        approved_assumptions=state.get("approved_assumptions", []),
    )
    qa_report = call_llm_json(qa_prompt)

    # Multi-channel consistency
    consistency_prompt = render_prompt(
        "qa/multi_channel_consistency.j2",
        channel_strategy=state["channel_strategy"],
        execution_plan=state["execution_plan"],
    )
    consistency_report = call_llm_json(consistency_prompt)

    # Final compliance review
    compliance_prompt = render_prompt(
        "qa/final_compliance_review.j2",
        execution_plan=state["execution_plan"],
        channel_strategy=state["channel_strategy"],
        compliance_report=state["compliance_report"],
    )
    final_compliance_report = call_llm_json(compliance_prompt)

    handoff_packet = generate_handoff_packet(
        structured_brief=state["structured_brief"],
        execution_plan=state["execution_plan"],
        channel_strategy=state["channel_strategy"],
        simulation_report=state["simulation_report"],
        qa_report=qa_report,
        final_compliance_report=final_compliance_report,
        approved_assumptions=state.get("approved_assumptions", []),
    )

    return {
        "qa_report": qa_report,
        "consistency_report": consistency_report,
        "final_compliance_report": final_compliance_report,
        "handoff_packet": handoff_packet,
        "current_step": "READY_FOR_REVIEW",
        "audit_trail": state.get("audit_trail", [])
        + [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "qa_and_handoff",
                "status": "completed",
                "alignment_score": qa_report.get("alignment_score", 0),
            }
        ],
    }


def final_approval_node(state: CampaignReadinessState) -> dict:
    """Stage 7: Final manager approval checkpoint.

    In production, this pauses for manager signoff.
    """
    return {
        "current_step": "AWAITING_FINAL_APPROVAL",
    }
