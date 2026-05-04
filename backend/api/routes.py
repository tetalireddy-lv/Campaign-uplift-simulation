"""FastAPI route definitions for Campaign Readiness Copilot."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from backend.models.schemas import (
    ApproveAssumptionsRequest,
    ApproveResponse,
    AmbiguityResponse,
    PlanResponse,
    QAHandoffResponse,
    ReadinessResponse,
    SessionResponse,
    StartRequest,
    StartResponse,
)
from backend.services import session as session_store
from backend.services import workflow_service as wf

router = APIRouter()


# ── GET /api/config/status ───────────────────────────────────────────────────

@router.get("/config/status")
async def config_status():
    """Returns current LLM configuration so the frontend can show live vs mock mode."""
    key = os.getenv("AZURE_OPENAI_API_KEY", "")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    placeholder = "your-azure-openai-api-key-here"
    live = bool(key and key != placeholder and endpoint and deployment)
    return {
        "llm_mode": "live" if live else "mock",
        "openai_key_configured": live,
        "model": deployment or "(not set)",
        "provider": "azure",
        "endpoint": endpoint or "(not set)",
    }


# ── GET /api/workflow/{session_id} ──────────────────────────────────────────

@router.get("/workflow/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(session_id=session_id, status=s["status"], data=s)


# ── POST /api/workflow/start ─────────────────────────────────────────────────

@router.post("/workflow/start", response_model=StartResponse)
async def start_workflow(body: StartRequest):
    if not body.raw_brief.strip():
        raise HTTPException(status_code=422, detail="raw_brief cannot be empty")

    session = session_store.create_session(body.raw_brief)
    session_id = session["session_id"]

    # run_parse_brief runs brief_parser + classify_intent concurrently
    result = await wf.run_parse_brief(body.raw_brief)

    session_store.update_session(session_id, {
        "structured_brief": result["structured_brief"],
        "campaign_intent": result["campaign_intent"],
        "status": "BRIEF_PARSED",
    })
    session_store.append_audit(session_id, "parse_brief", "completed")

    return StartResponse(
        session_id=session_id,
        status="BRIEF_PARSED",
        structured_brief=result["structured_brief"],
        campaign_intent=result["campaign_intent"],
    )


# ── POST /api/workflow/{session_id}/validate-readiness ───────────────────────

@router.post("/workflow/{session_id}/validate-readiness", response_model=ReadinessResponse)
async def validate_readiness(session_id: str):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if not s.get("structured_brief"):
        raise HTTPException(status_code=400, detail="Brief not parsed yet — call /start first")

    # gap_detector, compliance_risk_review, kpi_measurement_review run concurrently
    result = await wf.run_validate_readiness(s["structured_brief"])

    session_store.update_session(session_id, {
        **result,
        "status": "READINESS_VALIDATED",
    })
    session_store.append_audit(session_id, "validate_readiness", "completed", readiness_score=result["readiness_score"])

    return ReadinessResponse(
        session_id=session_id,
        status="READINESS_VALIDATED",
        **result,
    )


# ── POST /api/workflow/{session_id}/resolve-ambiguity ────────────────────────

@router.post("/workflow/{session_id}/resolve-ambiguity", response_model=AmbiguityResponse)
async def resolve_ambiguity(session_id: str):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if not s.get("gap_report"):
        raise HTTPException(status_code=400, detail="Readiness not validated yet")

    # Sequential: assumption_register depends on clarification_questions output
    result = await wf.run_resolve_ambiguity(
        s["structured_brief"],
        s["gap_report"],
        s["compliance_report"],
        s["kpi_report"],
    )

    session_store.update_session(session_id, {
        **result,
        "status": "AWAITING_MANAGER_APPROVAL",
    })
    session_store.append_audit(session_id, "resolve_ambiguity", "completed")

    return AmbiguityResponse(
        session_id=session_id,
        status="AWAITING_MANAGER_APPROVAL",
        **result,
    )


# ── POST /api/workflow/{session_id}/approve-assumptions ─────────────────────

@router.post("/workflow/{session_id}/approve-assumptions", response_model=ApproveResponse)
async def approve_assumptions(session_id: str, body: ApproveAssumptionsRequest):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    session_store.update_session(session_id, {
        "approved_assumptions": body.approved_assumptions,
        "manager_answers": body.manager_answers,
        "status": "ASSUMPTIONS_APPROVED",
    })
    session_store.append_audit(session_id, "approve_assumptions", "completed", count=len(body.approved_assumptions))

    return ApproveResponse(
        session_id=session_id,
        status="ASSUMPTIONS_APPROVED",
        approved_count=len(body.approved_assumptions),
    )


# ── POST /api/workflow/{session_id}/plan-and-simulate ───────────────────────

@router.post("/workflow/{session_id}/plan-and-simulate", response_model=PlanResponse)
async def plan_and_simulate(session_id: str):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if not s.get("structured_brief"):
        raise HTTPException(status_code=400, detail="Session not ready for planning")

    # orch → channel → plan (sequential), then asset/timeline/measurement (parallel),
    # then simulate_uplift (sequential after measurement_plan)
    result = await wf.run_plan_and_simulate(
        s["structured_brief"],
        s.get("gap_report", {}),
        s.get("approved_assumptions", []),
        s.get("manager_answers", {}),
    )

    session_store.update_session(session_id, {
        **result,
        "status": "PLAN_GENERATED",
    })
    session_store.append_audit(session_id, "plan_and_simulate", "completed")

    return PlanResponse(
        session_id=session_id,
        status="PLAN_GENERATED",
        **result,
    )


# ── POST /api/workflow/{session_id}/qa-and-handoff ──────────────────────────

@router.post("/workflow/{session_id}/qa-and-handoff", response_model=QAHandoffResponse)
async def qa_and_handoff(session_id: str):
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if not s.get("execution_plan"):
        raise HTTPException(status_code=400, detail="Plan not generated yet")

    # brief_to_plan_qa, multi_channel_consistency, final_compliance_review run concurrently,
    # then generate_handoff_packet runs after all three complete
    result = await wf.run_qa_and_handoff(
        s["structured_brief"],
        s["execution_plan"],
        s["channel_strategy"],
        s.get("compliance_report", {}),
        s.get("simulation_report", {}),
        s.get("approved_assumptions", []),
    )

    session_store.update_session(session_id, {
        **result,
        "status": "READY_FOR_REVIEW",
    })
    session_store.append_audit(session_id, "qa_and_handoff", "completed")

    return QAHandoffResponse(
        session_id=session_id,
        status="READY_FOR_REVIEW",
        **result,
    )
