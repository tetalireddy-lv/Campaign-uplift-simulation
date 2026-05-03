# Campaign Workflow Instructions

## Pipeline Stages

The workflow follows a strict 7-stage pipeline:

1. **Parse Brief** → Convert raw text to structured schema
2. **Validate Readiness** → Detect gaps, risks, KPI issues
3. **Resolve Ambiguity** → Generate questions and assumptions
4. **Await Manager Approval** → Human-in-the-loop checkpoint
5. **Generate Plan & Simulate** → Create execution plan, simulate uplift
6. **QA & Handoff** → Validate alignment, produce handoff packet
7. **Final Manager Approval** → Human signoff

## Conditional Routing

- If readiness score ≥ 85 → skip ambiguity resolution, go straight to planning
- If QA finds critical misalignments → loop back to plan generation
- If compliance finds blocking issues → route to legal review

## State Transitions

Each node must:
1. Read only its required inputs from state
2. Process using LLM + deterministic tools
3. Return only its outputs (merged into state by LangGraph)
4. Update `current_step` and `audit_trail`

## Adding New Stages

To add a new stage:
1. Create a prompt template in `prompts/`
2. Create a tool in `tools/` if deterministic logic needed
3. Add a node function in `workflow/nodes.py`
4. Register the node in `workflow/graph.py`
5. Define edges (when does this node run?)
