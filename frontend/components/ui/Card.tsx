// frontend/components/ui/Card.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered';
}

export function Card({ children, variant = 'default', className, ...props }: CardProps) {
  const variants = {
    default: 'bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] hover:bg-[color:var(--theme-card-hover)] hover:border-[color:var(--theme-border-hover)] shadow-md hover:shadow-lg',
    elevated: 'bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] hover:bg-[color:var(--theme-card-hover)] hover:border-[color:var(--theme-border-hover)] shadow-xl hover:shadow-2xl shadow-black/10',
    bordered: 'bg-[color:var(--theme-card-bg)] border-2 border-[color:var(--theme-accent-primary)] hover:bg-[color:var(--theme-card-hover)] hover:border-theme-accent-hover shadow-md hover:shadow-lg',
  };
  
  return (
    <div
      className={cn(
        'rounded-lg p-6 transition-all duration-200',
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

