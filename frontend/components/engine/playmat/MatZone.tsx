'use client';

import { ReactNode } from 'react';

interface MatZoneProps {
  title: string;
  count?: number;
  emptyLabel?: string;
  className?: string;
  children?: ReactNode;
}

export function MatZone({ title, count, emptyLabel = 'Empty', className, children }: MatZoneProps) {
  return (
    <section
      className={`rounded-xl border border-[color:var(--theme-border)] bg-[color:var(--theme-bg-secondary)]/20 p-3 ${className || ''}`.trim()}
    >
      <div className="flex items-center justify-between text-xs uppercase tracking-wide text-[color:var(--theme-text-secondary)] mb-2">
        <span>{title}</span>
        {typeof count === 'number' && <span>{count}</span>}
      </div>
      {children ? (
        children
      ) : (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">{emptyLabel}</div>
      )}
    </section>
  );
}
