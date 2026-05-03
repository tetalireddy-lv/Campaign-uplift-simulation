import { motion } from 'framer-motion';

interface Props {
  message?: string;
  subMessage?: string;
}

export function LoadingState({ message = 'AI is thinking...', subMessage }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center py-24 gap-6"
    >
      {/* Pulsing orb */}
      <div className="relative">
        <motion.div
          className="w-16 h-16 rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(201,168,76,0.4) 0%, rgba(201,168,76,0.05) 70%)' }}
          animate={{ scale: [1, 1.3, 1], opacity: [0.6, 1, 0.6] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute inset-0 rounded-full border border-gold-500/30"
          animate={{ scale: [1, 1.8], opacity: [0.8, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
        />
        <motion.div
          className="absolute inset-0 rounded-full border border-gold-500/20"
          animate={{ scale: [1, 2.2], opacity: [0.5, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut', delay: 0.5 }}
        />
      </div>

      {/* Animated dots */}
      <div className="flex gap-2">
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            className="w-2 h-2 rounded-full bg-gold-500"
            animate={{ opacity: [0.2, 1, 0.2], y: [0, -6, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>

      <div className="text-center">
        <p className="text-white/80 font-medium">{message}</p>
        {subMessage && <p className="text-white/40 text-sm mt-1">{subMessage}</p>}
      </div>
    </motion.div>
  );
}

export function SkeletonCard() {
  return (
    <div className="glass rounded-2xl p-5 space-y-3">
      <div className="shimmer h-4 rounded-lg w-1/3" />
      <div className="shimmer h-3 rounded-lg w-2/3" />
      <div className="shimmer h-3 rounded-lg w-1/2" />
      <div className="shimmer h-20 rounded-xl mt-4" />
    </div>
  );
}
