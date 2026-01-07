'use client';

// frontend/components/ui/StatusBadge.tsx

import { LucideIcon } from 'lucide-react';

interface StatusBadgeProps {
  label: string;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  icon?: LucideIcon;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const variantStyles = {
  default: 'bg-slate-700 text-slate-300 border-slate-600',
  success: 'bg-green-600/20 text-green-400 border-green-500/50',
  warning: 'bg-yellow-600/20 text-yellow-400 border-yellow-500/50',
  error: 'bg-red-600/20 text-red-400 border-red-500/50',
  info: 'bg-blue-600/20 text-blue-400 border-blue-500/50',
};

const sizeStyles = {
  sm: 'text-xs px-2 py-0.5',
  md: 'text-sm px-2.5 py-1',
  lg: 'text-base px-3 py-1.5',
};

export function StatusBadge({
  label,
  variant = 'default',
  icon: Icon,
  size = 'md',
  className = '',
}: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {Icon && <Icon className="w-3 h-3" strokeWidth={2.5} />}
      {label}
    </span>
  );
}

