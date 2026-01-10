'use client';

// frontend/components/ui/SearchInput.tsx

import { Search, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SearchInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  value: string;
  onChange: (value: string) => void;
  onSearch?: (value: string) => void;
  showClearButton?: boolean;
  iconPosition?: 'left' | 'right';
  size?: 'sm' | 'md' | 'lg';
}

export function SearchInput({
  value,
  onChange,
  onSearch,
  showClearButton = true,
  iconPosition = 'left',
  size = 'md',
  className,
  placeholder = 'Search...',
  ...props
}: SearchInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch(value);
    }
    props.onKeyDown?.(e);
  };

  const handleClear = () => {
    onChange('');
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-3 text-lg',
  };

  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  const paddingClasses = {
    sm: iconPosition === 'left' ? 'pl-9' : 'pr-9',
    md: iconPosition === 'left' ? 'pl-12' : 'pr-12',
    lg: iconPosition === 'left' ? 'pl-14' : 'pr-14',
  };

  return (
    <div className="relative w-full">
      {iconPosition === 'left' && (
        <Search
          className={cn(
            'absolute left-3 top-1/2 transform -translate-y-1/2 text-[color:var(--theme-accent-primary)] pointer-events-none',
            iconSizeClasses[size]
          )}
        />
      )}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={cn(
          'w-full bg-[color:var(--theme-input-bg)] border border-[color:var(--theme-input-border)] rounded-lg',
          'text-[color:var(--theme-input-text)] placeholder-theme-input-placeholder',
          'focus:outline-none focus:ring-2 focus:ring-[color:var(--theme-border-focus)] focus:border-[color:var(--theme-border-focus)]',
          'transition-all duration-200',
          sizeClasses[size],
          paddingClasses[size],
          showClearButton && value && 'pr-10',
          className
        )}
        {...props}
      />
      {showClearButton && value && (
        <button
          onClick={handleClear}
          className={cn(
            'absolute right-3 top-1/2 transform -translate-y-1/2 p-1',
            'hover:bg-[color:var(--theme-card-hover)] rounded transition-colors cursor-pointer',
            'text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]'
          )}
          aria-label="Clear search"
          type="button"
        >
          <X className={iconSizeClasses[size]} />
        </button>
      )}
      {iconPosition === 'right' && !showClearButton && (
        <Search
          className={cn(
            'absolute right-3 top-1/2 transform -translate-y-1/2 text-[color:var(--theme-accent-primary)] pointer-events-none',
            iconSizeClasses[size]
          )}
        />
      )}
    </div>
  );
}

