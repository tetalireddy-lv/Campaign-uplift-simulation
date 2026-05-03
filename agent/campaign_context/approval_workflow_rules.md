# Approval Workflow Rules

## Core Principle

The Campaign Readiness Copilot NEVER autonomously launches or finalizes a campaign. Every material decision requires explicit campaign manager approval.

## Approval Gates

### Gate 1: Assumption Approval (Post-Ambiguity Resolution)

**What is presented:**
- Clarification questions for stakeholders
- Explicit assumptions with confidence levels
- Planning hypotheses with risk assessments

**Manager Actions:**
- Approve assumption as-is
- Edit assumption (provide corrected version)
- Reject assumption (remove from plan)
- Answer clarification question directly
- Escalate question to stakeholder
- Mark as "proceed with low confidence"

**Criteria to pass:**
- All critical assumptions reviewed
- No high-risk assumptions left unaddressed
- Manager explicitly confirms "proceed to planning"

### Gate 2: Final Approval (Post-QA)

**What is presented:**
- Complete handoff packet
- QA findings and alignment score
- Simulation results with confidence ranges
- Compliance review findings
- Approval action options

**Manager Actions:**
- Approve for execution
- Request modifications (specify areas)
- Send to legal review
- Send to stakeholder for input
- Reject brief (with reason)
- Request re-simulation with different assumptions

**Criteria to pass:**
- Manager selects explicit approval action
- All critical QA findings addressed
- Compliance issues resolved or acknowledged

## Workflow Pause Behavior

When the workflow reaches an approval gate:
1. State is persisted (checkpointed)
2. Notification sent to manager
3. Workflow pauses — no further processing
4. Manager review can happen asynchronously
5. On manager response, workflow resumes from checkpoint

## Audit Trail

Every approval action is logged:
```json
{
  "timestamp": "ISO-8601",
  "gate": "assumption_approval | final_approval",
  "action": "approve | edit | reject | escalate",
  "actor": "manager_id",
  "item_id": "assumption_id or packet_id",
  "notes": "optional manager notes"
}
```

## Escalation Rules

- If manager does not respond within configured SLA → send reminder
- If critical compliance issue found → auto-escalate to legal
- If budget exceeds threshold → require additional approver
- If brief contradicts brand guidelines → flag for brand team
