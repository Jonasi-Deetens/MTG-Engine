'use client';

// frontend/components/ui/EmptyState.tsx

import { LucideIcon } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actionHref?: string;
  className?: string;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  actionHref,
  className = '',
}: EmptyStateProps) {
  const iconSize = 64;
  const iconStrokeWidth = 1.5;

  return (
    <div className={`flex flex-col items-center justify-center py-16 px-4 text-center ${className}`}>
      <div className="mb-6 p-4 rounded-full bg-[color:var(--theme-bg-secondary)] border border-[color:var(--theme-border-default)]">
        <Icon 
          className="w-16 h-16 text-[color:var(--theme-text-muted)]" 
          strokeWidth={iconStrokeWidth}
        />
      </div>
      <h3 className="text-xl font-semibold text-[color:var(--theme-text-primary)] mb-2">{title}</h3>
      <p className="text-[color:var(--theme-text-secondary)] max-w-md mb-6">{description}</p>
      {(actionLabel && (onAction || actionHref)) && (
        <div>
          {actionHref ? (
            <a href={actionHref}>
              <Button variant="primary">{actionLabel}</Button>
            </a>
          ) : (
            <Button variant="primary" onClick={onAction}>
              {actionLabel}
            </Button>
          )}
        </div>
      )}
    </div>
  );
}

