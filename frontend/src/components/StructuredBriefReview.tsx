import { motion } from 'framer-motion';
import { Target, Users, Megaphone, DollarSign, Calendar, BarChart2, AlertOctagon } from 'lucide-react';
import type { StartResponse } from '../types/campaign';
import { PlanningHypothesisCard } from './PlanningHypothesisCard';
import { ManagerActionPanel, approveAction, editAction, clarifyAction } from './ManagerActionPanel';

interface Props {
  data: StartResponse;
  onApprove: () => void;
  loading: boolean;
}

function Field({ icon, label, value }: { icon: React.ReactNode; label: string; value: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ background: 'rgba(201,168,76,0.1)' }}>
        <span className="text-gold-400">{icon}</span>
      </div>
      <div className="min-w-0">
        <p className="text-xs text-white/30 uppercase tracking-wide font-medium mb-0.5">{label}</p>
        <p className="text-sm text-white/80 leading-relaxed">{value}</p>
      </div>
    </div>
  );
}

export function StructuredBriefReview({ data, onApprove, loading }: Props) {
  const brief = data.structured_brief;
  const intent = data.campaign_intent;
  const hypo = brief.planning_hypothesis;

  const isMock = brief._source === 'mock';

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold">Step 1 — Understand Brief</p>
          {isMock && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-950 text-yellow-400 border border-yellow-800">
              Mock data (no API key)
            </span>
          )}
        </div>
        <h2 className="text-2xl font-bold text-white">
          {String(brief.campaign_name ?? 'Untitled Campaign')}
        </h2>
        <p className="text-white/40 text-sm mt-1">Brief successfully parsed — review and approve to continue</p>
      </motion.div>

      {/* Intent badge row */}
      {intent && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex flex-wrap gap-2"
        >
          {Object.entries(intent).filter(([k]) => k !== '_source').map(([key, val]) => (
            <span key={key} className="text-xs px-3 py-1 rounded-full glass text-white/50">
              <span className="text-white/25">{key.replace(/_/g, ' ')}: </span>
              <span className="text-white/70">{String(val)}</span>
            </span>
          ))}
        </motion.div>
      )}

      {/* Structured fields */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="glass rounded-2xl p-6 grid grid-cols-1 gap-5"
      >
        <Field icon={<Target size={15} />} label="Business Objective" value={String(brief.business_objective ?? '—')} />
        <hr className="divider" />

        <Field icon={<Users size={15} />} label="Target Audience" value={
          typeof brief.target_audience === 'object'
            ? Object.values(brief.target_audience as Record<string, string>).filter(Boolean).join(' · ')
            : String(brief.target_audience ?? '—')
        } />
        <hr className="divider" />

        <Field icon={<Megaphone size={15} />} label="Channels" value={
          Array.isArray(brief.channels) ? brief.channels.join(', ') : String(brief.channels ?? '—')
        } />
        <hr className="divider" />

        <Field icon={<DollarSign size={15} />} label="Budget" value={
          typeof brief.budget === 'object'
            ? `$${(brief.budget as any).total?.toLocaleString()} ${(brief.budget as any).currency ?? ''}`
            : String(brief.budget ?? '—')
        } />
        <hr className="divider" />

        <Field icon={<Calendar size={15} />} label="Timeline" value={
          typeof brief.timeline === 'object'
            ? `${(brief.timeline as any).start} → ${(brief.timeline as any).end}`
            : String(brief.timeline ?? '—')
        } />
        <hr className="divider" />

        <Field icon={<BarChart2 size={15} />} label="Success Metrics" value={
          typeof brief.success_metrics === 'object'
            ? `${(brief.success_metrics as any).primary}: ${(brief.success_metrics as any).target} (baseline: ${(brief.success_metrics as any).baseline})`
            : String(brief.success_metrics ?? '—')
        } />

        {Array.isArray(brief.constraints) && brief.constraints.length > 0 && (
          <>
            <hr className="divider" />
            <Field icon={<AlertOctagon size={15} />} label="Constraints" value={
              <ul className="list-disc list-inside space-y-1">
                {brief.constraints.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            } />
          </>
        )}
      </motion.div>

      {/* Planning hypothesis */}
      {hypo && (
        <PlanningHypothesisCard hypothesis={hypo} />
      )}

      {/* Manager actions */}
      <ManagerActionPanel
        title="Step 1 — Manager Actions"
        actions={[
          approveAction(onApprove, loading),
          editAction(() => alert('Edit mode: modify the brief above and re-submit')),
          clarifyAction(() => alert('Request clarification sent to brief owner')),
        ]}
      />
    </div>
  );
}
