'use client';

import React from 'react';
import { cn } from '@/lib/utils';

export function StylizedNativeSelect({
  className,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        'w-full px-2 py-1 bg-[color:var(--play-input-bg)] text-[color:var(--play-input-text)]',
        'border border-[color:var(--play-input-border)] rounded-none',
        'text-xs font-mono uppercase tracking-[0.12em]',
        'focus:border-[color:var(--play-accent-primary)] focus:outline-none',
        className
      )}
      {...props}
    />
  );
}
