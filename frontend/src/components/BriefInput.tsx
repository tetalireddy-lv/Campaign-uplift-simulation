import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ChevronRight, FileText } from 'lucide-react';
// PNG design reference — place at src/assets/cred-design.png
import credDesign from '../assets/cred-design.png';

const SAMPLE_BRIEF = `Campaign Name: Q3 Enterprise Trial Conversion
Business Objective: Convert 200 enterprise trial accounts to paid subscriptions by end of Q3 2026
Target Audience: Enterprise IT decision-makers currently in 14-day trial, company size 500+
Key Message: Your team is already seeing results — lock in your progress before trial ends
Channels: Email, In-App, LinkedIn Ads
Budget: $85,000 USD
Timeline: June 1 - August 31, 2026
Success Metrics: 40% trial-to-paid conversion rate (baseline: 22%)
Constraints: No discount offers without VP approval. Must comply with enterprise data handling policy.`;

interface Props {
  onSubmit: (brief: string) => void;
  loading: boolean;
}

export function BriefInput({ onSubmit, loading }: Props) {
  const [brief, setBrief] = useState('');

  const handleSample = () => setBrief(SAMPLE_BRIEF);

  return (
    <div className="flex flex-col gap-8">
      {/* Hero section with PNG */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative rounded-3xl overflow-hidden"
        style={{ minHeight: 260 }}
      >
        {/* PNG background */}
        <img
          src={credDesign}
          alt="Campaign Copilot Design Reference"
          className="absolute inset-0 w-full h-full object-cover object-top opacity-30"
          style={{ filter: 'brightness(0.6) saturate(1.2)' }}
          onError={(e) => {
            // Hide if PNG not found — layout still works
            (e.target as HTMLImageElement).style.display = 'none';
          }}
        />
        {/* Gradient overlay */}
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to bottom, rgba(10,10,10,0.3) 0%, rgba(10,10,10,0.85) 100%)',
          }}
        />

        {/* Content */}
        <div className="relative z-10 p-8 flex flex-col justify-end h-full" style={{ minHeight: 260 }}>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xs uppercase tracking-[0.25em] text-gold-500 font-semibold mb-2"
          >
            Step 1 of 5 — Understand Brief
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-bold text-white mb-3 leading-tight"
          >
            crafted for the<br />
            <span className="gold-text">campaign-ready.</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-white/50 text-sm max-w-lg"
          >
            Paste your raw campaign brief below. The AI will parse, validate, and build a launch-ready execution plan — with you in control at every step.
          </motion.p>
        </div>
      </motion.div>

      {/* Input card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText size={16} className="text-gold-400" />
            <p className="text-sm font-semibold text-white">Raw Campaign Brief</p>
          </div>
          <button
            onClick={handleSample}
            className="text-xs text-gold-500 hover:text-gold-300 transition-colors underline underline-offset-2"
          >
            Load sample brief
          </button>
        </div>

        <textarea
          value={brief}
          onChange={e => setBrief(e.target.value)}
          placeholder="Paste your campaign brief here…&#10;&#10;Include: objective, audience, channels, budget, timeline, success metrics, constraints"
          className="w-full bg-transparent border border-white/8 rounded-xl p-4 text-sm text-white/80 placeholder-white/20 resize-none focus:outline-none focus:border-gold-500/40 transition-colors leading-relaxed"
          rows={10}
          disabled={loading}
        />

        <div className="flex items-center justify-between mt-4">
          <p className="text-xs text-white/20">
            {brief.length > 0 ? `${brief.length} characters` : 'Supports free-text or structured briefs'}
          </p>

          <motion.button
            onClick={() => brief.trim() && onSubmit(brief)}
            disabled={!brief.trim() || loading}
            className="btn-primary flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <Sparkles size={16} />
            {loading ? 'Parsing Brief…' : 'Parse & Analyze'}
            {!loading && <ChevronRight size={16} />}
          </motion.button>
        </div>
      </motion.div>

      {/* What happens next */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="grid grid-cols-3 gap-4"
      >
        {[
          { step: '01', title: 'Brief Parsed', desc: 'Extracts all structured fields from your raw text' },
          { step: '02', title: 'Gaps Detected', desc: 'Identifies missing info, compliance risks & KPI gaps' },
          { step: '03', title: 'Plan Generated', desc: 'Builds execution plan, channel strategy & uplift sim' },
        ].map(item => (
          <div key={item.step} className="glass rounded-xl p-4">
            <p className="text-xs text-gold-500 font-mono font-semibold mb-2">{item.step}</p>
            <p className="text-sm font-semibold text-white mb-1">{item.title}</p>
            <p className="text-xs text-white/40 leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}
