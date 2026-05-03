# Frontend Design Instructions

## Stage-Based UI

The frontend should expose the workflow as a series of stages that the manager progresses through:

1. **Brief Input** — Text input or file upload for raw campaign brief
2. **Readiness Dashboard** — Shows readiness score, gaps, risks
3. **Clarification & Assumptions** — Interactive Q&A with approve/edit/reject per item
4. **Plan Review** — Execution plan, channel strategy, timeline visualization
5. **Simulation Results** — Scenario comparison with uplift ranges
6. **QA Findings** — Alignment checks and compliance status
7. **Handoff Packet** — Final document with approval actions

## Interaction Patterns

- **Approval gates are blocking** — UI prevents progression without explicit approval
- **Each stage shows its hypothesis** — Transparent reasoning at every step
- **Audit trail is always visible** — Side panel showing all decisions made
- **Manager can go back** — Any stage can be revisited and rerun

## API Design

The backend should expose:
- `POST /api/campaign/start` — Submit raw brief, returns session_id
- `GET /api/campaign/{session_id}/status` — Current stage and state
- `POST /api/campaign/{session_id}/approve` — Approve assumptions or final packet
- `GET /api/campaign/{session_id}/artifacts` — Get any stage output
