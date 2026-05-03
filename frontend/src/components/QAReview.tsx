import { motion } from 'framer-motion';
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import type { QAHandoffResponse, QAReport } from '../types/campaign';
import { PlanningHypothesisCard } from './PlanningHypothesisCard';
import { ManagerActionPanel } from './ManagerActionPanel';

interface Props {
  data: QAHandoffResponse;
  onProceed: () => void;
  loading: boolean;
}

function scoreColor(score: number): string {
  if (score >= 85) return 'text-emerald-400';
  if (score >= 65) return 'text-yellow-400';
  return 'text-red-400';
}

function AlignedItems({ items }: { items: string[] }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">What's Aligned</p>
      <div className="flex flex-col gap-2">
        {items.map((item, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex items-center gap-3 glass rounded-xl px-4 py-3"
          >
            <CheckCircle2 size={15} className="text-emerald-400 shrink-0" />
            <p className="text-sm text-white/70">{item}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function GapItems({ gaps }: { gaps: QAReport['gaps'] }) {
  if (!gaps || gaps.length === 0) return null;
  return (
    <div>
      <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Gaps to Address</p>
      <div className="flex flex-col gap-3">
        {gaps.map((gap, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.07 }}
            className="glass rounded-xl p-4 border border-yellow-900/30"
          >
            <div className="flex items-start gap-3">
              <AlertTriangle size={15} className="text-yellow-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-white mb-1">{gap.issue}</p>
                <p className="text-xs text-white/30 mb-1">Severity: {gap.severity}</p>
                <p className="text-xs text-gold-400">{gap.recommendation}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function CriticalItems({ items }: { items: string[] }) {
  if (items.length === 0) return null;
  return (
    <div className="glass rounded-xl p-4 border border-red-900/40">
      <div className="flex items-center gap-2 mb-3">
        <XCircle size={15} className="text-red-400" />
        <p className="text-sm font-semibold text-red-400">Critical Misalignments</p>
      </div>
      {items.map((m, i) => (
        <p key={i} className="text-sm text-white/60">{m}</p>
      ))}
    </div>
  );
}

export function QAReview({ data, onProceed, loading }: Props) {
  const { qa_report, consistency_report, final_compliance_report } = data;
  const score = qa_report.alignment_score ?? 0;
  const hypo = qa_report.planning_hypothesis;
  const alignedItems = qa_report.aligned_items ?? [];
  const gaps = qa_report.gaps;
  const criticals = qa_report.critical_misalignments ?? [];

  const consistencyScore = typeof consistency_report.consistency_score === 'number'
    ? consistency_report.consistency_score
    : Number(consistency_report.consistency_score ?? 0);
  const complianceStatus = String(final_compliance_report.status ?? '');

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Step 5 — QA + Handoff</p>
        <h2 className="text-2xl font-bold text-white">Quality Assurance Review</h2>
        <p className="text-white/40 text-sm mt-1">Final AI validation before the handoff packet is generated.</p>
      </motion.div>

      {/* Alignment score */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-xs text-white/30 uppercase tracking-wide mb-1">Brief-to-Plan Alignment</p>
            <p className={`text-4xl font-bold ${scoreColor(score)}`}>
              {score}
              <span className="text-xl text-white/20">/100</span>
            </p>
          </div>
          <ShieldCheck size={32} className={scoreColor(score)} />
        </div>
        <p className="text-sm text-white/60 leading-relaxed">{qa_report.overall_verdict ?? ''}</p>
      </motion.div>

      {alignedItems.length > 0 && <AlignedItems items={alignedItems} />}
      <GapItems gaps={gaps} />
      <CriticalItems items={criticals} />

      {/* Consistency */}
      {consistencyScore > 0 && (
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <p className="text-sm text-white/60">Multi-Channel Consistency Score</p>
          <p className={`text-2xl font-bold ${scoreColor(consistencyScore)}`}>
            {consistencyScore}%
          </p>
        </div>
      )}

      {/* Compliance */}
      {complianceStatus && (
        <div className="glass rounded-xl p-4 flex items-center justify-between">
          <p className="text-sm text-white/60">Final Compliance Status</p>
          <span className="text-sm font-semibold text-emerald-400">{complianceStatus}</span>
        </div>
      )}

      {hypo && <PlanningHypothesisCard hypothesis={hypo} />}

      <ManagerActionPanel
        title="Step 5 — Manager Actions"
        actions={[
          {
            label: 'Generate Handoff Packet',
            variant: 'primary',
            onClick: onProceed,
            disabled: loading,
          },
          {
            label: 'Send to Legal',
            variant: 'ghost',
            onClick: () => alert('QA report sent to legal team'),
          },
        ]}
      />
    </div>
  );
}
