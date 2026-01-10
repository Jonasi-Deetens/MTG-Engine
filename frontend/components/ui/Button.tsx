// frontend/components/ui/Button.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'link';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className,
  disabled,
  ...props
}: ButtonProps) {
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer inline-flex items-center justify-center';
  
  const variants = {
    primary: 'bg-[color:var(--theme-button-primary-bg)] hover:bg-[color:var(--theme-button-primary-hover)] text-[color:var(--theme-button-primary-text)] shadow-lg shadow-black/20',
    secondary: 'bg-[color:var(--theme-button-secondary-bg)] hover:bg-[color:var(--theme-button-secondary-hover)] text-[color:var(--theme-button-secondary-text)] border border-[color:var(--theme-border-default)]',
    outline: 'border-2 border-[color:var(--theme-button-outline-border)] text-[color:var(--theme-button-outline-text)] hover:bg-[color:var(--theme-button-outline-hover)] hover:text-[color:var(--theme-button-outline-text)] bg-transparent',
    ghost: 'bg-transparent hover:bg-[color:var(--theme-button-ghost-hover)] text-[color:var(--theme-button-ghost-text)] hover:text-[color:var(--theme-text-primary)]',
    danger: 'bg-[color:var(--theme-status-error)] hover:opacity-90 text-white',
    link: 'bg-transparent text-[color:var(--theme-accent-primary)] hover:text-[color:var(--theme-accent-hover)] underline-offset-4 hover:underline p-0',
  };
  
  const sizes = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
          Loading...
        </span>
      ) : (
        children
      )}
    </button>
  );
}

