# Campaign Readiness Copilot

An AI-powered full-stack application that guides a campaign manager from a raw campaign brief to a launch-ready execution plan through a structured 5-step workflow.

> The AI never launches campaigns automatically. The campaign manager remains in control at every step.

---

## Quick Start

You need two terminals running simultaneously.

### Backend
```bash
# From project root
.venv/bin/uvicorn backend.main:app --reload --port 8000
```
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### Frontend
```bash
cd frontend
npm install   # first time only
npm run dev
```
- App: `http://localhost:5173`

> The Vite dev server proxies `/api` requests to `http://localhost:8000`.

### CLI (optional)
```bash
# Run the workflow directly from the command line
.venv/bin/python main.py

# Or pass a brief file
.venv/bin/python main.py path/to/brief.txt
```

---

## Architecture

```
Campaign-uplift-simulation/
├── agent/                      # All AI / LangGraph agent code
│   ├── workflow/               # LangGraph graph, nodes, state, LLM utils
│   ├── tools/                  # 14 modular tool functions
│   ├── prompts/                # Jinja2 prompt templates (organised by step)
│   ├── campaign_context/       # Domain knowledge markdown
│   └── data/
│       ├── raw/                # Source CSV files
│       └── scripts/            # Data generation scripts
├── backend/                    # FastAPI HTTP layer
│   ├── main.py                 # FastAPI app entry point
│   ├── api/routes.py           # 7 API routes
│   ├── models/schemas.py       # Pydantic request/response models
│   └── services/
│       ├── session.py          # In-memory session store
│       ├── workflow_service.py # Calls agent tools / LLM
│       └── mock_data.py        # Fallback data (no API key needed)
├── frontend/                   # React + Vite + TypeScript
│   └── src/
│       ├── api/campaignApi.ts  # All API calls
│       ├── types/campaign.ts   # TypeScript types
│       ├── components/         # UI components
│       └── pages/              # CampaignWorkflowPage
├── tests/                      # pytest test suite
├── docs/                       # Planning docs and instructions
├── main.py                     # CLI entry point
└── requirements.txt
```

---

## 5-Step Workflow

| Step | Label | Backend Route | Tools Used |
|------|-------|---------------|------------|
| 1 | Understand Brief | `POST /api/workflow/start` | brief_parser, classify_intent |
| 2 | Validate Readiness | `POST /api/workflow/{id}/validate-readiness` | gap_detector, compliance_risk, kpi_review |
| 3 | Resolve Ambiguity | `POST /api/workflow/{id}/resolve-ambiguity` | clarification_questions, assumption_register |
| 3b | Approve Assumptions | `POST /api/workflow/{id}/approve-assumptions` | (manager action) |
| 4 | Plan + Simulate | `POST /api/workflow/{id}/plan-and-simulate` | channel_strategy, execution_plan, asset_checklist, timeline, uplift_sim |
| 5 | QA + Handoff | `POST /api/workflow/{id}/qa-and-handoff` | brief_to_plan_qa, multi_channel_consistency, compliance_review, handoff_packet |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_OPENAI_ENDPOINT` | Yes (for live mode) | Azure OpenAI resource endpoint |
| `AZURE_OPENAI_API_KEY` | Yes (for live mode) | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | Yes (for live mode) | Model deployment name |
| `AZURE_OPENAI_API_VERSION` | Optional | Default: `2024-12-01-preview` |

Without valid Azure credentials all steps automatically fall back to realistic mock data.

Copy `.env` and fill in your values — the file is already present at the project root.

---

## Session Storage

In-memory for demo/hackathon use. Replace `backend/services/session.py` with SQLite or Redis for production.

---

## Running Tests

```bash
.venv/bin/pytest tests/
```
