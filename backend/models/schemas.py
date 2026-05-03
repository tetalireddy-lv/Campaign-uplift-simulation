"""Pydantic request/response schemas for the Campaign Readiness Copilot API."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel


# ── Requests ────────────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    raw_brief: str


class ApproveAssumptionsRequest(BaseModel):
    approved_assumptions: list[dict[str, Any]] = []
    manager_answers: dict[str, str] = {}


# ── Responses ────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str
    status: str
    data: dict[str, Any]


class StartResponse(BaseModel):
    session_id: str
    status: str
    structured_brief: dict[str, Any]
    campaign_intent: dict[str, Any]


class ReadinessResponse(BaseModel):
    session_id: str
    status: str
    readiness_score: int
    gap_report: dict[str, Any]
    compliance_report: dict[str, Any]
    kpi_report: dict[str, Any]


class AmbiguityResponse(BaseModel):
    session_id: str
    status: str
    clarification_questions: list[dict[str, Any]]
    assumptions: list[dict[str, Any]]


class ApproveResponse(BaseModel):
    session_id: str
    status: str
    approved_count: int


class PlanResponse(BaseModel):
    session_id: str
    status: str
    channel_strategy: dict[str, Any]
    execution_plan: dict[str, Any]
    measurement_plan: dict[str, Any]
    simulation_report: dict[str, Any]
    asset_checklist: dict[str, Any]
    timeline_plan: dict[str, Any]


class QAHandoffResponse(BaseModel):
    session_id: str
    status: str
    qa_report: dict[str, Any]
    consistency_report: dict[str, Any]
    final_compliance_report: dict[str, Any]
    handoff_packet: dict[str, Any]
