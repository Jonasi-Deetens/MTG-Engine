'use client';

// frontend/components/landing/LandingSearchBar.tsx

import { Search, X } from 'lucide-react';

interface LandingSearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSearch?: (query: string) => void;
}

export function LandingSearchBar({ searchQuery, onSearchChange, onSearch }: LandingSearchBarProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && onSearch) {
      onSearch(searchQuery);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-[color:var(--theme-accent-primary)]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search for Magic: The Gathering cards..."
          className="w-full pl-14 pr-12 py-4 bg-[color:var(--theme-input-bg)]/95 backdrop-blur-sm text-[color:var(--theme-input-text)] text-lg rounded-lg border-2 focus:border-[color:var(--theme-border-focus)] focus:outline-none shadow-xl transition-colors"
          style={{ borderColor: 'var(--theme-input-border)' }}
          autoFocus
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 p-1 hover:bg-[color:var(--theme-card-hover)] rounded transition-colors cursor-pointer"
            aria-label="Clear search"
          >
            <X className="w-5 h-5 text-[color:var(--theme-text-secondary)]" />
          </button>
        )}
      </div>
    </div>
  );
}

