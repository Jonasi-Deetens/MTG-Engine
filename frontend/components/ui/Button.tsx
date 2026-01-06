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
  const baseStyles = 'font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center';
  
  const variants = {
    primary: 'bg-gradient-to-r from-amber-600 to-amber-500 hover:from-amber-500 hover:to-amber-400 text-white shadow-lg shadow-amber-900/50',
    secondary: 'bg-slate-700 hover:bg-slate-600 text-white',
    outline: 'border-2 border-amber-500 text-amber-500 hover:bg-amber-500 hover:text-white bg-transparent',
    ghost: 'bg-transparent hover:bg-slate-700 text-slate-300 hover:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    link: 'bg-transparent text-amber-400 hover:text-amber-300 underline-offset-4 hover:underline p-0',
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

