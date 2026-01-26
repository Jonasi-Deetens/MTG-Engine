'use client';

// frontend/components/ui/Select.tsx

import React from 'react';
import { cn } from '@/lib/utils';

export interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  options?: SelectOption[];
  placeholder?: string;
}

export function Select({
  options,
  placeholder,
  className,
  disabled,
  children,
  ...props
}: SelectProps) {
  return (
    <select
      className={cn(
        className,
        'w-full px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)]',
        'border border-[color:var(--theme-input-border)] rounded-none',
        'text-xs font-mono uppercase tracking-[0.12em]',
        'hover:border-[color:var(--theme-accent-primary)]',
        'focus:border-[color:var(--theme-accent-primary)] focus:outline-none',
        'transition-all duration-200',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
      disabled={disabled}
      {...props}
    >
      {options ? (
        <>
          {placeholder && <option value="">{placeholder}</option>}
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </>
      ) : (
        children
      )}
    </select>
  );
}

