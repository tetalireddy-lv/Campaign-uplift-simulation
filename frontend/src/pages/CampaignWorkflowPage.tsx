import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { campaignApi } from '../api/campaignApi';
import { WorkflowSidebar } from '../components/WorkflowSidebar';
import { BriefInput } from '../components/BriefInput';
import { StructuredBriefReview } from '../components/StructuredBriefReview';
import { ReadinessReview } from '../components/ReadinessReview';
import { AmbiguityResolution } from '../components/AmbiguityResolution';
import { PlanSimulation } from '../components/PlanSimulation';
import { QAReview } from '../components/QAReview';
import { HandoffPacket } from '../components/HandoffPacket';
import { CampaignReport } from '../components/CampaignReport';
import { LoadingState } from '../components/LoadingState';
import type {
  Assumption,
  WorkflowState,
  WorkflowStep,
  StartResponse,
  ReadinessResponse,
  AmbiguityResponse,
  PlanResponse,
  QAHandoffResponse,
} from '../types/campaign';

const STEP_ORDER: WorkflowStep[] = ['brief', 'readiness', 'ambiguity', 'plan', 'handoff'];

const PAGE_VARIANTS = {
  initial: { opacity: 0, x: 24 },
  animate: { opacity: 1, x: 0, transition: { duration: 0.35, ease: 'easeOut' } },
  exit: { opacity: 0, x: -24, transition: { duration: 0.2 } },
};

function ErrorBanner({ message, onDismiss }: { message: string; onDismiss: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      className="glass rounded-xl p-4 border border-red-900/40 flex items-start justify-between gap-4 mb-4"
    >
      <p className="text-sm text-red-400">{message}</p>
      <button onClick={onDismiss} className="text-white/30 hover:text-white text-xs shrink-0">Dismiss</button>
    </motion.div>
  );
}

