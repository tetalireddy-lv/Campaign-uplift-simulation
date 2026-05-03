# Agent Vision & Architecture Instructions

## Core Principle

The Campaign Readiness Copilot is a **manager-controlled, AI-assisted** workflow. The AI surfaces options, structures ambiguity, explains assumptions, and keeps the campaign manager in control.

## Architecture Boundaries

```
Orchestrator (LangGraph) → owns state transitions and routing
LLM (GPT-4o / Claude) → owns judgment, reasoning, natural language generation
Python Tools → own deterministic execution (scoring, validation, formatting)
Campaign Manager → owns approval decisions
```

## Non-Negotiable Rules

1. **AI never launches campaigns** — It produces a readiness packet for human approval
2. **Manager approval gates cannot be skipped** — Both assumption approval and final approval are required
3. **Every assumption is explicit** — No hidden reasoning that affects the plan
4. **Audit trail is complete** — Every step logged with timestamp and outcome
5. **Prompts are scoped** — Each LLM call receives only the state it needs, not the full conversation

## State Management

- State is owned by the orchestrator (LangGraph StateGraph)
- LLM calls receive scoped slices of state
- State is checkpointed at every stage transition
- State can be resumed from any checkpoint

## Tool Design Rules

- Tools should be pure functions where possible
- Deterministic logic (scoring, validation) is in Python, not prompts
- Tools return structured JSON, not natural language
- Tools should be independently testable
