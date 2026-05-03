"""Workflow service — calls LLM tools when OPENAI_API_KEY is set, falls back to mock otherwise."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Allow importing from parent project
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .mock_data import (
    MOCK_ASSUMPTIONS,
    MOCK_CAMPAIGN_INTENT,
    MOCK_CHANNEL_STRATEGY,
    MOCK_CLARIFICATION_QUESTIONS,
    MOCK_COMPLIANCE_REPORT,
    MOCK_EXECUTION_PLAN,
    MOCK_GAP_REPORT,
    MOCK_HANDOFF_PACKET,
    MOCK_KPI_REPORT,
    MOCK_QA_REPORT,
    MOCK_SIMULATION_REPORT,
    MOCK_STRUCTURED_BRIEF,
)
from agent.tools.campaign_uplift_simulator_tool import simulate_uplift
from agent.tools.kpi_measurement_plan_tool import generate_measurement_plan
from agent.tools.stakeholder_handoff_packet_tool import generate_handoff_packet

log = logging.getLogger(__name__)


def _llm_available() -> bool:
    """True when all Azure OpenAI credentials are configured."""
    key = os.getenv("AZURE_OPENAI_API_KEY", "")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    placeholder = "your-azure-openai-api-key-here"
    return bool(key and key != placeholder and endpoint and deployment)


def _call_llm(prompt: str) -> dict:
    """Call the LLM and parse JSON. Raises on any failure — caller handles fallback."""
    from agent.workflow.llm_utils import call_llm_json
    return call_llm_json(prompt)


def _call_with_fallback(prompt: str, fallback: dict, label: str) -> dict:
    """
    Try the LLM call. If OPENAI_API_KEY is not set, skip and return mock.
    If the key is set but the call fails, log the error and return mock.
    """
    if not _llm_available():
        log.debug("[mock] %s — no OPENAI_API_KEY", label)
        return {**fallback, "_source": "mock"}

    try:
        result = _call_llm(prompt)
        if not isinstance(result, dict):
            log.warning("[fallback] %s returned non-dict, using mock", label)
            return {**fallback, "_source": "mock"}
        log.info("[llm] %s — success", label)
        return result
    except Exception as exc:
        log.error("[fallback] %s failed: %s — using mock", label, exc)
        return {**fallback, "_source": "mock"}


# ─────────────────────────────────────────────
# Step 1 — Parse Brief
# ─────────────────────────────────────────────

def run_parse_brief(raw_brief: str) -> dict:
    from agent.workflow.prompt_renderer import render_prompt

    structured = _call_with_fallback(
        render_prompt("parse_brief/brief_parser.j2", raw_brief=raw_brief),
        fallback=MOCK_STRUCTURED_BRIEF,
        label="brief_parser",
    )
    intent = _call_with_fallback(
        render_prompt("classify_intent/classify_campaign_intent.j2", raw_brief=raw_brief),
        fallback=MOCK_CAMPAIGN_INTENT,
        label="classify_intent",
    )
    return {"structured_brief": structured, "campaign_intent": intent}


# ─────────────────────────────────────────────
# Step 2 — Validate Readiness
# ─────────────────────────────────────────────

def run_validate_readiness(structured_brief: dict) -> dict:
    from agent.workflow.prompt_renderer import render_prompt

    gap = _call_with_fallback(
        render_prompt("readiness/gap_detector.j2", structured_brief=structured_brief),
        fallback=MOCK_GAP_REPORT,
        label="gap_detector",
    )
    compliance = _call_with_fallback(
        render_prompt("readiness/compliance_risk_review.j2", structured_brief=structured_brief),
        fallback=MOCK_COMPLIANCE_REPORT,
        label="compliance_risk_review",
    )
    kpi = _call_with_fallback(
        render_prompt("readiness/kpi_measurement_review.j2", structured_brief=structured_brief),
        fallback=MOCK_KPI_REPORT,
        label="kpi_measurement_review",
    )
    readiness_score = int(gap.get("readiness_score", 72))
    return {
        "gap_report": gap,
        "compliance_report": compliance,
        "kpi_report": kpi,
        "readiness_score": readiness_score,
    }


# ─────────────────────────────────────────────
# Step 3 — Resolve Ambiguity
# ─────────────────────────────────────────────

def run_resolve_ambiguity(
    structured_brief: dict,
    gap_report: dict,
    compliance_report: dict,
    kpi_report: dict,
) -> dict:
    from agent.workflow.prompt_renderer import render_prompt

    q_result = _call_with_fallback(
        render_prompt(
            "ambiguity/clarification_questions.j2",
            structured_brief=structured_brief,
            gap_report=gap_report,
            compliance_report=compliance_report,
            kpi_report=kpi_report,
        ),
        fallback={"questions": MOCK_CLARIFICATION_QUESTIONS},
        label="clarification_questions",
    )
    questions = q_result.get("questions", MOCK_CLARIFICATION_QUESTIONS)

    a_result = _call_with_fallback(
        render_prompt(
            "ambiguity/assumption_register.j2",
            structured_brief=structured_brief,
            gap_report=gap_report,
            clarification_questions=questions,
        ),
        fallback={"assumptions": MOCK_ASSUMPTIONS},
        label="assumption_register",
    )
    assumptions = a_result.get("assumptions", MOCK_ASSUMPTIONS)

    return {"clarification_questions": questions, "assumptions": assumptions}


# ─────────────────────────────────────────────
# Step 4 — Plan and Simulate
# ─────────────────────────────────────────────

def run_plan_and_simulate(
    structured_brief: dict,
    gap_report: dict,
    approved_assumptions: list,
    manager_answers: dict,
) -> dict:
    from agent.workflow.prompt_renderer import render_prompt

    orch = _call_with_fallback(
        render_prompt(
            "planning/campaign_orchestrator_plan.j2",
            structured_brief=structured_brief,
            manager_answers=manager_answers,
            approved_assumptions=approved_assumptions,
        ),
        fallback={},
        label="campaign_orchestrator_plan",
    )

    channel = _call_with_fallback(
        render_prompt(
            "planning/channel_strategy.j2",
            structured_brief=structured_brief,
            orchestration_plan=orch,
        ),
        fallback=MOCK_CHANNEL_STRATEGY,
        label="channel_strategy",
    )

    plan = _call_with_fallback(
        render_prompt(
            "planning/execution_plan_generator.j2",
            structured_brief=structured_brief,
            channel_strategy=channel,
        ),
        fallback=MOCK_EXECUTION_PLAN,
        label="execution_plan_generator",
    )

    assets = _call_with_fallback(
        render_prompt(
            "planning/asset_checklist.j2",
            channel_strategy=channel,
            execution_plan=plan,
        ),
        fallback={"assets": [], "checklist": []},
        label="asset_checklist",
    )

    timeline = _call_with_fallback(
        render_prompt(
            "planning/timeline_workback.j2",
            structured_brief=structured_brief,
            execution_plan=plan,
        ),
        fallback={"milestones": [], "workback_schedule": []},
        label="timeline_workback",
    )

    measurement_plan = generate_measurement_plan(
        structured_brief=structured_brief,
        execution_plan=plan,
        channel_strategy=channel,
    )

    try:
        simulation = simulate_uplift(
            structured_brief=structured_brief,
            execution_plan=plan,
            gap_report=gap_report,
            approved_assumptions=approved_assumptions,
            measurement_plan=measurement_plan,
            campaign_id=structured_brief.get("campaign_id"),
        )
    except Exception as exc:
        log.error("[fallback] market_uplift_simulator failed: %s — using mock", exc)
        simulation = {**MOCK_SIMULATION_REPORT, "_source": "mock"}

    return {
        "channel_strategy": channel,
        "execution_plan": plan,
        "asset_checklist": assets,
        "timeline_plan": timeline,
        "measurement_plan": measurement_plan,
        "simulation_report": simulation,
    }


# ─────────────────────────────────────────────
# Step 5 — QA and Handoff
# ─────────────────────────────────────────────

def run_qa_and_handoff(
    structured_brief: dict,
    execution_plan: dict,
    channel_strategy: dict,
    compliance_report: dict,
    simulation_report: dict,
    approved_assumptions: list,
) -> dict:
    from agent.workflow.prompt_renderer import render_prompt

    qa = _call_with_fallback(
        render_prompt(
            "qa/brief_to_plan_qa.j2",
            structured_brief=structured_brief,
            execution_plan=execution_plan,
            approved_assumptions=approved_assumptions,
        ),
        fallback=MOCK_QA_REPORT,
        label="brief_to_plan_qa",
    )

    consistency = _call_with_fallback(
        render_prompt(
            "qa/multi_channel_consistency.j2",
            channel_strategy=channel_strategy,
            execution_plan=execution_plan,
        ),
        fallback={"consistency_score": 92, "summary": "Consistent across channels"},
        label="multi_channel_consistency",
    )

    final_compliance = _call_with_fallback(
        render_prompt(
            "qa/final_compliance_review.j2",
            execution_plan=execution_plan,
            channel_strategy=channel_strategy,
            compliance_report=compliance_report,
        ),
        fallback={"status": "Approved with notes", "notes": []},
        label="final_compliance_review",
    )

    try:
        handoff = generate_handoff_packet(
            structured_brief=structured_brief,
            execution_plan=execution_plan,
            channel_strategy=channel_strategy,
            simulation_report=simulation_report,
            qa_report=qa,
            final_compliance_report=final_compliance,
            approved_assumptions=approved_assumptions,
        )
    except Exception as exc:
        log.error("[fallback] stakeholder_handoff_packet failed: %s — using mock", exc)
        handoff = {**MOCK_HANDOFF_PACKET, "_source": "mock"}

    return {
        "qa_report": qa,
        "consistency_report": consistency,
        "final_compliance_report": final_compliance,
        "handoff_packet": handoff,
    }
