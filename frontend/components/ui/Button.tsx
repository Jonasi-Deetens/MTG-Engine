// frontend/components/ui/Button.tsx

import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:
    | 'primary'
    | 'secondary'
    | 'outline'
    | 'ghost'
    | 'danger'
    | 'link'
    | 'nier-primary'
    | 'nier-secondary'
    | 'nier-ghost';
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
  const baseStyles =
    'font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer inline-flex items-center justify-center';
  
  const variants = {
    primary: 'bg-[color:var(--theme-button-primary-bg)] hover:bg-[color:var(--theme-button-primary-hover)] text-[color:var(--theme-button-primary-text)]',
    secondary: 'bg-[color:var(--theme-button-secondary-bg)] hover:bg-[color:var(--theme-button-secondary-hover)] text-[color:var(--theme-button-secondary-text)] border border-[color:var(--theme-border-default)]',
    outline: 'border-2 border-[color:var(--theme-button-outline-border)] text-[color:var(--theme-button-outline-text)] hover:bg-[color:var(--theme-button-outline-hover)] hover:text-[color:var(--theme-button-primary-text)] bg-transparent',
    ghost: 'bg-transparent hover:bg-[color:var(--theme-button-ghost-hover)] text-[color:var(--theme-button-ghost-text)] hover:text-[color:var(--theme-text-primary)]',
    danger: 'bg-[color:var(--theme-status-error)] hover:opacity-90 text-[color:var(--theme-text-primary)]',
    link: 'bg-transparent text-[color:var(--theme-accent-primary)] hover:text-[color:var(--theme-accent-hover)] underline-offset-4 hover:underline p-0',
    'nier-primary':
      "group relative rounded-none font-mono font-normal text-sm tracking-[0.2em] uppercase bg-[color:var(--play-text-primary)] !text-[color:var(--play-bg-primary)] transition-all duration-300 before:content-[''] before:absolute before:inset-0 before:z-0 before:border before:border-[color:var(--play-text-primary)] before:transition-all before:duration-300 after:content-[''] after:absolute after:top-1 after:left-1 after:right-[-1px] after:bottom-[-1px] after:z-0 after:border after:border-[color:color-mix(in srgb, var(--play-text-primary) 35%, transparent)] after:transition-all after:duration-300 hover:bg-[color:var(--play-bg-primary)] hover:!text-[color:var(--play-text-primary)] hover:before:bg-[color:var(--play-bg-primary)] hover:before:border-[color:var(--play-text-primary)] hover:after:opacity-0 px-8 py-3",
    'nier-secondary':
      "group relative rounded-none font-mono font-normal text-sm tracking-[0.2em] uppercase !text-[color:var(--play-text-primary)] transition-all duration-300 before:content-[''] before:absolute before:inset-0 before:z-0 before:border before:border-foreground before:transition-all before:duration-300 after:content-[''] after:absolute after:top-1 after:left-1 after:right-[-1px] after:bottom-[-1px] after:z-0 after:border after:border-foreground/30 after:transition-all after:duration-300 hover:before:bg-foreground hover:!text-[color:var(--play-bg-primary)] px-6 py-2",
    'nier-ghost':
      "group relative rounded-none font-mono font-normal text-sm tracking-[0.2em] uppercase !text-[color:var(--play-text-primary)] transition-all duration-300 before:content-[''] before:absolute before:inset-0 before:z-0 before:border before:border-transparent before:transition-all before:duration-300 after:content-[''] after:absolute after:top-1 after:left-1 after:right-[-1px] after:bottom-[-1px] after:z-0 after:border after:border-transparent after:transition-all after:duration-300 hover:before:border-foreground hover:before:bg-foreground hover:!text-[color:var(--play-bg-primary)] px-4 py-2",
  };
  
  const sizes = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  const isNierVariant = variant.startsWith('nier-');
  const sizeClassName = isNierVariant ? '' : sizes[size];
  
  return (
    <button
      className={cn(baseStyles, variants[variant], sizeClassName, className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className={cn('flex items-center gap-2', isNierVariant && 'relative z-10')}>
          <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-[color:var(--theme-button-primary-text)]"></span>
          Loading...
        </span>
      ) : isNierVariant ? (
        <span className="relative z-10">{children}</span>
      ) : (
        children
      )}
    </button>
  );
}

