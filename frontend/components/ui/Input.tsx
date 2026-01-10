// frontend/components/ui/Input.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-1.5">
          {label}
        </label>
      )}
      <input
        className={cn(
          'w-full px-4 py-2 bg-[color:var(--theme-input-bg)] border border-[color:var(--theme-input-border)] rounded-lg',
          'text-[color:var(--theme-input-text)] placeholder-theme-input-placeholder',
          'focus:outline-none focus:ring-2 focus:ring-[color:var(--theme-border-focus)] focus:border-[color:var(--theme-border-focus)]',
          'transition-all duration-200',
          error && 'border-[color:var(--theme-status-error)] focus:ring-[color:var(--theme-status-error)]',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1.5 text-sm text-[color:var(--theme-status-error)]">{error}</p>
      )}
    </div>
  );
}

