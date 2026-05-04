"""Workflow service — calls LLM tools when Azure credentials are set, falls back to mock otherwise."""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agent.workflow.prompt_renderer import render_prompt
from agent.tools.campaign_uplift_simulator_tool import simulate_uplift
from agent.tools.kpi_measurement_plan_tool import generate_measurement_plan
from agent.tools.stakeholder_handoff_packet_tool import generate_handoff_packet
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

log = logging.getLogger(__name__)


def _llm_available() -> bool:
    key = os.getenv("AZURE_OPENAI_API_KEY", "")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    return bool(key and key != "your-azure-openai-api-key-here" and endpoint and deployment)


def _call_llm(prompt: str) -> dict:
    from agent.workflow.llm_utils import call_llm_json
    return call_llm_json(prompt)


def _call_with_fallback(prompt: str, fallback: dict, label: str) -> dict:
    if not _llm_available():
        log.debug("[mock] %s — no Azure credentials", label)
        return {**fallback, "_source": "mock"}
    try:
        result = _call_llm(prompt)
        if not isinstance(result, dict):
            return {**fallback, "_source": "mock"}
        log.info("[llm] %s — success", label)
        return result
    except Exception as exc:
        log.error("[fallback] %s failed: %s — using mock", label, exc)
        return {**fallback, "_source": "mock"}


async def _async_call(prompt: str, fallback: dict, label: str) -> dict:
    try:
        return await asyncio.to_thread(_call_with_fallback, prompt, fallback, label)
    except Exception as exc:
        log.error("[async-fallback] %s raised unexpectedly: %s", label, exc)
        return {**fallback, "_source": "mock"}


# ── Step 1 — Parse Brief ─────────────────────────────────────────────────────

async def run_parse_brief(raw_brief: str) -> dict:
    t0 = time.perf_counter()
    structured, intent = await asyncio.gather(
        _async_call(
            render_prompt("parse_brief/brief_parser.j2", raw_brief=raw_brief),
            fallback=MOCK_STRUCTURED_BRIEF,
            label="brief_parser",
        ),
        _async_call(
            render_prompt("classify_intent/classify_campaign_intent.j2", raw_brief=raw_brief),
            fallback=MOCK_CAMPAIGN_INTENT,
            label="classify_intent",
        ),
    )
    log.info("[timing] run_parse_brief %.2fs", time.perf_counter() - t0)
    return {"structured_brief": structured, "campaign_intent": intent}


# ── Step 2 — Validate Readiness ──────────────────────────────────────────────

async def run_validate_readiness(structured_brief: dict) -> dict:
    t0 = time.perf_counter()
    gap, compliance, kpi = await asyncio.gather(
        _async_call(
            render_prompt("readiness/gap_detector.j2", structured_brief=structured_brief),
            fallback=MOCK_GAP_REPORT,
            label="gap_detector",
        ),
        _async_call(
            render_prompt("readiness/compliance_risk_review.j2", structured_brief=structured_brief),
            fallback=MOCK_COMPLIANCE_REPORT,
            label="compliance_risk_review",
        ),
        _async_call(
            render_prompt("readiness/kpi_measurement_review.j2", structured_brief=structured_brief),
            fallback=MOCK_KPI_REPORT,
            label="kpi_measurement_review",
        ),
    )
    log.info("[timing] run_validate_readiness %.2fs", time.perf_counter() - t0)
    return {
        "gap_report": gap,
        "compliance_report": compliance,
        "kpi_report": kpi,
        "readiness_score": int(gap.get("readiness_score", 72)),
    }


# ── Step 3 — Resolve Ambiguity ───────────────────────────────────────────────

