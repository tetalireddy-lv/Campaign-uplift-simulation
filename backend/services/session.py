"""In-memory session storage for Campaign Readiness Copilot."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

# In-memory store: session_id -> session_state
_sessions: dict[str, dict[str, Any]] = {}


def create_session(raw_brief: str) -> dict[str, Any]:
    session_id = str(uuid.uuid4())
    session: dict[str, Any] = {
        "session_id": session_id,
        "raw_brief": raw_brief,
        "structured_brief": None,
        "campaign_intent": None,
        "gap_report": None,
        "compliance_report": None,
        "kpi_report": None,
        "readiness_score": None,
        "clarification_questions": None,
        "assumptions": None,
        "approved_assumptions": [],
        "manager_answers": {},
        "channel_strategy": None,
        "execution_plan": None,
        "asset_checklist": None,
        "timeline_plan": None,
        "measurement_plan": None,
        "simulation_report": None,
        "qa_report": None,
        "consistency_report": None,
        "final_compliance_report": None,
        "handoff_packet": None,
        "status": "STARTED",
        "audit_trail": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": "session_created",
                "status": "completed",
            }
        ],
    }
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> dict[str, Any] | None:
    return _sessions.get(session_id)


def update_session(session_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    if session_id not in _sessions:
        return None
    _sessions[session_id].update(updates)
    return _sessions[session_id]


def append_audit(session_id: str, step: str, status: str, **extra) -> None:
    if session_id not in _sessions:
        return
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "status": status,
        **extra,
    }
    _sessions[session_id].setdefault("audit_trail", []).append(entry)
