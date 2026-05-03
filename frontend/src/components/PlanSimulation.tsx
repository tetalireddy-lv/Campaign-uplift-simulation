import { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, BarChart3, CheckCircle2, CheckSquare, Clock, Edit3, Layers, MessageSquare, ShieldAlert, TrendingUp, Users2 } from 'lucide-react';
import type { AudienceUpliftEntry, PlanResponse, SimulationAssumption, SimulationScenarioResult } from '../types/campaign';
import { PlanningHypothesisCard } from './PlanningHypothesisCard';
import { ManagerActionPanel } from './ManagerActionPanel';

interface Props {
  data: PlanResponse;
  onApprove: () => void;
  loading: boolean;
}

function isPercentMetric(metricName: string | undefined) {
  return Boolean(metricName && /rate|ctr|awareness/i.test(metricName));
}

function formatKpiValue(value: number | undefined, metricName: string | undefined) {
  if (value === undefined || Number.isNaN(value)) return '—';
  if (metricName && /roas/i.test(metricName)) return `${value.toFixed(1)}x`;
  if (isPercentMetric(metricName)) return `${value.toFixed(1)}%`;
  return value >= 100 ? value.toLocaleString() : value.toFixed(1);
}

function ScenarioCard({ scenario, delay, primaryKpi }: { scenario: SimulationScenarioResult; delay: number; primaryKpi?: string }) {
  const colorMap: Record<string, string> = {
    'Current Brief As-Is': 'border-red-900/60 bg-red-950/20',
    'Clarified Plan': 'border-gold-700/60 bg-gold-950/20 glow-gold',
    'Optimized Plan': 'border-emerald-800/60 bg-emerald-950/20',
  };
  const cls = colorMap[scenario.scenario] ?? 'border-white/10';

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`glass rounded-2xl p-5 border ${cls}`}
      whileHover={{ scale: 1.02, y: -2 }}
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="font-bold text-white">{scenario.scenario}</p>
          <p className="text-xs text-white/30 mt-0.5">Confidence: {scenario.confidence}</p>
        </div>
        <TrendingUp size={18} className="text-gold-400 mt-1" />
      </div>
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <p className="text-xs text-white/30 mb-0.5">Expected KPI</p>
          <p className="text-xl font-bold text-white">{formatKpiValue(scenario.expected_kpi_value, primaryKpi)}</p>
        </div>
        <div>
          <p className="text-xs text-white/30 mb-0.5">Market Uplift</p>
          <p className="text-xl font-bold text-emerald-400">{scenario.market_uplift_percent.toFixed(1)}%</p>
        </div>
      </div>
      <div className="p-3 rounded-lg bg-black/20">
        <p className="text-xs uppercase tracking-wide text-gold-400 mb-1">Scenario Reason</p>
        <p className="text-xs text-white/50 leading-relaxed">{scenario.reason}</p>
      </div>
    </motion.div>
  );
}

function AudienceMixCard({ segment, details, delay }: { segment: string; details: AudienceUpliftEntry; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass rounded-xl p-4 border border-white/5"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <p className="text-sm font-semibold text-white">{segment}</p>
          <p className="text-xs text-white/30 mt-0.5">{details.count.toLocaleString()} people</p>
        </div>
        <p className="text-lg font-bold text-gold-400">{details.pct}%</p>
      </div>
      <p className="text-xs text-white/55 leading-relaxed">{details.explanation}</p>
    </motion.div>
  );
}

function AssumptionRow({ assumption }: { assumption: SimulationAssumption }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/5 px-4 py-3">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
        <p className="text-sm font-semibold text-white">{assumption.field}</p>
        <span className={`text-[11px] px-2 py-0.5 rounded-full border ${assumption.editable_by_manager ? 'border-gold-700 text-gold-400 bg-gold-950/30' : 'border-white/10 text-white/40'}`}>
          {assumption.editable_by_manager ? 'Editable' : 'Locked'}
        </span>
      </div>
      <p className="text-sm text-white/70">{String(assumption.value)}</p>
      <p className="text-xs text-white/35 mt-1">{assumption.source}</p>
    </div>
  );
}

