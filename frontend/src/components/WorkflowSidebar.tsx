import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Brain, ShieldCheck, HelpCircle, BarChart3, PackageCheck, Zap, Database, FileText } from 'lucide-react';
import type { WorkflowStep } from '../types/campaign';
import { campaignApi } from '../api/campaignApi';

const STEPS: { id: WorkflowStep; label: string; sub: string; icon: React.ReactNode }[] = [
  { id: 'brief', label: 'Understand Brief', sub: 'Parse & structure raw campaign brief', icon: <Brain size={16} /> },
  { id: 'readiness', label: 'Validate Readiness', sub: 'Gaps, compliance & KPI analysis', icon: <ShieldCheck size={16} /> },
  { id: 'ambiguity', label: 'Resolve Ambiguity', sub: 'Clarification questions & assumptions', icon: <HelpCircle size={16} /> },
  { id: 'plan', label: 'Plan + Simulate', sub: 'Execution plan & uplift scenarios', icon: <BarChart3 size={16} /> },
  { id: 'handoff', label: 'QA + Handoff', sub: 'Final review & launch packet', icon: <PackageCheck size={16} /> },
  { id: 'report', label: 'Final Report', sub: 'Structured campaign readiness report', icon: <FileText size={16} /> },
];

interface Props {
  currentStep: WorkflowStep;
  completedSteps: Set<WorkflowStep>;
  onStepClick: (step: WorkflowStep) => void;
}

function getStatus(step: WorkflowStep, current: WorkflowStep, completed: Set<WorkflowStep>) {
  if (step === current) return 'active';
  if (completed.has(step)) return 'done';
  return 'pending';
}

interface LLMStatus {
  llm_mode: 'live' | 'mock';
  openai_key_configured: boolean;
  model: string;
}

export function WorkflowSidebar({ currentStep, completedSteps, onStepClick }: Props) {
  const [llmStatus, setLlmStatus] = useState<LLMStatus | null>(null);

  useEffect(() => {
    campaignApi.getConfigStatus()
      .then(setLlmStatus)
      .catch(() => setLlmStatus({ llm_mode: 'mock', openai_key_configured: false, model: 'gpt-4o' }));
  }, []);

  return (
    <aside className="w-72 shrink-0 flex flex-col gap-2">
      {/* Brand header */}
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Campaign Readiness</p>
        <h1 className="text-xl font-bold text-white">Copilot</h1>
        <p className="text-xs text-white/40 mt-1">AI-powered · Manager in control</p>
      </div>

      {/* LLM mode badge */}
      {llmStatus && (
        <motion.div
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-2 ${
            llmStatus.llm_mode === 'live'
              ? 'bg-emerald-950/60 border border-emerald-800/40'
              : 'bg-yellow-950/60 border border-yellow-800/40'
          }`}
        >
          {llmStatus.llm_mode === 'live' ? (
            <Zap size={13} className="text-emerald-400 shrink-0" />
          ) : (
            <Database size={13} className="text-yellow-400 shrink-0" />
          )}
          <div className="min-w-0">
            <p className={`text-xs font-semibold ${llmStatus.llm_mode === 'live' ? 'text-emerald-400' : 'text-yellow-400'}`}>
              {llmStatus.llm_mode === 'live' ? `Live LLM · ${llmStatus.model}` : 'Mock Mode'}
            </p>
            <p className="text-xs text-white/30 truncate">
              {llmStatus.llm_mode === 'live' ? 'Real AI responses active' : 'Set AZURE_OPENAI_API_KEY in .env'}
            </p>
          </div>
          <span className={`w-2 h-2 rounded-full shrink-0 ${
            llmStatus.llm_mode === 'live' ? 'bg-emerald-400 animate-pulse' : 'bg-yellow-400/60'
          }`} />
        </motion.div>
      )}

      <div className="flex flex-col gap-1">
        {STEPS.map((step, idx) => {
          const status = getStatus(step.id, currentStep, completedSteps);
          const isClickable = status === 'done' || status === 'active';

          return (
            <motion.button
              key={step.id}
              onClick={() => isClickable && onStepClick(step.id)}
              disabled={!isClickable && status === 'pending'}
              className={`w-full text-left rounded-xl p-4 transition-all duration-200 ${
                status === 'active'
                  ? 'glass-gold glow-gold'
                  : status === 'done'
                  ? 'glass hover:bg-white/5 cursor-pointer'
                  : 'opacity-40 cursor-not-allowed'
              }`}
              whileHover={isClickable ? { x: 4 } : {}}
              layout
            >
              <div className="flex items-start gap-3">
                <div
                  className={`step-badge shrink-0 mt-0.5 ${
                    status === 'active'
                      ? 'step-badge-active'
                      : status === 'done'
                      ? 'step-badge-done'
                      : 'step-badge-pending'
                  }`}
                >
                  {status === 'done' ? <Check size={14} /> : status === 'active' ? step.icon : idx + 1}
                </div>

                <div className="min-w-0">
                  <p className={`text-sm font-semibold leading-tight ${
                    status === 'active' ? 'text-gold-400' : status === 'done' ? 'text-white' : 'text-white/40'
                  }`}>
                    {step.label}
                  </p>
                  <p className="text-xs text-white/40 mt-0.5 leading-snug">{step.sub}</p>
                </div>
              </div>

              {status === 'active' && (
                <motion.div
                  layoutId="active-indicator"
                  className="h-0.5 mt-3 rounded-full"
                  style={{ background: 'linear-gradient(90deg, #C9A84C, transparent)' }}
                />
              )}
            </motion.button>
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="mt-6 px-1">
        <div className="flex justify-between text-xs text-white/30 mb-2">
          <span>Progress</span>
          <span>{completedSteps.size}/6</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #C9A84C, #F5D98A)' }}
            initial={{ width: 0 }}
            animate={{ width: `${(completedSteps.size / 6) * 100}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      <div className="mt-auto pt-6">
        <div className="glass rounded-xl p-3 text-xs text-white/30 leading-relaxed">
          ⚠️ AI never launches campaigns automatically. Every step requires manager approval.
        </div>
      </div>
    </aside>
  );
}
