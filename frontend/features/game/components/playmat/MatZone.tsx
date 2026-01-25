'use client';

import { ReactNode } from 'react';
import { BracketHeader } from '@/components/ui/play/NierUIElements';

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
      className={`mat-zone nier-zone ${className || ''}`.trim()}
    >
      <div className="mat-zone-header flex items-center justify-between gap-2">
        <BracketHeader>{title}</BracketHeader>
        {typeof count === 'number' && (
          <span className="text-[10px] uppercase tracking-[0.18em] text-[color:var(--theme-text-muted)]">
            {count}
          </span>
        )}
      </div>
      {children ? (
        children
      ) : (
        <div className="text-xs text-[color:var(--theme-text-secondary)] nier-card-slot flex items-center justify-center">
          {emptyLabel}
        </div>
      )}
    </section>
  );
}
