// frontend/components/ui/Card.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'bordered';
}

export function Card({ children, variant = 'default', className, ...props }: CardProps) {
  const variants = {
    default: 'bg-white border border-amber-200/50',
    elevated: 'bg-white border border-amber-200/50 shadow-xl shadow-amber-900/10',
    bordered: 'bg-white border-2 border-amber-500/50',
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

