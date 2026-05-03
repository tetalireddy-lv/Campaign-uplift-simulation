import { motion } from 'framer-motion';
import { ShieldAlert, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';
import type { ReadinessResponse, Gap } from '../types/campaign';
import { PlanningHypothesisCard } from './PlanningHypothesisCard';
import { ManagerActionPanel, approveAction, legalAction, clarifyAction } from './ManagerActionPanel';

interface Props {
  data: ReadinessResponse;
  onApprove: () => void;
  loading: boolean;
}

function severityClass(s: string) {
  const m: Record<string, string> = { critical: 'badge-critical', high: 'badge-high', medium: 'badge-medium', low: 'badge-low' };
  return m[s?.toLowerCase()] ?? 'badge-low';
}

function ScoreRing({ score }: { score: number }) {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#10b981' : score >= 60 ? '#C9A84C' : '#ef4444';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-24 h-24">
        <svg width="96" height="96" className="-rotate-90">
          <circle cx="48" cy="48" r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
          <motion.circle
            cx="48" cy="48" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-2xl font-bold text-white"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {score}
          </motion.span>
          <span className="text-xs text-white/30">/ 100</span>
        </div>
      </div>
      <p className="text-xs text-white/40">Readiness Score</p>
    </div>
  );
}

function GapCard({ gap }: { gap: Gap }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      className="glass rounded-xl p-4"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <p className="text-sm font-semibold text-white">{gap.field}</p>
        <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${severityClass(gap.severity)}`}>
          {gap.severity}
        </span>
      </div>
      <p className="text-sm text-white/50 mb-2 leading-relaxed">{gap.description}</p>
      <div className="flex gap-2">
        <TrendingUp size={13} className="text-gold-400 shrink-0 mt-0.5" />
        <p className="text-xs text-gold-400">{gap.recommendation}</p>
      </div>
    </motion.div>
  );
}

export function ReadinessReview({ data, onApprove, loading }: Props) {
  const { readiness_score, gap_report, compliance_report, kpi_report } = data;
  const hypo = gap_report.planning_hypothesis;
  const compHypo = compliance_report.planning_hypothesis;
  const kpiHypo = kpi_report.planning_hypothesis;

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Step 2 — Validate Readiness</p>
        <h2 className="text-2xl font-bold text-white">Readiness Assessment</h2>
        <p className="text-white/40 text-sm mt-1">AI has analyzed your brief for gaps, compliance risks, and KPI measurability.</p>
      </motion.div>

      {/* Score + summary row */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-2xl p-6 flex items-center gap-8"
      >
        <ScoreRing score={readiness_score} />
        <div className="flex-1">
          <p className="text-sm font-semibold text-white mb-1">Overall Assessment</p>
          <p className="text-sm text-white/60 leading-relaxed">{gap_report.overall_assessment ?? '—'}</p>
          {Array.isArray(gap_report.strengths) && gap_report.strengths.length > 0 && (
            <div className="mt-3 flex flex-col gap-1">
              {gap_report.strengths.map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
                  <p className="text-xs text-white/50">{s}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </motion.div>

      {/* Gaps */}
      {Array.isArray(gap_report.gaps) && gap_report.gaps.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Brief Gaps</p>
          <div className="flex flex-col gap-3">
            {gap_report.gaps.map((gap, i) => (
              <GapCard key={i} gap={gap as Gap} />
            ))}
          </div>
        </div>
      )}

      {/* Compliance */}
      {Array.isArray((compliance_report as any).risks) && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <ShieldAlert size={15} className="text-orange-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Compliance Risks</p>
            <span className={`text-xs px-2 py-0.5 rounded-full ${severityClass((compliance_report.overall_risk ?? 'medium').toLowerCase())}`}>
              {compliance_report.overall_risk} Risk
            </span>
          </div>
          <div className="flex flex-col gap-3">
            {(compliance_report as any).risks.map((risk: any, i: number) => (
              <div key={i} className="glass rounded-xl p-4">
                <div className="flex items-start justify-between gap-3 mb-1">
                  <p className="text-sm font-semibold text-white">{risk.category}</p>
                  <span className={`text-xs px-2 py-0.5 rounded-full whitespace-nowrap ${severityClass(risk.severity)}`}>{risk.severity}</span>
                </div>
                <p className="text-sm text-white/50 mb-2">{risk.description}</p>
                <p className="text-xs text-gold-400">Mitigation: {risk.mitigation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KPI */}
      {kpi_report.primary_kpi && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle size={15} className="text-yellow-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">KPI Readiness</p>
          </div>
          <div className="glass rounded-xl p-4">
            <p className="text-sm font-semibold text-white mb-1">{String((kpi_report.primary_kpi as any).metric)}</p>
            <p className="text-sm text-white/50">Target: <span className="text-white/80">{String((kpi_report.primary_kpi as any).target)}</span> · Baseline: <span className="text-white/80">{String((kpi_report.primary_kpi as any).baseline)}</span></p>
            {Array.isArray(kpi_report.measurement_gaps) && (
              <div className="mt-3 flex flex-col gap-1">
                {kpi_report.measurement_gaps.map((g, i) => (
                  <div key={i} className="flex gap-2">
                    <AlertTriangle size={12} className="text-yellow-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-yellow-400/80">{g}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Hypotheses */}
      {hypo && <PlanningHypothesisCard hypothesis={hypo} />}
      {compHypo && <PlanningHypothesisCard hypothesis={compHypo} />}

      {/* Actions */}
      <ManagerActionPanel
        title="Step 2 — Manager Actions"
        actions={[
          approveAction(onApprove, loading),
          legalAction(() => alert('Compliance section sent to legal team')),
          clarifyAction(() => alert('Clarification request sent')),
        ]}
      />
    </div>
  );
}
