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
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-amber-600" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search for Magic: The Gathering cards..."
          className="w-full pl-14 pr-12 py-4 bg-white/95 backdrop-blur-sm text-slate-900 text-lg rounded-lg border-2 border-amber-400/50 focus:border-amber-500 focus:outline-none shadow-xl"
          autoFocus
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 p-1 hover:bg-amber-50 rounded transition-colors"
            aria-label="Clear search"
          >
            <X className="w-5 h-5 text-slate-700" />
          </button>
        )}
      </div>
    </div>
  );
}