export function CampaignWorkflowPage() {
  const [state, setState] = useState<WorkflowState>({
    sessionId: null,
    currentStep: 'brief',
    loading: false,
    error: null,
    startData: null,
    readinessData: null,
    ambiguityData: null,
    planData: null,
    qaData: null,
    approvedAssumptions: [],
    managerAnswers: {},
  });

  const [completedSteps, setCompletedSteps] = useState<Set<WorkflowStep>>(new Set());
  const [subView, setSubView] = useState<'review' | 'handoff' | 'report'>('review');

  const setLoading = (loading: boolean) => setState(s => ({ ...s, loading }));
  const setError = (error: string | null) => setState(s => ({ ...s, error }));

  const advance = useCallback((to: WorkflowStep, from: WorkflowStep) => {
    setCompletedSteps(prev => new Set([...prev, from]));
    setState(s => ({ ...s, currentStep: to }));
  }, []);

  // ── Step 1: Parse brief ───────────────────────────────────────────────────
  const handleStartWorkflow = async (rawBrief: string) => {
    setLoading(true);
    setError(null);
    try {
      const data: StartResponse = await campaignApi.startWorkflow(rawBrief);
      setState(s => ({ ...s, sessionId: data.session_id, startData: data, loading: false }));
    } catch (e: unknown) {
      setLoading(false);
      setError(`Failed to parse brief: ${(e as Error).message}`);
    }
  };

  // ── Step 2: Validate readiness ────────────────────────────────────────────
  const handleValidateReadiness = async () => {
    if (!state.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data: ReadinessResponse = await campaignApi.validateReadiness(state.sessionId);
      setState(s => ({ ...s, readinessData: data, loading: false }));
      advance('readiness', 'brief');
    } catch (e: unknown) {
      setLoading(false);
      setError(`Readiness validation failed: ${(e as Error).message}`);
    }
  };

  // ── Step 3: Resolve ambiguity ─────────────────────────────────────────────
  const handleResolveAmbiguity = async () => {
    if (!state.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data: AmbiguityResponse = await campaignApi.resolveAmbiguity(state.sessionId);
      setState(s => ({ ...s, ambiguityData: data, loading: false }));
      advance('ambiguity', 'readiness');
    } catch (e: unknown) {
      setLoading(false);
      setError(`Ambiguity resolution failed: ${(e as Error).message}`);
    }
  };

  // ── Step 3b: Approve assumptions ──────────────────────────────────────────
  const handleApproveAssumptions = async (approved: Assumption[], answers: Record<string, string>) => {
    if (!state.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      await campaignApi.approveAssumptions(state.sessionId, approved, answers);
      setState(s => ({ ...s, approvedAssumptions: approved, managerAnswers: answers, loading: false }));
      advance('plan', 'ambiguity');
    } catch (e: unknown) {
      setLoading(false);
      setError(`Failed to save approvals: ${(e as Error).message}`);
    }
  };

  // ── Step 4: Plan and simulate ─────────────────────────────────────────────
  const handlePlanAndSimulate = async () => {
    if (!state.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data: PlanResponse = await campaignApi.planAndSimulate(state.sessionId);
      setState(s => ({ ...s, planData: data, loading: false }));
    } catch (e: unknown) {
      setLoading(false);
      setError(`Planning failed: ${(e as Error).message}`);
    }
  };

  // ── Step 5: QA and handoff ────────────────────────────────────────────────
  const handleQAAndHandoff = async () => {
    if (!state.sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data: QAHandoffResponse = await campaignApi.qaAndHandoff(state.sessionId);
      setState(s => ({ ...s, qaData: data, loading: false }));
      advance('handoff', 'plan');
    } catch (e: unknown) {
      setLoading(false);
      setError(`QA & Handoff failed: ${(e as Error).message}`);
    }
  };

  const handleGenerateHandoff = async () => {
    if (!state.sessionId) return;
    if (state.qaData) { setSubView('handoff'); return; }
    setLoading(true);
    setError(null);
    try {
      const data: QAHandoffResponse = await campaignApi.qaAndHandoff(state.sessionId);
      setState(s => ({ ...s, qaData: data, loading: false }));
      setSubView('handoff');
    } catch (e: unknown) {
      setLoading(false);
      setError(`Handoff generation failed: ${(e as Error).message}`);
    }
  };

  // ── Render current step ───────────────────────────────────────────────────
  const renderContent = () => {
    const { currentStep, loading } = state;

    // Step 1
    if (currentStep === 'brief') {
      if (loading) return <LoadingState message="Parsing campaign brief…" subMessage="Extracting structured fields and classifying intent" />;
      if (state.startData) {
        return (
          <StructuredBriefReview
            data={state.startData}
            onApprove={handleValidateReadiness}
            loading={loading}
          />
        );
      }
      return <BriefInput onSubmit={handleStartWorkflow} loading={loading} />;
    }

    // Step 2
    if (currentStep === 'readiness') {
      if (loading) return <LoadingState message="Validating readiness…" subMessage="Detecting gaps, compliance risks, and KPI measurability" />;
      if (state.readinessData) {
        return (
          <ReadinessReview
            data={state.readinessData}
            onApprove={handleResolveAmbiguity}
            loading={loading}
          />
        );
      }
      return <LoadingState message="Loading readiness data…" />;
    }

    // Step 3
    if (currentStep === 'ambiguity') {
      if (loading && !state.ambiguityData) return <LoadingState message="Generating clarifications…" subMessage="Identifying unanswered questions and forming assumptions" />;
      if (state.ambiguityData) {
        return (
          <AmbiguityResolution
            data={state.ambiguityData}
            onApprove={handleApproveAssumptions}
            loading={loading}
          />
        );
      }
      return <LoadingState message="Loading ambiguity data…" />;
    }

    // Step 4
    if (currentStep === 'plan') {
      if (loading && !state.planData) return <LoadingState message="Generating execution plan…" subMessage="Building channel strategy, measurement plan, timeline, asset checklist, and uplift simulation" />;
      if (state.planData) {
        return (
          <PlanSimulation
            data={state.planData}
            onApprove={handleQAAndHandoff}
            loading={loading}
          />
        );
      }
      // Auto-trigger plan generation when reaching this step
      return (
        <div className="flex flex-col items-center gap-6 py-16">
          <p className="text-white/60">Ready to generate the execution plan.</p>
          <motion.button
            onClick={handlePlanAndSimulate}
            className="btn-primary"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Generate Plan + Simulation
          </motion.button>
        </div>
      );
    }

    // Step 5
    if (currentStep === 'handoff') {
      if (loading && !state.qaData) return <LoadingState message="Running QA checks…" subMessage="Brief-to-plan alignment, consistency, and compliance review" />;

      if (state.qaData) {
        if (subView === 'report' && state.startData && state.readinessData && state.planData) {
          return (
            <CampaignReport
              startData={state.startData}
              readinessData={state.readinessData}
              ambiguityData={state.ambiguityData}
              planData={state.planData}
              qaData={state.qaData}
              approvedAssumptions={state.approvedAssumptions}
              onBack={() => setSubView('handoff')}
            />
          );
        }
        if (subView === 'handoff') {
          return <HandoffPacket data={state.qaData} onViewReport={() => setSubView('report')} />;
        }
        return (
          <QAReview
            data={state.qaData}
            onProceed={handleGenerateHandoff}
            loading={loading}
          />
        );
      }
      return <LoadingState message="Loading QA data…" />;
    }

    return null;
  };

  return (
    <div className="min-h-screen flex" style={{ background: 'radial-gradient(ellipse at top, rgba(201,168,76,0.04) 0%, #0a0a0a 60%)' }}>
      {/* Ambient background orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/3 w-96 h-96 rounded-full opacity-5"
          style={{ background: 'radial-gradient(circle, #C9A84C 0%, transparent 70%)', filter: 'blur(40px)' }} />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 rounded-full opacity-5"
          style={{ background: 'radial-gradient(circle, #C9A84C 0%, transparent 70%)', filter: 'blur(60px)' }} />
      </div>

      {/* Sidebar */}
      <div className="w-80 border-r border-white/5 p-6 flex flex-col sticky top-0 h-screen overflow-y-auto">
        <WorkflowSidebar
          currentStep={state.currentStep}
          completedSteps={completedSteps}
          onStepClick={(step) => {
            if (completedSteps.has(step) || step === state.currentStep) {
              setState(s => ({ ...s, currentStep: step }));
              setSubView(step === 'handoff' ? 'handoff' : 'review');
            }
          }}
        />
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-8 py-10">
          {/* Error banner */}
          <AnimatePresence>
            {state.error && (
              <ErrorBanner message={state.error} onDismiss={() => setError(null)} />
            )}
          </AnimatePresence>

          {/* Step content with animated transitions */}
          <AnimatePresence mode="wait">
            <motion.div
              key={`${state.currentStep}-${state.startData ? 'data' : 'input'}-${subView}`}
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
