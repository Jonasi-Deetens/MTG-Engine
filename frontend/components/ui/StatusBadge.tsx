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
  default: 'bg-[color:var(--theme-bg-secondary)] text-[color:var(--theme-text-secondary)] border-[color:var(--theme-border-default)]',
  success: 'bg-[color:var(--theme-status-success)]/20 text-[color:var(--theme-status-success)] border-[color:var(--theme-status-success)]/50',
  warning: 'bg-[color:var(--theme-status-warning)]/20 text-[color:var(--theme-status-warning)] border-[color:var(--theme-status-warning)]/50',
  error: 'bg-[color:var(--theme-status-error)]/20 text-[color:var(--theme-status-error)] border-[color:var(--theme-status-error)]/50',
  info: 'bg-[color:var(--theme-status-info)]/20 text-[color:var(--theme-status-info)] border-[color:var(--theme-status-info)]/50',
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

