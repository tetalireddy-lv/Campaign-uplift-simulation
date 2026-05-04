// ── Core domain types for Campaign Readiness Copilot ───────────────────────

export interface PlanningHypothesis {
  what_ai_believes: string;
  evidence_from_brief: string;
  risk_if_wrong: string;
  validation_needed: string;
  manager_action_required: string;
}

export interface StructuredBrief {
  campaign_name?: string;
  business_objective?: string;
  target_audience?: Record<string, unknown>;
  key_message?: string;
  channels?: string[];
  budget?: Record<string, unknown>;
  timeline?: Record<string, unknown>;
  success_metrics?: Record<string, unknown>;
  constraints?: string[];
  brand_voice?: string;
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
  [key: string]: unknown;
}

export interface Gap {
  field: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  recommendation: string;
}

export interface GapReport {
  readiness_score: number;
  overall_assessment?: string;
  gaps?: Gap[];
  strengths?: string[];
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
  [key: string]: unknown;
}

export interface ComplianceRisk {
  category: string;
  severity: 'high' | 'medium' | 'low';
  description: string;
  mitigation: string;
}

export interface ComplianceReport {
  overall_risk?: string;
  risks?: ComplianceRisk[];
  compliance_checklist?: string[];
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
  [key: string]: unknown;
}

export interface KpiReport {
  primary_kpi?: Record<string, unknown>;
  secondary_kpis?: Array<Record<string, unknown>>;
  measurement_gaps?: string[];
  tracking_readiness?: string;
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
  [key: string]: unknown;
}

export interface ClarificationQuestion {
  id: string;
  question: string;
  category: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  impact: string;
}

export interface Assumption {
  id: string;
  assumption: string;
  confidence: 'High' | 'Medium' | 'Low';
  source: string;
  if_wrong: string;
}

export interface SimulationScenarioResult {
  scenario: string;
  expected_kpi_value: number;
  market_uplift_percent: number;
  confidence: string;
  reason: string;
}

export type SimulationScenario = SimulationScenarioResult;

export interface AudienceUpliftEntry {
  pct: number;
  count: number;
  explanation: string;
}

export interface SimulationAssumption {
  field: string;
  value: unknown;
  source: string;
  editable_by_manager: boolean;
}

export interface MeasurementPlan {
  primary_kpi?: string;
  baseline?: string | number | null;
  target?: string | number | null;
  measurement_framework?: string;
  measurement_window?: string;
  reporting_cadence?: string;
  data_sources?: string[];
  control_strategy?: string;
  success_thresholds?: Record<string, unknown>;
  notes?: string[];
  owner?: string;
  [key: string]: unknown;
}

export interface SimulationReport {
  simulation_mode?: string;
  confidence_level?: string;
  primary_kpi?: string;
  baseline_kpi_value?: number;
  target_kpi_value?: number;
  expected_kpi_value?: number;
  market_uplift_percent?: number;
  scenario_results?: SimulationScenarioResult[];
  scenarios?: SimulationScenarioResult[];
  audience_uplift_mix?: Record<string, AudienceUpliftEntry>;
  assumptions_used?: SimulationAssumption[];
  uplift_drivers?: string[];
  uplift_blockers?: string[];
  manager_editable_fields?: string[];
  warning?: string;
  expected_value?: string | number;
  roi?: string | number;
  risk_factors?: string[];
  recommendation?: string;
  expected_campaign_revenue?: number;
  _source?: string;
  [key: string]: unknown;
}

export interface ExecutionPlan {
  campaign_overview?: string;
  strategy_summary?: string;
  phases?: Array<Record<string, unknown>>;
  channel_mix?: Record<string, string>;
  budget_allocation?: Record<string, number>;
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
  [key: string]: unknown;
}

export interface QAReport {
  alignment_score?: number;
  overall_verdict?: string;
  aligned_items?: string[];
  gaps?: Array<{ issue: string; severity: string; recommendation: string }>;
  critical_misalignments?: string[];
  planning_hypothesis?: PlanningHypothesis;
  _source?: string;
}

export interface HandoffPacket {
  campaign_name?: string;
  launch_date?: string;
  status?: string;
  executive_summary?: string;
  stakeholder_sections?: Record<string, string[]>;
  next_steps?: string[];
  risk_register?: string[];
  important_notice?: string;
  market_uplift_summary?: {
    simulation_mode?: string;
    confidence_level?: string;
    baseline_kpi?: { name?: string; value?: string | number };
    target_kpi?: string | number;
    expected_kpi?: string | number;
    market_uplift_percent?: number;
    audience_uplift_mix?: Record<string, AudienceUpliftEntry>;
    top_uplift_drivers?: string[];
    top_uplift_blockers?: string[];
    warning?: string;
  };
  _source?: string;
  [key: string]: unknown;
}

// ── API Response types ───────────────────────────────────────────────────────

export interface StartResponse {
  session_id: string;
  status: string;
  structured_brief: StructuredBrief;
  campaign_intent: Record<string, unknown>;
}

export interface ReadinessResponse {
  session_id: string;
  status: string;
  readiness_score: number;
  gap_report: GapReport;
  compliance_report: ComplianceReport;
  kpi_report: KpiReport;
}

export interface AmbiguityResponse {
  session_id: string;
  status: string;
  clarification_questions: ClarificationQuestion[];
  assumptions: Assumption[];
}

export interface ApproveResponse {
  session_id: string;
  status: string;
  approved_count: number;
}

export interface PlanResponse {
  session_id: string;
  status: string;
  channel_strategy: Record<string, unknown>;
  execution_plan: ExecutionPlan;
  measurement_plan: MeasurementPlan;
  simulation_report: SimulationReport;
  asset_checklist: Record<string, unknown>;
  timeline_plan: Record<string, unknown>;
}

export interface QAHandoffResponse {
  session_id: string;
  status: string;
  qa_report: QAReport;
  consistency_report: Record<string, unknown>;
  final_compliance_report: Record<string, unknown>;
  handoff_packet: HandoffPacket;
}

// ── Workflow step enum ───────────────────────────────────────────────────────

export type WorkflowStep =
  | 'brief'
  | 'readiness'
  | 'ambiguity'
  | 'plan'
  | 'handoff'
  | 'report';

export interface WorkflowState {
  sessionId: string | null;
  currentStep: WorkflowStep;
  loading: boolean;
  error: string | null;
  // Data
  startData: StartResponse | null;
  readinessData: ReadinessResponse | null;
  ambiguityData: AmbiguityResponse | null;
  planData: PlanResponse | null;
  qaData: QAHandoffResponse | null;
  // Manager state
  approvedAssumptions: Assumption[];
  managerAnswers: Record<string, string>;
}