async def run_resolve_ambiguity(
    structured_brief: dict,
    gap_report: dict,
    compliance_report: dict,
    kpi_report: dict,
) -> dict:
    t0 = time.perf_counter()
    q_result = await _async_call(
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

    a_result = await _async_call(
        render_prompt(
            "ambiguity/assumption_register.j2",
            structured_brief=structured_brief,
            gap_report=gap_report,
            clarification_questions=questions,
        ),
        fallback={"assumptions": MOCK_ASSUMPTIONS},
        label="assumption_register",
    )
    log.info("[timing] run_resolve_ambiguity %.2fs", time.perf_counter() - t0)
    return {
        "clarification_questions": questions,
        "assumptions": a_result.get("assumptions", MOCK_ASSUMPTIONS),
    }


# ── Step 4 — Plan and Simulate ───────────────────────────────────────────────

async def run_plan_and_simulate(
    structured_brief: dict,
    gap_report: dict,
    approved_assumptions: list,
    manager_answers: dict,
) -> dict:
    t0 = time.perf_counter()

    # Stage 1: channel strategy (incorporates orchestration context directly)
    channel = await _async_call(
        render_prompt(
            "planning/channel_strategy.j2",
            structured_brief=structured_brief,
            manager_answers=manager_answers,
            approved_assumptions=approved_assumptions,
        ),
        fallback=MOCK_CHANNEL_STRATEGY,
        label="channel_strategy",
    )

    # Stage 2: execution plan depends on channel
    plan = await _async_call(
        render_prompt(
            "planning/execution_plan_generator.j2",
            structured_brief=structured_brief,
            channel_strategy=channel,
        ),
        fallback=MOCK_EXECUTION_PLAN,
        label="execution_plan_generator",
    )

    # Stage 3: asset checklist, timeline, and measurement plan are all independent
    assets, timeline, measurement_plan = await asyncio.gather(
        _async_call(
            render_prompt(
                "planning/asset_checklist.j2",
                channel_strategy=channel,
                execution_plan=plan,
            ),
            fallback={"assets": [], "checklist": []},
            label="asset_checklist",
        ),
        _async_call(
            render_prompt(
                "planning/timeline_workback.j2",
                structured_brief=structured_brief,
                execution_plan=plan,
            ),
            fallback={"milestones": [], "workback_schedule": []},
            label="timeline_workback",
        ),
        asyncio.to_thread(generate_measurement_plan, structured_brief, plan, channel),
    )

    # Stage 4: simulation depends on measurement_plan
    try:
        simulation = await asyncio.to_thread(
            simulate_uplift,
            structured_brief,
            plan,
            gap_report,
            approved_assumptions,
            measurement_plan,
            structured_brief.get("campaign_id"),
        )
    except Exception as exc:
        log.error("[fallback] simulate_uplift failed: %s — using mock", exc)
        simulation = {**MOCK_SIMULATION_REPORT, "_source": "mock"}

    log.info("[timing] run_plan_and_simulate %.2fs", time.perf_counter() - t0)
    return {
        "channel_strategy": channel,
        "execution_plan": plan,
        "asset_checklist": assets,
        "timeline_plan": timeline,
        "measurement_plan": measurement_plan,
        "simulation_report": simulation,
    }


# ── Step 5 — QA and Handoff ──────────────────────────────────────────────────

async def run_qa_and_handoff(
    structured_brief: dict,
    execution_plan: dict,
    channel_strategy: dict,
    compliance_report: dict,
    simulation_report: dict,
    approved_assumptions: list,
) -> dict:
    t0 = time.perf_counter()

    qa, consistency, final_compliance = await asyncio.gather(
        _async_call(
            render_prompt(
                "qa/brief_to_plan_qa.j2",
                structured_brief=structured_brief,
                execution_plan=execution_plan,
                approved_assumptions=approved_assumptions,
            ),
            fallback=MOCK_QA_REPORT,
            label="brief_to_plan_qa",
        ),
        _async_call(
            render_prompt(
                "qa/multi_channel_consistency.j2",
                channel_strategy=channel_strategy,
                execution_plan=execution_plan,
            ),
            fallback={"consistency_score": 92, "summary": "Consistent across channels"},
            label="multi_channel_consistency",
        ),
        _async_call(
            render_prompt(
                "qa/final_compliance_review.j2",
                execution_plan=execution_plan,
                channel_strategy=channel_strategy,
                compliance_report=compliance_report,
            ),
            fallback={"status": "Approved with notes", "notes": []},
            label="final_compliance_review",
        ),
    )

    try:
        handoff = await asyncio.to_thread(
            generate_handoff_packet,
            structured_brief,
            execution_plan,
            channel_strategy,
            simulation_report,
            qa,
            final_compliance,
            approved_assumptions,
        )
    except Exception as exc:
        log.error("[fallback] generate_handoff_packet failed: %s — using mock", exc)
        handoff = {**MOCK_HANDOFF_PACKET, "_source": "mock"}

    log.info("[timing] run_qa_and_handoff %.2fs", time.perf_counter() - t0)
    return {
        "qa_report": qa,
        "consistency_report": consistency,
        "final_compliance_report": final_compliance,
        "handoff_packet": handoff,
    }
