import { motion } from 'framer-motion';
import { PackageCheck, AlertTriangle, ArrowRight, Download, Users, FileText } from 'lucide-react';
import type { QAHandoffResponse } from '../types/campaign';

interface Props {
  data: QAHandoffResponse;
  onViewReport?: () => void;
}

export function HandoffPacket({ data, onViewReport }: Props) {
  const pkt = data.handoff_packet;

  const handleDownload = () => {
    const text = JSON.stringify(pkt, null, 2);
    const blob = new Blob([text], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `campaign-handoff-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Final — Handoff Packet</p>
        <h2 className="text-2xl font-bold text-white">{String(pkt.campaign_name ?? 'Campaign')}</h2>
        <div className="flex items-center gap-3 mt-2">
          <span className="text-xs px-3 py-1 rounded-full bg-gold-950 text-gold-400 border border-gold-800 font-semibold">
            {String(pkt.status ?? 'READY FOR REVIEW')}
          </span>
          {pkt.launch_date && (
            <span className="text-xs text-white/30">Launch: {String(pkt.launch_date)}</span>
          )}
        </div>
      </motion.div>

      {/* Warning banner */}
      <motion.div
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass rounded-xl p-4 border border-yellow-900/40"
      >
        <div className="flex items-start gap-3">
          <AlertTriangle size={18} className="text-yellow-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-yellow-400 mb-1">Campaign Not Launched</p>
            <p className="text-sm text-white/60 leading-relaxed">
              {String(pkt.important_notice ?? 'This packet requires manager approval before any execution begins.')}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Executive summary */}
      {pkt.executive_summary && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center gap-2 mb-3">
            <PackageCheck size={16} className="text-gold-400" />
            <p className="text-sm font-semibold text-white">Executive Summary</p>
          </div>
          <p className="text-sm text-white/70 leading-relaxed">{String(pkt.executive_summary)}</p>
        </motion.div>
      )}

      {pkt.market_uplift_summary && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.18 }}
          className="glass rounded-2xl p-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <PackageCheck size={16} className="text-gold-400" />
            <p className="text-sm font-semibold text-white">Market Uplift Summary</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4 mb-4">
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Simulation Mode</p>
              <p className="text-sm font-semibold text-white">{String(pkt.market_uplift_summary.simulation_mode ?? '—')}</p>
            </div>
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Confidence</p>
              <p className="text-sm font-semibold text-white">{String(pkt.market_uplift_summary.confidence_level ?? '—')}</p>
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-3 mb-4">
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Baseline KPI</p>
              <p className="text-sm font-semibold text-white">{String(pkt.market_uplift_summary.baseline_kpi?.name ?? 'KPI')}</p>
              <p className="text-lg font-bold text-white mt-1">{String(pkt.market_uplift_summary.baseline_kpi?.value ?? '—')}</p>
            </div>
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Target KPI</p>
              <p className="text-lg font-bold text-white">{String(pkt.market_uplift_summary.target_kpi ?? '—')}</p>
            </div>
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Expected KPI</p>
              <p className="text-lg font-bold text-emerald-400">{String(pkt.market_uplift_summary.expected_kpi ?? '—')}</p>
            </div>
            <div className="rounded-xl bg-black/20 p-4">
              <p className="text-xs text-white/30 mb-1">Market Uplift</p>
              <p className="text-lg font-bold text-gold-400">{String(pkt.market_uplift_summary.market_uplift_percent ?? '—')}%</p>
            </div>
          </div>

          {pkt.market_uplift_summary.audience_uplift_mix && (
            <div className="mb-4">
              <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Audience Uplift Mix</p>
              <div className="grid md:grid-cols-2 gap-3">
                {Object.entries(pkt.market_uplift_summary.audience_uplift_mix).map(([segment, details]) => (
                  <div key={segment} className="rounded-xl border border-white/5 bg-white/5 px-4 py-3">
                    <div className="flex items-start justify-between gap-3 mb-1">
                      <p className="text-sm font-semibold text-white">{segment.replace(/_/g, ' ')}</p>
                      <p className="text-sm font-bold text-gold-400">{String(details?.pct ?? '—')}%</p>
                    </div>
                    <p className="text-xs text-white/45">{String(details?.count ?? '—')} audience</p>
                    <p className="text-xs text-white/55 mt-2 leading-relaxed">{String(details?.explanation ?? '')}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Top Drivers</p>
              <div className="flex flex-col gap-2">
                {(pkt.market_uplift_summary.top_uplift_drivers ?? []).map((driver, index) => (
                  <div key={`${driver}-${index}`} className="rounded-xl bg-emerald-950/20 border border-emerald-900/30 px-4 py-3 text-sm text-white/70">
                    {driver}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Top Blockers</p>
              <div className="flex flex-col gap-2">
                {(pkt.market_uplift_summary.top_uplift_blockers ?? []).map((blocker, index) => (
                  <div key={`${blocker}-${index}`} className="rounded-xl bg-red-950/20 border border-red-900/30 px-4 py-3 text-sm text-white/70">
                    {blocker}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {pkt.market_uplift_summary.warning && (
            <div className="mt-4 rounded-xl border border-yellow-900/40 bg-yellow-950/15 px-4 py-3">
              <p className="text-sm text-yellow-200/85 leading-relaxed">{String(pkt.market_uplift_summary.warning)}</p>
            </div>
          )}
        </motion.div>
      )}

      {/* Stakeholder sections */}
      {pkt.stakeholder_sections && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Users size={15} className="text-blue-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">By Stakeholder</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(pkt.stakeholder_sections as Record<string, string[]>).map(([team, items], i) => (
              <motion.div
                key={team}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="glass rounded-xl p-4"
              >
                <p className="text-xs font-semibold text-gold-400 uppercase tracking-wide mb-3">
                  {team.replace(/_/g, ' ')}
                </p>
                <ul className="flex flex-col gap-2">
                  {items.map((item, j) => (
                    <li key={j} className="flex items-start gap-2">
                      <ArrowRight size={11} className="text-gold-500 shrink-0 mt-1" />
                      <span className="text-xs text-white/60">{item}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Risk register */}
      {Array.isArray(pkt.risk_register) && (
        <div>
          <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Risk Register</p>
          <div className="glass rounded-xl p-4 flex flex-col gap-2">
            {(pkt.risk_register as string[]).map((risk, i) => (
              <div key={i} className="flex items-start gap-3">
                <AlertTriangle size={13} className="text-red-400 shrink-0 mt-0.5" />
                <p className="text-sm text-white/60">{risk}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Next steps */}
      {Array.isArray(pkt.next_steps) && (
        <div>
          <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Next Steps</p>
          <div className="flex flex-col gap-2">
            {(pkt.next_steps as string[]).map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="flex items-center gap-4 glass rounded-xl px-4 py-3"
              >
                <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0"
                  style={{ background: 'linear-gradient(135deg, #C9A84C, #A8893D)', color: '#0a0a0a' }}>
                  {i + 1}
                </span>
                <p className="text-sm text-white/70">{step}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Download CTA */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
        className="flex gap-3 mt-2"
      >
        {onViewReport && (
          <motion.button
            onClick={onViewReport}
            className="btn-primary flex items-center gap-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{ background: 'linear-gradient(135deg, #C9A84C, #A8893D)' }}
          >
            <FileText size={16} />
            View Full Campaign Report
          </motion.button>
        )}
        <motion.button
          onClick={handleDownload}
          className="btn-ghost flex items-center gap-2"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Download size={16} />
          Download JSON
        </motion.button>
        <button
          onClick={() => window.print()}
          className="btn-ghost flex items-center gap-2"
        >
          Print / Share
        </button>
      </motion.div>
    </div>
  );
}