export function PlanSimulation({ data, onApprove, loading }: Props) {
  const [acceptedSimulation, setAcceptedSimulation] = useState(false);

  const { execution_plan, channel_strategy, simulation_report, measurement_plan } = data;
  const hypo = execution_plan.planning_hypothesis;
  const scenarios = (simulation_report.scenario_results ?? simulation_report.scenarios ?? []) as SimulationScenarioResult[];
  const audienceMix = (simulation_report.audience_uplift_mix ?? {}) as Record<string, AudienceUpliftEntry>;
  const assumptions = (simulation_report.assumptions_used ?? []) as SimulationAssumption[];
  const drivers = simulation_report.uplift_drivers ?? [];
  const blockers = simulation_report.uplift_blockers ?? [];
  const editableFields = simulation_report.manager_editable_fields ?? [];
  const primaryKpi = simulation_report.primary_kpi;

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Step 4 — Plan + Simulate</p>
        <h2 className="text-2xl font-bold text-white">Execution Plan & Uplift Scenarios</h2>
        <p className="text-white/40 text-sm mt-1">AI-generated plan ready for manager review. Not yet approved for execution.</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center gap-2 mb-3">
          <Layers size={16} className="text-gold-400" />
          <p className="text-sm font-semibold text-white">Campaign Strategy</p>
        </div>
        <p className="text-sm text-white/60 mb-4 leading-relaxed">{execution_plan.strategy_summary ?? execution_plan.campaign_overview ?? '—'}</p>

        {execution_plan.channel_mix && (
          <div className="grid grid-cols-3 gap-3">
            {Object.entries(execution_plan.channel_mix as Record<string, string>).map(([ch, pct]) => (
              <div key={ch} className="p-3 rounded-xl bg-white/5 text-center">
                <p className="text-lg font-bold text-gold-400">{pct}</p>
                <p className="text-xs text-white/40">{ch}</p>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.12 }}
        className="glass rounded-2xl p-6 border border-gold-900/30"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 mb-5">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-gold-500 font-semibold mb-1">Market Uplift Simulation</p>
            <h3 className="text-xl font-bold text-white">{simulation_report.simulation_mode ?? 'Scenario estimate'}</h3>
            <p className="text-sm text-white/45 mt-1">Confidence: {simulation_report.confidence_level ?? 'Medium'}</p>
          </div>
          <div className="flex items-start gap-3 rounded-xl border border-yellow-900/40 bg-yellow-950/15 px-4 py-3 max-w-xl">
            <AlertTriangle size={16} className="text-yellow-400 mt-0.5 shrink-0" />
            <p className="text-xs text-white/65 leading-relaxed">
              {simulation_report.warning ?? 'This is a scenario estimate, not a guaranteed forecast.'}
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-3">
          <div className="rounded-xl bg-black/20 p-4">
            <p className="text-xs text-white/30 mb-1">Primary KPI</p>
            <p className="text-sm font-semibold text-white leading-snug">{primaryKpi ?? '—'}</p>
          </div>
          <div className="rounded-xl bg-black/20 p-4">
            <p className="text-xs text-white/30 mb-1">Baseline KPI</p>
            <p className="text-xl font-bold text-white">{formatKpiValue(simulation_report.baseline_kpi_value, primaryKpi)}</p>
          </div>
          <div className="rounded-xl bg-black/20 p-4">
            <p className="text-xs text-white/30 mb-1">Target KPI</p>
            <p className="text-xl font-bold text-white">{formatKpiValue(simulation_report.target_kpi_value, primaryKpi)}</p>
          </div>
          <div className="rounded-xl bg-black/20 p-4">
            <p className="text-xs text-white/30 mb-1">Expected KPI</p>
            <p className="text-xl font-bold text-emerald-400">{formatKpiValue(simulation_report.expected_kpi_value, primaryKpi)}</p>
            <p className="text-xs text-white/35 mt-1">
              {simulation_report.market_uplift_percent !== undefined ? `${simulation_report.market_uplift_percent.toFixed(1)}% uplift` : '—'}
            </p>
          </div>
        </div>
      </motion.div>

      {Array.isArray(execution_plan.phases) && execution_plan.phases.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Clock size={15} className="text-blue-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Execution Phases</p>
          </div>
          <div className="flex flex-col gap-3">
            {(execution_plan.phases as Array<Record<string, unknown>>).map((phase, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="glass rounded-xl p-4"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-sm font-semibold text-white">Phase {String(phase.phase)}: {String(phase.name)}</p>
                    <p className="text-xs text-white/30">Weeks {String(phase.weeks)} · Owner: {String(phase.owner)}</p>
                  </div>
                </div>
                {Array.isArray(phase.activities) && (
                  <ul className="flex flex-col gap-1 mt-2">
                    {(phase.activities as string[]).map((act, j) => (
                      <li key={j} className="flex items-center gap-2 text-xs text-white/50">
                        <CheckSquare size={11} className="text-gold-500 shrink-0" />
                        {act}
                      </li>
                    ))}
                  </ul>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {scenarios.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 size={15} className="text-gold-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Market Uplift Scenarios</p>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {scenarios.map((scenario, index) => (
              <ScenarioCard key={`${scenario.scenario}-${index}`} scenario={scenario} delay={index * 0.08} primaryKpi={primaryKpi} />
            ))}
          </div>
          {(simulation_report.expected_campaign_revenue || simulation_report.roi !== undefined) && (
            <div className="glass rounded-xl p-4 mt-3 grid md:grid-cols-2 gap-4 items-center">
              <div>
                <p className="text-xs text-white/30 mb-0.5">Expected Campaign Revenue</p>
                <p className="text-xl font-bold text-white">
                  {simulation_report.expected_campaign_revenue ? `$${simulation_report.expected_campaign_revenue.toLocaleString()}` : '—'}
                </p>
              </div>
              <div className="text-left md:text-right">
                <p className="text-xs text-white/30 mb-0.5">Estimated ROI</p>
                <p className="text-xl font-bold text-emerald-400">
                  {typeof simulation_report.roi === 'number' ? `${simulation_report.roi.toFixed(1)}%` : (simulation_report.roi ?? '—')}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {Object.keys(audienceMix).length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Users2 size={15} className="text-blue-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Audience Uplift Mix</p>
          </div>
          <div className="grid md:grid-cols-2 xl:grid-cols-5 gap-3">
            {Object.entries(audienceMix).map(([segment, details], index) => (
              <AudienceMixCard
                key={segment}
                segment={segment.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase())}
                details={details}
                delay={index * 0.05}
              />
            ))}
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <ShieldAlert size={15} className="text-gold-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Assumptions Used</p>
          </div>
          <div className="flex flex-col gap-3">
            {assumptions.length > 0 ? assumptions.map((assumption, index) => (
              <AssumptionRow key={`${assumption.field}-${index}`} assumption={assumption} />
            )) : (
              <p className="text-sm text-white/45">No explicit assumptions were recorded for this simulation.</p>
            )}
          </div>
          {editableFields.length > 0 && (
            <p className="text-xs text-white/35 mt-4">Manager-editable fields: {editableFields.join(', ')}</p>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={15} className="text-emerald-400" />
              <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Uplift Drivers</p>
            </div>
            <div className="flex flex-col gap-2">
              {drivers.length > 0 ? drivers.map((driver, index) => (
                <div key={`${driver}-${index}`} className="rounded-xl bg-emerald-950/20 border border-emerald-900/30 px-4 py-3 text-sm text-white/70">
                  {driver}
                </div>
              )) : <p className="text-sm text-white/45">No major drivers highlighted yet.</p>}
            </div>
          </div>

          <div className="glass rounded-2xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle size={15} className="text-red-400" />
              <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">Uplift Blockers</p>
            </div>
            <div className="flex flex-col gap-2">
              {blockers.length > 0 ? blockers.map((blocker, index) => (
                <div key={`${blocker}-${index}`} className="rounded-xl bg-red-950/20 border border-red-900/30 px-4 py-3 text-sm text-white/70">
                  {blocker}
                </div>
              )) : <p className="text-sm text-white/45">No major blockers highlighted.</p>}
            </div>
          </div>

          <div className="glass rounded-2xl p-5">
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Measurement Plan</p>
            <p className="text-sm text-white/70 leading-relaxed">{String(measurement_plan.measurement_framework ?? 'Measurement framework pending.')}</p>
            <div className="grid grid-cols-2 gap-3 mt-4 text-xs text-white/45">
              <div>
                <p className="text-white/30 mb-1">Reporting Cadence</p>
                <p className="text-white/70">{String(measurement_plan.reporting_cadence ?? '—')}</p>
              </div>
              <div>
                <p className="text-white/30 mb-1">Control Strategy</p>
                <p className="text-white/70">{String(measurement_plan.control_strategy ?? '—')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {Array.isArray((channel_strategy as any)?.channels) && (
        <div>
          <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-3">Channel Details</p>
          <div className="flex flex-col gap-3">
            {((channel_strategy as any).channels as Array<Record<string, unknown>>).map((channel, index) => (
              <div key={index} className="glass rounded-xl p-4">
                <div className="flex items-start justify-between mb-2">
                  <p className="text-sm font-semibold text-white">{String(channel.channel)}</p>
                  <p className="text-sm font-bold text-gold-400">${(channel.budget as number)?.toLocaleString()}</p>
                </div>
                <p className="text-xs text-white/40 mb-2">{String(channel.role)}</p>
                {Array.isArray(channel.kpis) && (
                  <div className="flex flex-wrap gap-2">
                    {(channel.kpis as string[]).map((kpi, idx) => (
                      <span key={idx} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-white/50">{kpi}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {hypo && <PlanningHypothesisCard hypothesis={hypo} />}

      <ManagerActionPanel
        title="Step 4 — Manager Actions"
        actions={[
          {
            label: 'Edit Assumptions',
            variant: 'ghost',
            icon: <Edit3 size={16} />,
            onClick: () => alert(`Editable fields: ${editableFields.join(', ') || 'No editable fields recorded'}`),
          },
          {
            label: acceptedSimulation ? 'Simulation Accepted' : 'Accept Simulation',
            variant: 'outline',
            icon: <CheckCircle2 size={16} />,
            onClick: () => setAcceptedSimulation(true),
            disabled: acceptedSimulation,
          },
          {
            label: 'Continue to QA',
            variant: 'primary',
            icon: <BarChart3 size={16} />,
            onClick: onApprove,
            disabled: loading || !acceptedSimulation,
          },
          {
            label: 'Request Clarification',
            variant: 'outline',
            icon: <MessageSquare size={16} />,
            onClick: () => alert('Request clarification: tighten audience definition, channel roles, or KPI assumptions before continuing.'),
          },
        ]}
      />
    </div>
  );
}
