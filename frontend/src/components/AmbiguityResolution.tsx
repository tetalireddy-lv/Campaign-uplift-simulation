import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle, Check, ChevronDown, ChevronUp, Info } from 'lucide-react';
import type { AmbiguityResponse, Assumption, ClarificationQuestion } from '../types/campaign';
import { PlanningHypothesisCard } from './PlanningHypothesisCard';
import { ManagerActionPanel, approveAction } from './ManagerActionPanel';

interface Props {
  data: AmbiguityResponse;
  onApprove: (approved: Assumption[], answers: Record<string, string>) => void;
  loading: boolean;
}

function priorityColor(p: string) {
  const m: Record<string, string> = { critical: 'text-red-400 bg-red-950 border-red-800', high: 'text-orange-400 bg-orange-950 border-orange-800', medium: 'text-yellow-400 bg-yellow-950 border-yellow-800', low: 'text-emerald-400 bg-emerald-950 border-emerald-800' };
  return m[p] ?? m.medium;
}

function confidenceColor(c: string) {
  const m: Record<string, string> = { High: 'text-emerald-400', Medium: 'text-yellow-400', Low: 'text-red-400' };
  return m[c] ?? 'text-white/50';
}

export function AmbiguityResolution({ data, onApprove, loading }: Props) {
  const { clarification_questions, assumptions } = data;
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [approvedIds, setApprovedIds] = useState<Set<string>>(new Set());
  const [expandedQ, setExpandedQ] = useState<Set<string>>(new Set());

  const toggleApprove = (id: string) => {
    setApprovedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleExpand = (id: string) => {
    setExpandedQ(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleApprove = () => {
    const approved = assumptions.filter(a => approvedIds.has(a.id));
    onApprove(approved, answers);
  };

  return (
    <div className="flex flex-col gap-6">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <p className="text-xs uppercase tracking-[0.2em] text-gold-500 font-semibold mb-1">Step 3 — Resolve Ambiguity</p>
        <h2 className="text-2xl font-bold text-white">Clarifications & Assumptions</h2>
        <p className="text-white/40 text-sm mt-1">Answer questions, approve or reject AI assumptions, then proceed to planning.</p>
      </motion.div>

      {/* Clarification questions */}
      {clarification_questions.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <HelpCircle size={15} className="text-blue-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">
              Clarification Questions ({clarification_questions.length})
            </p>
          </div>
          <div className="flex flex-col gap-3">
            {clarification_questions.map((q: ClarificationQuestion) => {
              const isExpanded = expandedQ.has(q.id);
              return (
                <motion.div
                  key={q.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass rounded-xl overflow-hidden"
                >
                  <button
                    onClick={() => toggleExpand(q.id)}
                    className="w-full text-left p-4 flex items-start gap-3"
                  >
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${priorityColor(q.priority)} whitespace-nowrap mt-0.5`}>
                      {q.priority}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white">{q.question}</p>
                      <p className="text-xs text-white/30 mt-0.5">{q.category}</p>
                    </div>
                    <span className="text-white/30 shrink-0">
                      {isExpanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
                    </span>
                  </button>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 border-t border-white/5 pt-3">
                          <div className="flex gap-2 mb-2">
                            <Info size={13} className="text-white/30 shrink-0 mt-0.5" />
                            <p className="text-xs text-white/40">{q.impact}</p>
                          </div>
                          <textarea
                            value={answers[q.id] ?? ''}
                            onChange={e => setAnswers(prev => ({ ...prev, [q.id]: e.target.value }))}
                            placeholder="Your answer…"
                            className="w-full bg-black/20 border border-white/8 rounded-lg px-3 py-2 text-sm text-white/80 placeholder-white/20 resize-none focus:outline-none focus:border-gold-500/30 transition-colors"
                            rows={2}
                          />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </div>
        </div>
      )}

      {/* Assumptions */}
      {assumptions.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Info size={15} className="text-gold-400" />
            <p className="text-xs uppercase tracking-widest text-white/30 font-semibold">
              AI Assumptions — Select to Approve ({approvedIds.size}/{assumptions.length})
            </p>
          </div>
          <div className="flex flex-col gap-3">
            {assumptions.map((a: Assumption) => {
              const isApproved = approvedIds.has(a.id);
              return (
                <motion.button
                  key={a.id}
                  onClick={() => toggleApprove(a.id)}
                  className={`text-left glass rounded-xl p-4 border transition-all duration-200 ${
                    isApproved ? 'border-gold-500/30 glow-gold' : 'border-white/5 hover:border-white/10'
                  }`}
                  whileHover={{ scale: 1.005 }}
                  whileTap={{ scale: 0.998 }}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 transition-all ${
                      isApproved ? 'border-gold-500 bg-gold-500/20' : 'border-white/20'
                    }`}>
                      {isApproved && <Check size={11} className="text-gold-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white mb-1">{a.assumption}</p>
                      <div className="flex items-center gap-3 text-xs">
                        <span>Confidence: <span className={confidenceColor(a.confidence)}>{a.confidence}</span></span>
                        <span className="text-white/20">·</span>
                        <span className="text-white/30 truncate">{a.source}</span>
                      </div>
                      <p className="text-xs text-red-400/70 mt-1.5">If wrong: {a.if_wrong}</p>
                    </div>
                  </div>
                </motion.button>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <ManagerActionPanel
        title="Step 3 — Manager Actions"
        actions={[
          approveAction(handleApprove, loading),
          {
            label: 'Skip & Use All Assumptions',
            variant: 'ghost',
            onClick: () => onApprove(assumptions, answers),
            disabled: loading,
          },
        ]}
      />
    </div>
  );
}
