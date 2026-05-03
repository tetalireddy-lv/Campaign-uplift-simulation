import { motion } from 'framer-motion';
import { Brain, AlertTriangle, CheckCircle, Search, UserCheck } from 'lucide-react';
import type { PlanningHypothesis } from '../types/campaign';

interface Props {
  hypothesis: PlanningHypothesis;
  className?: string;
}

const ROWS = [
  { key: 'what_ai_believes', label: 'What AI Believes', icon: <Brain size={14} />, color: 'text-blue-400' },
  { key: 'evidence_from_brief', label: 'Evidence from Brief', icon: <CheckCircle size={14} />, color: 'text-emerald-400' },
  { key: 'risk_if_wrong', label: 'Risk If Wrong', icon: <AlertTriangle size={14} />, color: 'text-red-400' },
  { key: 'validation_needed', label: 'Validation Needed', icon: <Search size={14} />, color: 'text-yellow-400' },
  { key: 'manager_action_required', label: 'Manager Action Required', icon: <UserCheck size={14} />, color: 'text-gold-400' },
] as const;

export function PlanningHypothesisCard({ hypothesis, className = '' }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={`glass-gold rounded-2xl p-5 ${className}`}
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: 'rgba(201,168,76,0.15)' }}>
          <Brain size={16} className="text-gold-400" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-widest text-gold-500 font-semibold">Planning Hypothesis</p>
          <p className="text-xs text-white/30">AI reasoning transparency</p>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {ROWS.map(({ key, label, icon, color }) => {
          const value = hypothesis[key as keyof PlanningHypothesis];
          if (!value) return null;
          return (
            <div key={key} className="flex gap-3">
              <div className={`mt-0.5 shrink-0 ${color}`}>{icon}</div>
              <div>
                <p className={`text-xs font-semibold ${color} mb-0.5`}>{label}</p>
                <p className="text-sm text-white/70 leading-relaxed">{value}</p>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
