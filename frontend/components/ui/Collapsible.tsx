'use client';

// frontend/components/ui/Collapsible.tsx

import { useState, ReactNode } from 'react';

interface CollapsibleProps {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export function Collapsible({ title, children, defaultOpen = false, className = '' }: CollapsibleProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`border border-[color:var(--theme-card-border)] rounded-lg ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2 flex items-center justify-between text-left hover:bg-[color:var(--theme-card-hover)] transition-colors"
      >
        <span className="font-medium text-[color:var(--theme-text-primary)]">{title}</span>
        <svg
          className={`w-5 h-5 text-[color:var(--theme-text-secondary)] transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {isOpen && (
        <div className="px-4 py-3 border-t border-[color:var(--theme-card-border)]">
          {children}
        </div>
      )}
    </div>
  );
}

