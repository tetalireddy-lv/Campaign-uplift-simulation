import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Edit3, MessageSquare, Scale, SendHorizonal } from 'lucide-react';

interface Action {
  label: string;
  variant: 'primary' | 'ghost' | 'danger' | 'outline';
  icon?: React.ReactNode;
  onClick: () => void;
  disabled?: boolean;
}

interface Props {
  title?: string;
  actions: Action[];
  className?: string;
}

const VARIANT_CLASSES: Record<Action['variant'], string> = {
  primary: 'btn-primary',
  ghost: 'btn-ghost',
  danger: 'btn-danger',
  outline: 'px-6 py-3 rounded-lg font-semibold text-sm border border-white/10 text-white/60 hover:border-white/20 hover:text-white transition-all duration-200',
};

export function ManagerActionPanel({ title = 'Manager Actions', actions, className = '' }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass rounded-2xl p-5 ${className}`}
    >
      <p className="text-xs uppercase tracking-widest text-white/30 font-semibold mb-4">{title}</p>
      <div className="flex flex-wrap gap-3">
        {actions.map((action, i) => (
          <motion.button
            key={i}
            onClick={action.onClick}
            disabled={action.disabled}
            className={`${VARIANT_CLASSES[action.variant]} flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed`}
            whileHover={action.disabled ? {} : { scale: 1.02 }}
            whileTap={action.disabled ? {} : { scale: 0.98 }}
          >
            {action.icon}
            {action.label}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

// Pre-built action sets
export const approveAction = (onClick: () => void, disabled?: boolean): Action => ({
  label: 'Approve & Continue',
  variant: 'primary',
  icon: <CheckCircle size={16} />,
  onClick,
  disabled,
});

export const rejectAction = (onClick: () => void): Action => ({
  label: 'Reject',
  variant: 'danger',
  icon: <XCircle size={16} />,
  onClick,
});

export const editAction = (onClick: () => void): Action => ({
  label: 'Edit',
  variant: 'ghost',
  icon: <Edit3 size={16} />,
  onClick,
});

export const clarifyAction = (onClick: () => void): Action => ({
  label: 'Request Clarification',
  variant: 'outline',
  icon: <MessageSquare size={16} />,
  onClick,
});

export const legalAction = (onClick: () => void): Action => ({
  label: 'Send to Legal',
  variant: 'outline',
  icon: <Scale size={16} />,
  onClick,
});

export const handoffAction = (onClick: () => void, disabled?: boolean): Action => ({
  label: 'Approve for Handoff',
  variant: 'primary',
  icon: <SendHorizonal size={16} />,
  onClick,
  disabled,
});
