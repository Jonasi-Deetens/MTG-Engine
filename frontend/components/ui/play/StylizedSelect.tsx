'use client';

import { useEffect, useRef, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StylizedSelectOption {
  value: string;
  label: string;
  icon?: React.ComponentType<{ className?: string }>;
}

interface StylizedSelectProps {
  options: StylizedSelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export function StylizedSelect({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  className,
  disabled = false,
}: StylizedSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);
  const selectedOption = options.find((opt) => opt.value === value);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
  };

  return (
    <div ref={selectRef} className={cn('relative', className)}>
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'w-full flex items-center justify-between gap-2 px-3 py-2',
          'bg-[color:var(--play-input-bg)] border border-[color:var(--play-border-default)] rounded-none',
          'text-[color:var(--play-text-primary)] text-xs font-mono uppercase tracking-[0.18em]',
          'hover:border-[color:var(--play-accent-primary)]',
          'focus:outline-none focus:ring-2 focus:ring-[color:var(--play-accent-primary)] focus:border-[color:var(--play-accent-primary)]',
          'transition-all duration-200 cursor-pointer',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <div className="flex items-center gap-2 min-w-0">
          {selectedOption?.icon && (
            <selectedOption.icon className="w-4 h-4 flex-shrink-0" />
          )}
          <span className="truncate">
            {selectedOption?.label || placeholder}
          </span>
        </div>
        <ChevronDown
          className={cn(
            'w-4 h-4 flex-shrink-0 text-[color:var(--play-text-secondary)] transition-transform',
            isOpen && 'transform rotate-180'
          )}
        />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-50 mt-1 w-full bg-[color:var(--play-card-bg)] border border-[color:var(--play-border-default)] rounded-none shadow-lg max-h-60 overflow-auto">
            {options.map((option) => {
              const Icon = option.icon;
              const isSelected = option.value === value;

              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option.value)}
                  className={cn(
                    'w-full flex items-center gap-2 px-3 py-2 text-xs text-left transition-colors uppercase tracking-[0.12em]',
                    'hover:bg-[color:var(--play-card-hover)]',
                    isSelected && 'bg-[color:var(--play-card-hover)] text-[color:var(--play-accent-primary)] font-semibold'
                  )}
                >
                  {Icon && <Icon className="w-4 h-4 flex-shrink-0" />}
                  <span className="truncate">{option.label}</span>
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
