import axios from 'axios';
import type {
  ApproveResponse,
  AmbiguityResponse,
  PlanResponse,
  QAHandoffResponse,
  ReadinessResponse,
  StartResponse,
} from '../types/campaign';

const BASE = '/api';

const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const campaignApi = {
  /** Step 1 — Parse the raw brief */
  startWorkflow: (rawBrief: string): Promise<StartResponse> =>
    api.post<StartResponse>('/workflow/start', { raw_brief: rawBrief }).then(r => r.data),

  /** Step 2 — Validate readiness */
  validateReadiness: (sessionId: string): Promise<ReadinessResponse> =>
    api.post<ReadinessResponse>(`/workflow/${sessionId}/validate-readiness`).then(r => r.data),

  /** Step 3 — Resolve ambiguity */
  resolveAmbiguity: (sessionId: string): Promise<AmbiguityResponse> =>
    api.post<AmbiguityResponse>(`/workflow/${sessionId}/resolve-ambiguity`).then(r => r.data),

  /** Step 3b — Approve assumptions */
  approveAssumptions: (
    sessionId: string,
    approvedAssumptions: unknown[],
    managerAnswers: Record<string, string>
  ): Promise<ApproveResponse> =>
    api
      .post<ApproveResponse>(`/workflow/${sessionId}/approve-assumptions`, {
        approved_assumptions: approvedAssumptions,
        manager_answers: managerAnswers,
      })
      .then(r => r.data),

  /** Step 4 — Plan and simulate */
  planAndSimulate: (sessionId: string): Promise<PlanResponse> =>
    api.post<PlanResponse>(`/workflow/${sessionId}/plan-and-simulate`).then(r => r.data),

  /** Step 5 — QA and handoff */
  qaAndHandoff: (sessionId: string): Promise<QAHandoffResponse> =>
    api.post<QAHandoffResponse>(`/workflow/${sessionId}/qa-and-handoff`).then(r => r.data),

  /** Get session state */
  getSession: (sessionId: string) =>
    api.get(`/workflow/${sessionId}`).then(r => r.data),

  /** Check LLM configuration */
  getConfigStatus: (): Promise<{ llm_mode: 'live' | 'mock'; openai_key_configured: boolean; model: string }> =>
    api.get('/config/status').then(r => r.data),
};
