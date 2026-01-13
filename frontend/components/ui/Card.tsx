// frontend/components/ui/Card.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered' | 'bare';
}

export function Card({ children, variant = 'default', className, style, ...props }: CardProps) {
  const variants = {
    default: 'bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] hover:border-[color:var(--theme-border-hover)] shadow-md hover:shadow-lg',
    elevated: 'bg-[color:var(--theme-card-bg)] border-0',
    bordered: 'bg-[color:var(--theme-card-bg)] border-2 border-[color:var(--theme-accent-primary)] hover:border-theme-accent-hover shadow-md hover:shadow-lg',
    bare: 'card-elevated-shadow transition-all duration-200 group', // No padding, bg, or border - just shadow and hover behavior
  };
  
  // Base classes that apply to all variants except 'bare'
  const baseClasses = variant === 'bare' ? '' : 'rounded-lg p-6 transition-all duration-200';
  
  return (
    <div
      className={cn(
        baseClasses,
        variants[variant],
        variant === 'elevated' && 'card-elevated-shadow',
        className
      )}
      style={style}
      {...props}
    >
      {children}
    </div>
  );
}

