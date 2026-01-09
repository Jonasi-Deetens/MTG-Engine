'use client';

// frontend/components/landing/LandingSearchResults.tsx

import { useState, useMemo } from 'react';
import { CardData } from '@/components/cards/CardPreview';
import { CardPreview } from '@/components/cards/CardPreview';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { Button } from '@/components/ui/Button';
import { Filter, X } from 'lucide-react';

interface LandingSearchResultsProps {
  searchQuery: string;
  searchResults: CardData[];
  searching: boolean;
  error?: string;
}

const COLORS = ['W', 'U', 'B', 'R', 'G', 'C'];
const COLOR_NAMES: Record<string, string> = {
  'W': 'White',
  'U': 'Blue',
  'B': 'Black',
  'R': 'Red',
  'G': 'Green',
  'C': 'Colorless',
};

export function LandingSearchResults({
  searchQuery,
  searchResults,
  searching,
  error,
}: LandingSearchResultsProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('');

  const filteredResults = useMemo(() => {
    let filtered = [...searchResults];

    // Filter by colors
    if (selectedColors.length > 0) {
      filtered = filtered.filter(card => {
        if (!card.colors || card.colors.length === 0) {
          return selectedColors.includes('C');
        }
        return selectedColors.some(color => card.colors?.includes(color.toLowerCase()));
      });
    }

    // Filter by type
    if (typeFilter) {
      filtered = filtered.filter(card =>
        card.type_line?.toLowerCase().includes(typeFilter.toLowerCase())
      );
    }

    return filtered;
  }, [searchResults, selectedColors, typeFilter]);

  const toggleColor = (color: string) => {
    setSelectedColors(prev =>
      prev.includes(color)
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
  };

  const clearFilters = () => {
    setSelectedColors([]);
    setTypeFilter('');
  };

  const hasActiveFilters = selectedColors.length > 0 || typeFilter;

  if (!searchQuery && !searching) {
    return null;
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Filters */}
      {searchQuery && (
        <div className="mb-2 px-4 flex-shrink-0">
          <div className="flex items-center justify-between mb-1.5">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-1.5 px-2 py-1 bg-white/10 hover:bg-white/20 rounded text-white text-xs transition-colors"
            >
              <Filter className="w-3.5 h-3.5" />
              Filters
            </button>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="flex items-center gap-1 px-1.5 py-0.5 text-white/70 hover:text-white text-xs"
              >
                <X className="w-3 h-3" />
                Clear
              </button>
            )}
          </div>

          {showFilters && (
            <div className="bg-white/10 backdrop-blur-sm rounded p-2 space-y-2">
              {/* Color Filters */}
              <div>
                <label className="block text-white text-xs font-medium mb-1">Colors</label>
                <div className="flex flex-wrap gap-1">
                  {COLORS.map(color => (
                    <button
                      key={color}
                      onClick={() => toggleColor(color)}
                      className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                        selectedColors.includes(color)
                          ? 'bg-amber-500 text-white'
                          : 'bg-white/20 text-white hover:bg-white/30'
                      }`}
                    >
                      {COLOR_NAMES[color]}
                    </button>
                  ))}
                </div>
              </div>

              {/* Type Filter */}
              <div>
                <label className="block text-white text-xs font-medium mb-1">Type</label>
                <input
                  type="text"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  placeholder="e.g., Creature, Instant..."
                  className="w-full px-2 py-1 text-xs bg-white/20 border border-white/30 rounded text-white placeholder-white/50 focus:border-amber-500 focus:outline-none"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Results */}
      <div className="flex-1 overflow-y-auto px-4 min-h-0">
        {error ? (
          <div className="text-center py-8">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        ) : searching ? (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 xl:grid-cols-8 gap-2 pb-4">
            <CardGridSkeleton count={16} />
          </div>
        ) : filteredResults.length > 0 ? (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-7 xl:grid-cols-8 gap-2 pb-4">
            {filteredResults.map((card) => (
              <CardPreview key={card.card_id} card={card} />
            ))}
          </div>
        ) : searchQuery ? (
          <div className="text-center py-8">
            <p className="text-white/70 text-sm">No cards found matching "{searchQuery}"</p>
            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="mt-2 px-2 py-1 text-xs bg-white/10 hover:bg-white/20 text-white rounded transition-colors"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}

