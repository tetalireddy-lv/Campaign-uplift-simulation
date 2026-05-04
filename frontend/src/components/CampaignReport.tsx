import { useRef } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Download, Printer, ChevronRight,
  Target, Users, Megaphone, DollarSign, Calendar, BarChart2,
  AlertOctagon, ShieldCheck, TrendingUp, AlertTriangle,
  CheckCircle2, ArrowRight, PackageCheck, Layers, Clock,
  ClipboardList, ListOrdered, LineChart,
} from 'lucide-react';
import type {
  StartResponse, ReadinessResponse, AmbiguityResponse,
  PlanResponse, QAHandoffResponse, Assumption,
} from '../types/campaign';

interface ReportProps {
  startData: StartResponse;
  readinessData: ReadinessResponse;
  ambiguityData: AmbiguityResponse | null;
  planData: PlanResponse;
  qaData: QAHandoffResponse;
  approvedAssumptions: Assumption[];
  onBack: () => void;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function severityBadge(s: string) {
  const map: Record<string, string> = {
    critical: 'bg-red-950 text-red-400 border-red-800',
    high: 'bg-orange-950 text-orange-400 border-orange-800',
    medium: 'bg-yellow-950 text-yellow-400 border-yellow-800',
    low: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  };
  return map[(s ?? '').toLowerCase()] ?? map.medium;
}

function scoreColor(n: number) {
  if (n >= 80) return '#10b981';
  if (n >= 60) return '#C9A84C';
  return '#ef4444';
}

function Section({ num, title, children }: { num: string; title: string; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      <div className="flex items-center gap-3 mb-4">
        <span
          className="text-xs font-bold px-2.5 py-1 rounded-lg"
          style={{ background: 'rgba(201,168,76,0.15)', color: '#C9A84C', border: '1px solid rgba(201,168,76,0.25)' }}
        >
          {num}
        </span>
        <h2 className="text-base font-bold text-white uppercase tracking-widest">{title}</h2>
        <div className="flex-1 h-px" style={{ background: 'linear-gradient(to right, rgba(201,168,76,0.2), transparent)' }} />
      </div>
      {children}
    </motion.div>
  );
}

function Row({ icon, label, value }: { icon: React.ReactNode; label: string; value: React.ReactNode }) {
  return (
    <div className="flex gap-3 py-3 border-b border-white/5 last:border-0">
      <div className="w-7 h-7 rounded-md flex items-center justify-center shrink-0 mt-0.5" style={{ background: 'rgba(201,168,76,0.1)' }}>
        <span className="text-gold-400">{icon}</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-white/30 uppercase tracking-wide mb-0.5">{label}</p>
        <div className="text-sm text-white/80 leading-relaxed">{value}</div>
      </div>
    </div>
  );
}

function ScoreBadge({ score, label }: { score: number; label: string }) {
  const color = scoreColor(score);
  const pct = (score / 100) * 100;
  return (
    <div className="flex items-center gap-4 p-4 rounded-xl" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
      <div className="relative w-14 h-14 shrink-0">
        <svg width="56" height="56" className="-rotate-90">
          <circle cx="28" cy="28" r="22" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="5" />
          <motion.circle
            cx="28" cy="28" r="22"
            fill="none" stroke={color} strokeWidth="5" strokeLinecap="round"
            strokeDasharray={2 * Math.PI * 22}
            initial={{ strokeDashoffset: 2 * Math.PI * 22 }}
            animate={{ strokeDashoffset: 2 * Math.PI * 22 * (1 - pct / 100) }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold" style={{ color }}>{score}</span>
        </div>
      </div>
      <div>
        <p className="text-xs text-white/30 mb-0.5">{label}</p>
        <p className="text-sm font-semibold" style={{ color }}>
          {score >= 80 ? 'Excellent' : score >= 65 ? 'Satisfactory' : 'Needs Attention'}
        </p>
      </div>
    </div>
  );
}

// ── Main Report ───────────────────────────────────────────────────────────────

export function CampaignReport({
  startData, readinessData, ambiguityData, planData, qaData, approvedAssumptions, onBack,
}: ReportProps) {
  const printRef = useRef<HTMLDivElement>(null);

  const brief = startData.structured_brief;
  const { gap_report, compliance_report, kpi_report, readiness_score } = readinessData;
  const { execution_plan, channel_strategy, simulation_report, timeline_plan, asset_checklist, measurement_plan } = planData;
  const { qa_report, consistency_report, final_compliance_report, handoff_packet } = qaData;
  const campaignName = String(brief.campaign_name ?? handoff_packet.campaign_name ?? 'Campaign');

  // Auto-incrementing section counter — reset each render
  let _sec = 0;
  const S = () => String(++_sec).padStart(2, '0');

  const handleDownloadJSON = () => {
    const report = {
      generated_at: new Date().toISOString(),
      campaign_name: campaignName,
      brief, readiness: { readiness_score, gap_report, compliance_report, kpi_report },
      approved_assumptions: approvedAssumptions,
      plan: { channel_strategy, execution_plan, timeline_plan, asset_checklist },
      simulation: simulation_report,
      qa: { qa_report, consistency_report, final_compliance_report },
      handoff: handoff_packet,
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${campaignName.replace(/\s+/g, '_')}_Readiness_Report_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => window.print();

  return (
    <div className="flex flex-col gap-0" ref={printRef}>

      {/* ── Report Header ── */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative rounded-2xl overflow-hidden mb-8"
        style={{ background: 'linear-gradient(135deg, rgba(201,168,76,0.12) 0%, rgba(0,0,0,0) 60%)', border: '1px solid rgba(201,168,76,0.15)' }}
      >
        {/* Decorative corner lines */}
        <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 rounded-tl-2xl" style={{ borderColor: 'rgba(201,168,76,0.4)' }} />
        <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 rounded-br-2xl" style={{ borderColor: 'rgba(201,168,76,0.4)' }} />

        <div className="p-8">
          <div className="flex items-start justify-between gap-6">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-gold-500 font-semibold mb-3">
                Campaign Readiness Copilot · Launch Readiness Report
              </p>
              <h1 className="text-3xl font-bold text-white mb-3 leading-tight">{campaignName}</h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs px-3 py-1 rounded-full font-semibold border"
                  style={{ background: 'rgba(201,168,76,0.12)', color: '#C9A84C', borderColor: 'rgba(201,168,76,0.3)' }}>
                  {String(handoff_packet.status ?? 'READY FOR APPROVAL')}
                </span>
                {handoff_packet.launch_date && (
                  <span className="text-xs text-white/40">Launch: {String(handoff_packet.launch_date)}</span>
                )}
                <span className="text-xs text-white/30">Generated: {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
              </div>
            </div>
            <div className="flex flex-col items-end gap-3 shrink-0">
              <div className="flex gap-2">
                <motion.button
                  onClick={handlePrint}
                  className="btn-ghost flex items-center gap-2 text-xs px-4 py-2"
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                >
                  <Printer size={13} /> Print
                </motion.button>
                <motion.button
                  onClick={handleDownloadJSON}
                  className="btn-primary flex items-center gap-2 text-xs px-4 py-2"
                  whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                >
                  <Download size={13} /> Download
                </motion.button>
              </div>
              <button onClick={onBack} className="text-xs text-white/30 hover:text-white/60 flex items-center gap-1 transition-colors">
                ← Back to workflow
              </button>
            </div>
          </div>

          {/* Score row */}
          <div className="grid grid-cols-3 gap-3 mt-6">
            <ScoreBadge score={readiness_score} label="Brief Readiness" />
            <ScoreBadge score={qa_report.alignment_score ?? 0} label="Plan Alignment" />
            <ScoreBadge score={Number((consistency_report as any).consistency_score ?? 92)} label="Channel Consistency" />
          </div>
        </div>
      </motion.div>

      {/* ── Warning notice ── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex items-start gap-3 px-4 py-3 rounded-xl mb-8"
        style={{ background: 'rgba(234,179,8,0.06)', border: '1px solid rgba(234,179,8,0.15)' }}
      >
        <AlertTriangle size={15} className="text-yellow-500 shrink-0 mt-0.5" />
        <p className="text-xs text-yellow-500/80 leading-relaxed">
          {String(handoff_packet.important_notice ?? '⚠️ This campaign has NOT been launched. All content requires manager approval before any execution begins.')}
        </p>
      </motion.div>

      {/* ── Executive Summary ── */}
      <Section num={S()} title="Executive Summary">
        <div className="glass rounded-xl p-5">
          <p className="text-sm text-white/70 leading-relaxed">
            {String(handoff_packet.executive_summary ?? execution_plan.campaign_overview ?? '—')}
          </p>
          {startData.campaign_intent && (
            <div className="flex flex-wrap gap-2 mt-4">
              {Object.entries(startData.campaign_intent)
                .filter(([k]) => k !== '_source')
                .map(([k, v]) => (
                  <span key={k} className="text-xs px-2.5 py-1 rounded-full"
                    style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)' }}>
                    <span style={{ color: 'rgba(255,255,255,0.25)' }}>{k.replace(/_/g, ' ')}: </span>{String(v)}
                  </span>
                ))}
            </div>
          )}
        </div>
      </Section>

      {/* ── Campaign Brief ── */}
      <Section num={S()} title="Campaign Brief">
        <div className="glass rounded-xl divide-y divide-white/5">
          <Row icon={<Target size={14} />} label="Business Objective" value={String(brief.business_objective ?? '—')} />
          <Row icon={<Users size={14} />} label="Target Audience" value={
            typeof brief.target_audience === 'object'
              ? Object.values(brief.target_audience as Record<string, string>).filter(Boolean).join(' · ')
              : String(brief.target_audience ?? '—')
          } />
          <Row icon={<Megaphone size={14} />} label="Channels" value={
            Array.isArray(brief.channels) ? brief.channels.join(', ') : String(brief.channels ?? '—')
          } />
          <Row icon={<DollarSign size={14} />} label="Budget" value={
            typeof brief.budget === 'object'
              ? `$${((brief.budget as any).total ?? 0).toLocaleString()} ${(brief.budget as any).currency ?? ''}`
              : String(brief.budget ?? '—')
          } />
          <Row icon={<Calendar size={14} />} label="Timeline" value={
            typeof brief.timeline === 'object'
              ? `${(brief.timeline as any).start} → ${(brief.timeline as any).end}`
              : String(brief.timeline ?? '—')
          } />
          <Row icon={<BarChart2 size={14} />} label="Success Metrics" value={
            typeof brief.success_metrics === 'object'
              ? `${(brief.success_metrics as any).primary}: ${(brief.success_metrics as any).target} (baseline: ${(brief.success_metrics as any).baseline})`
              : String(brief.success_metrics ?? '—')
          } />
          {Array.isArray(brief.constraints) && brief.constraints.length > 0 && (
            <Row icon={<AlertOctagon size={14} />} label="Constraints" value={
              <ul className="list-disc list-inside space-y-0.5">
                {brief.constraints.map((c, i) => <li key={i}>{String(c)}</li>)}
              </ul>
            } />
          )}
        </div>
      </Section>

      {/* ── Readiness Assessment ── */}
      <Section num={S()} title="Readiness Assessment">
        {/* Overview */}
        <div className="glass rounded-xl p-4 mb-3">
          <p className="text-sm text-white/60 leading-relaxed">{String(gap_report.overall_assessment ?? '—')}</p>
          {Array.isArray(gap_report.strengths) && gap_report.strengths.length > 0 && (
            <div className="mt-3 flex flex-col gap-1.5">
              {(gap_report.strengths as string[]).map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <CheckCircle2 size={12} className="text-emerald-400 shrink-0" />
                  <p className="text-xs text-white/50">{s}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Gaps table */}
        {Array.isArray(gap_report.gaps) && gap_report.gaps.length > 0 && (
          <div>
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-2">Brief Gaps</p>
            <div className="rounded-xl overflow-hidden border border-white/6">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                    {['Gap Field', 'Severity', 'Description', 'Recommendation'].map(h => (
                      <th key={h} className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(gap_report.gaps as any[]).map((g, i) => (
                    <tr key={i} className="border-t border-white/5">
                      <td className="px-4 py-3 text-white/80 font-medium text-xs">{g.field}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${severityBadge(g.severity)}`}>{g.severity}</span>
                      </td>
                      <td className="px-4 py-3 text-white/50 text-xs leading-relaxed">{g.description}</td>
                      <td className="px-4 py-3 text-gold-400 text-xs leading-relaxed">{g.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Compliance risks */}
        {Array.isArray((compliance_report as any).risks) && (
          <div className="mt-3">
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-2">Compliance Risks</p>
            <div className="rounded-xl overflow-hidden border border-white/6">
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                    {['Category', 'Severity', 'Risk', 'Mitigation'].map(h => (
                      <th key={h} className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {((compliance_report as any).risks as any[]).map((r, i) => (
                    <tr key={i} className="border-t border-white/5">
                      <td className="px-4 py-3 text-white/80 font-medium text-xs">{r.category}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${severityBadge(r.severity)}`}>{r.severity}</span>
                      </td>
                      <td className="px-4 py-3 text-white/50 text-xs">{r.description}</td>
                      <td className="px-4 py-3 text-gold-400 text-xs">{r.mitigation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* KPI */}
        {kpi_report.primary_kpi && (
          <div className="mt-3 glass rounded-xl p-4">
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-3">KPI Readiness</p>
            <div className="flex items-center gap-6 mb-3">
              <div>
                <p className="text-xs text-white/30 mb-0.5">Primary KPI</p>
                <p className="text-sm font-semibold text-white">{String((kpi_report.primary_kpi as any).metric)}</p>
              </div>
              <div>
                <p className="text-xs text-white/30 mb-0.5">Target</p>
                <p className="text-sm font-bold text-gold-400">{String((kpi_report.primary_kpi as any).target)}</p>
              </div>
              <div>
                <p className="text-xs text-white/30 mb-0.5">Baseline</p>
                <p className="text-sm font-semibold text-white/60">{String((kpi_report.primary_kpi as any).baseline)}</p>
              </div>
              <div>
                <p className="text-xs text-white/30 mb-0.5">Measurability</p>
                <p className="text-sm font-semibold text-emerald-400">{String((kpi_report.primary_kpi as any).measurability ?? '—')}</p>
              </div>
            </div>
            {Array.isArray(kpi_report.measurement_gaps) && kpi_report.measurement_gaps.length > 0 && (
              <div className="flex flex-col gap-1">
                {kpi_report.measurement_gaps.map((g, i) => (
                  <div key={i} className="flex gap-2">
                    <AlertTriangle size={11} className="text-yellow-400 shrink-0 mt-0.5" />
                    <p className="text-xs text-yellow-400/70">{String(g)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Section>

      {/* ── Approved Assumptions ── */}
      {approvedAssumptions.length > 0 && (
        <Section num={S()} title="Approved Assumptions">
          <div className="flex flex-col gap-2">
            {approvedAssumptions.map((a, i) => (
              <div key={i} className="glass rounded-xl p-4 flex gap-3">
                <CheckCircle2 size={15} className="text-gold-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-white/80 mb-1">{a.assumption}</p>
                  <div className="flex gap-4 text-xs">
                    <span className="text-white/30">Confidence: <span className={
                      a.confidence === 'High' ? 'text-emerald-400' : a.confidence === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                    }>{a.confidence}</span></span>
                    <span className="text-white/30">Source: {a.source}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Channel Strategy & Execution ── */}
      <Section num={S()} title="Channel Strategy & Execution Plan">
        {/* Strategy summary */}
        <div className="glass rounded-xl p-4 mb-3">
          <p className="text-sm text-white/70 leading-relaxed">{String(execution_plan.strategy_summary ?? execution_plan.campaign_overview ?? '—')}</p>
        </div>

        {/* Channel mix */}
        {Array.isArray((channel_strategy as any)?.channels) && (
          <div className="mb-3">
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-2">Channel Breakdown</p>
            <div className="rounded-xl overflow-hidden border border-white/6">
              <table className="w-full">
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                    {['Channel', 'Budget', 'Role', 'KPIs', 'Cadence'].map(h => (
                      <th key={h} className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {((channel_strategy as any).channels as any[]).map((ch, i) => (
                    <tr key={i} className="border-t border-white/5">
                      <td className="px-4 py-3 text-white/80 font-semibold text-xs">{ch.channel}</td>
                      <td className="px-4 py-3 text-gold-400 font-bold text-xs">${(ch.budget as number)?.toLocaleString()}</td>
                      <td className="px-4 py-3 text-white/50 text-xs">{ch.role}</td>
                      <td className="px-4 py-3 text-white/50 text-xs">{Array.isArray(ch.kpis) ? (ch.kpis as string[]).join(', ') : '—'}</td>
                      <td className="px-4 py-3 text-white/40 text-xs">{ch.cadence ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Phases */}
        {Array.isArray(execution_plan.phases) && execution_plan.phases.length > 0 && (
          <div>
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-2">Execution Phases</p>
            <div className="flex flex-col gap-2">
              {(execution_plan.phases as any[]).map((ph, i) => (
                <div key={i} className="glass rounded-xl p-4 flex gap-4">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 font-bold text-sm"
                    style={{ background: 'linear-gradient(135deg, #C9A84C, #A8893D)', color: '#0a0a0a' }}>
                    {ph.phase}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-semibold text-white">{ph.name}</p>
                      <div className="flex gap-3 text-xs text-white/30">
                        <span className="flex items-center gap-1"><Clock size={11} /> Weeks {ph.weeks}</span>
                        <span>Owner: {ph.owner}</span>
                      </div>
                    </div>
                    {Array.isArray(ph.activities) && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {(ph.activities as string[]).map((act, j) => (
                          <span key={j} className="text-xs px-2 py-0.5 rounded-full" style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)' }}>
                            {act}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Section>

      {/* ── Asset Checklist ── */}
      {Array.isArray((asset_checklist as any)?.assets) && (asset_checklist as any).assets.length > 0 && (
        <Section num={S()} title="Asset Checklist">
          <div className="rounded-xl overflow-hidden border border-white/6 mb-3">
            <table className="w-full text-sm">
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                  {['Asset', 'Channel', 'Format', 'Owner', 'Deadline', 'Status'].map(h => (
                    <th key={h} className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {((asset_checklist as any).assets as any[]).map((a: any, i: number) => {
                  const statusColors: Record<string, string> = {
                    not_started: 'bg-white/5 text-white/40 border-white/10',
                    in_progress: 'bg-yellow-950 text-yellow-400 border-yellow-800',
                    done: 'bg-emerald-950 text-emerald-400 border-emerald-800',
                    complete: 'bg-emerald-950 text-emerald-400 border-emerald-800',
                    blocked: 'bg-red-950 text-red-400 border-red-800',
                  };
                  const sc = statusColors[String(a.status ?? 'not_started').toLowerCase()] ?? statusColors.not_started;
                  return (
                    <tr key={i} className="border-t border-white/5">
                      <td className="px-4 py-3 text-white/80 font-medium text-xs">{a.asset_name}</td>
                      <td className="px-4 py-3 text-white/50 text-xs">{a.channel ?? '—'}</td>
                      <td className="px-4 py-3 text-white/40 text-xs">{a.format ?? '—'}</td>
                      <td className="px-4 py-3 text-white/50 text-xs">{a.owner_role ?? '—'}</td>
                      <td className="px-4 py-3 text-white/40 text-xs">{a.deadline ?? '—'}</td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full border ${sc}`}>
                          {String(a.status ?? 'not started').replace(/_/g, ' ')}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {(asset_checklist as any).total_assets != null && (
            <p className="text-xs text-white/30">Total assets: {String((asset_checklist as any).total_assets)}</p>
          )}
        </Section>
      )}

      {/* ── Timeline Workback ── */}
      {Array.isArray((timeline_plan as any)?.timeline) && (timeline_plan as any).timeline.length > 0 && (
        <Section num={S()} title="Timeline Workback">
          <div className="flex flex-col gap-2 mb-3">
            {((timeline_plan as any).timeline as any[]).map((m: any, i: number) => {
              const typeColors: Record<string, string> = {
                launch: '#C9A84C',
                deadline: '#ef4444',
                review: '#60a5fa',
                checkpoint: '#a78bfa',
              };
              const dot = typeColors[String(m.type ?? 'checkpoint').toLowerCase()] ?? '#60a5fa';
              return (
                <div key={i} className="glass rounded-xl px-4 py-3 flex items-center gap-4">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: dot }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-white/80">{m.milestone}</p>
                    {Array.isArray(m.dependencies) && m.dependencies.length > 0 && (
                      <p className="text-xs text-white/30 mt-0.5">Depends on: {(m.dependencies as string[]).join(', ')}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-4 shrink-0 text-xs text-white/40">
                    {m.date && <span className="flex items-center gap-1"><Calendar size={11} /> {m.date}</span>}
                    {m.owner_role && <span>{m.owner_role}</span>}
                    <span className="px-2 py-0.5 rounded-full border text-xs" style={{ borderColor: `${dot}40`, color: dot, background: `${dot}10` }}>
                      {String(m.type ?? 'checkpoint')}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
          {(timeline_plan as any).critical_path?.length > 0 && (
            <div className="glass rounded-xl p-4">
              <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-2">Critical Path</p>
              <div className="flex flex-wrap gap-2">
                {((timeline_plan as any).critical_path as string[]).map((item: string, i: number) => (
                  <span key={i} className="text-xs px-2.5 py-1 rounded-full"
                    style={{ background: 'rgba(201,168,76,0.1)', color: '#C9A84C', border: '1px solid rgba(201,168,76,0.2)' }}>
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}
        </Section>
      )}

      {/* ── Measurement Plan ── */}
      {measurement_plan && Object.keys(measurement_plan).some(k => k !== '_source' && (measurement_plan as any)[k]) && (
        <Section num={S()} title="Measurement Plan">
          <div className="grid grid-cols-2 gap-3 mb-3">
            {measurement_plan.primary_kpi && (
              <div className="glass rounded-xl p-4">
                <p className="text-xs text-white/30 mb-1">Primary KPI</p>
                <p className="text-sm font-semibold text-white">{String(measurement_plan.primary_kpi)}</p>
                <div className="flex gap-4 mt-2 text-xs text-white/40">
                  {measurement_plan.baseline != null && <span>Baseline: <span className="text-white/60">{String(measurement_plan.baseline)}</span></span>}
                  {measurement_plan.target != null && <span>Target: <span className="text-gold-400 font-semibold">{String(measurement_plan.target)}</span></span>}
                </div>
              </div>
            )}
            {measurement_plan.measurement_framework && (
              <div className="glass rounded-xl p-4">
                <p className="text-xs text-white/30 mb-1">Measurement Framework</p>
                <p className="text-sm text-white/70 leading-relaxed">{String(measurement_plan.measurement_framework)}</p>
              </div>
            )}
          </div>
          <div className="glass rounded-xl divide-y divide-white/5">
            {measurement_plan.measurement_window && (
              <Row icon={<Calendar size={14} />} label="Measurement Window" value={String(measurement_plan.measurement_window)} />
            )}
            {measurement_plan.reporting_cadence && (
              <Row icon={<Clock size={14} />} label="Reporting Cadence" value={String(measurement_plan.reporting_cadence)} />
            )}
            {measurement_plan.control_strategy && (
              <Row icon={<ShieldCheck size={14} />} label="Control Strategy" value={String(measurement_plan.control_strategy)} />
            )}
            {Array.isArray(measurement_plan.data_sources) && measurement_plan.data_sources.length > 0 && (
              <Row icon={<Layers size={14} />} label="Data Sources" value={
                <div className="flex flex-wrap gap-1.5 mt-0.5">
                  {(measurement_plan.data_sources as string[]).map((src, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded-full"
                      style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.5)' }}>{src}</span>
                  ))}
                </div>
              } />
            )}
            {measurement_plan.owner && (
              <Row icon={<Users size={14} />} label="Owner" value={String(measurement_plan.owner)} />
            )}
          </div>
          {Array.isArray(measurement_plan.notes) && measurement_plan.notes.length > 0 && (
            <div className="mt-3 flex flex-col gap-1.5">
              {(measurement_plan.notes as string[]).map((note, i) => (
                <div key={i} className="flex items-start gap-2">
                  <AlertTriangle size={11} className="text-yellow-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-yellow-400/70">{note}</p>
                </div>
              ))}
            </div>
          )}
        </Section>
      )}

      {/* ── Market Uplift Simulation ── */}
      {Array.isArray(simulation_report.scenarios) && simulation_report.scenarios.length > 0 && (
        <Section num={S()} title="Market Uplift Simulation">
          <div className="rounded-xl overflow-hidden border border-white/6 mb-3">
            <table className="w-full">
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                  {['Scenario', 'Probability', 'Conversion Rate', 'Accounts', 'Revenue Impact', 'Key Driver'].map(h => (
                    <th key={h} className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(simulation_report.scenarios as any[]).map((sc, i) => (
                  <tr key={i} className={`border-t border-white/5 ${sc.name === 'Base Case' ? 'bg-gold-950/10' : ''}`}>
                    <td className="px-4 py-3">
                      <p className="text-xs font-bold text-white">{sc.name}</p>
                      {sc.name === 'Base Case' && <span className="text-xs text-gold-400">★ Recommended</span>}
                    </td>
                    <td className="px-4 py-3 text-white/60 text-xs">{sc.probability}</td>
                    <td className="px-4 py-3 text-white/80 font-semibold text-xs">{sc.conversion_rate}</td>
                    <td className="px-4 py-3 text-white/80 text-xs">{sc.accounts_converted}</td>
                    <td className="px-4 py-3 text-gold-400 font-bold text-xs">{sc.revenue_impact}</td>
                    <td className="px-4 py-3 text-white/40 text-xs">{sc.key_driver}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex gap-4">
            {simulation_report.expected_value && (
              <div className="glass rounded-xl px-5 py-3 flex-1">
                <p className="text-xs text-white/30 mb-0.5">Expected Revenue</p>
                <p className="text-xl font-bold text-white">{simulation_report.expected_value}</p>
              </div>
            )}
            {simulation_report.roi && (
              <div className="glass rounded-xl px-5 py-3 flex-1">
                <p className="text-xs text-white/30 mb-0.5">Campaign ROI</p>
                <p className="text-xl font-bold text-emerald-400">{simulation_report.roi}</p>
              </div>
            )}
            {simulation_report.recommendation && (
              <div className="glass rounded-xl px-5 py-3 flex-2" style={{ flex: 2 }}>
                <p className="text-xs text-white/30 mb-0.5">AI Recommendation</p>
                <p className="text-sm text-white/70">{String(simulation_report.recommendation)}</p>
              </div>
            )}
          </div>
        </Section>
      )}

      {/* ── QA Findings ── */}
      <Section num={S()} title="QA Findings">
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="glass rounded-xl p-4">
            <p className="text-xs text-white/30 mb-1">Brief-to-Plan Alignment</p>
            <p className="text-3xl font-bold" style={{ color: scoreColor(qa_report.alignment_score ?? 0) }}>
              {qa_report.alignment_score}<span className="text-lg text-white/20">/100</span>
            </p>
            <p className="text-xs text-white/40 mt-1">{qa_report.overall_verdict}</p>
          </div>
          <div className="glass rounded-xl p-4">
            <p className="text-xs text-white/30 mb-1">Final Compliance Status</p>
            <p className="text-lg font-bold text-emerald-400">{String((final_compliance_report as any).status ?? '—')}</p>
            <p className="text-xs text-white/30 mt-1">Multi-channel consistency: {String((consistency_report as any).consistency_score ?? '—')}%</p>
          </div>
        </div>

        {/* Aligned items */}
        {Array.isArray(qa_report.aligned_items) && qa_report.aligned_items.length > 0 && (
          <div className="glass rounded-xl p-4 mb-3">
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-3">Aligned Items</p>
            <div className="grid grid-cols-2 gap-1.5">
              {qa_report.aligned_items.map((item, i) => (
                <div key={i} className="flex items-start gap-2">
                  <CheckCircle2 size={12} className="text-emerald-400 shrink-0 mt-0.5" />
                  <p className="text-xs text-white/60">{item}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* QA gaps */}
        {Array.isArray(qa_report.gaps) && qa_report.gaps.length > 0 && (
          <div className="glass rounded-xl p-4 border border-yellow-900/20">
            <p className="text-xs text-white/30 uppercase tracking-widest font-semibold mb-3">Gaps to Resolve</p>
            {qa_report.gaps.map((g, i) => (
              <div key={i} className="flex gap-3 py-2 border-b border-white/5 last:border-0">
                <AlertTriangle size={13} className="text-yellow-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-white">{g.issue} <span className="text-white/30 font-normal">({g.severity})</span></p>
                  <p className="text-xs text-gold-400 mt-0.5">{g.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* ── Stakeholder Handoff ── */}
      {handoff_packet.stakeholder_sections && (
        <Section num={S()} title="Stakeholder Handoff">
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(handoff_packet.stakeholder_sections as Record<string, string[]>).map(([team, items]) => (
              <div key={team} className="glass rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <Users size={13} className="text-gold-400" />
                  <p className="text-xs font-bold text-gold-400 uppercase tracking-wide">{team.replace(/_/g, ' ')}</p>
                </div>
                <ul className="flex flex-col gap-1.5">
                  {items.map((item, j) => (
                    <li key={j} className="flex items-start gap-2">
                      <ArrowRight size={10} className="text-gold-500 shrink-0 mt-1" />
                      <span className="text-xs text-white/60 leading-relaxed">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Risk Register ── */}
      {Array.isArray(handoff_packet.risk_register) && (
        <Section num={S()} title="Risk Register">
          <div className="rounded-xl overflow-hidden border border-white/6">
            <table className="w-full">
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.03)' }}>
                  <th className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">#</th>
                  <th className="text-left px-4 py-2 text-xs text-white/30 font-semibold uppercase tracking-wide">Risk</th>
                </tr>
              </thead>
              <tbody>
                {(handoff_packet.risk_register as string[]).map((r, i) => (
                  <tr key={i} className="border-t border-white/5">
                    <td className="px-4 py-3 text-white/30 text-xs">{i + 1}</td>
                    <td className="px-4 py-3 text-white/60 text-xs leading-relaxed">
                      <div className="flex items-start gap-2">
                        <AlertTriangle size={12} className="text-red-400 shrink-0 mt-0.5" />
                        {r}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {/* ── Next Steps ── */}
      {Array.isArray(handoff_packet.next_steps) && (
        <Section num={S()} title="Next Steps">
          <div className="flex flex-col gap-2">
            {(handoff_packet.next_steps as string[]).map((step, i) => (
              <div key={i} className="glass rounded-xl px-4 py-3 flex items-center gap-4">
                <span
                  className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                  style={{ background: 'linear-gradient(135deg, #C9A84C, #A8893D)', color: '#0a0a0a' }}
                >
                  {i + 1}
                </span>
                <p className="text-sm text-white/70">{step}</p>
                <ChevronRight size={14} className="text-white/20 ml-auto shrink-0" />
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* ── Footer ── */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-4 pt-6 border-t border-white/5 flex items-center justify-between"
      >
        <div>
          <p className="text-xs text-white/20">Campaign Readiness Copilot · AI-generated report</p>
          <p className="text-xs text-white/15 mt-0.5">All outputs require human review and manager approval before execution.</p>
        </div>
        <div className="flex gap-2">
          <motion.button
            onClick={handlePrint}
            className="btn-ghost flex items-center gap-2 text-xs px-4 py-2"
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
          >
            <Printer size={13} /> Print Report
          </motion.button>
          <motion.button
            onClick={handleDownloadJSON}
            className="btn-primary flex items-center gap-2 text-xs px-4 py-2"
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
          >
            <Download size={13} /> Download JSON
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
}
