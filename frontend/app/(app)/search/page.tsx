'use client';

// frontend/app/(app)/search/page.tsx

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { SearchInput } from '@/components/ui/SearchInput';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { api } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { SearchX } from 'lucide-react';

interface SearchResponse {
  cards: CardData[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
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

export default function SearchPage() {
  const searchParams = useSearchParams();
  const urlQuery = searchParams.get('q') || '';
  
  const [searchQuery, setSearchQuery] = useState(urlQuery);
  const [allCards, setAllCards] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  // Filters
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [setFilter, setSetFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const debouncedQuery = useDebounce(searchQuery, 500);

  // Sync search query with URL parameter
  useEffect(() => {
    setSearchQuery(urlQuery);
  }, [urlQuery]);

  const searchCards = useCallback(async (query: string, pageNum: number = 1) => {
    if (!query.trim()) {
      setAllCards([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Fetch more results to allow client-side filtering
      const response = await api.get<SearchResponse>(
        `/api/cards/search?q=${encodeURIComponent(query)}&page=${pageNum}&page_size=100`
      );
      setAllCards(response.cards);
      setTotal(response.total);
      setHasMore(response.has_more);
      setPage(pageNum);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to search cards');
      setAllCards([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    searchCards(debouncedQuery, 1);
  }, [debouncedQuery, searchCards]);

  // Apply client-side filters
  const filteredCards = useMemo(() => {
    let filtered = [...allCards];
    
    // Filter by colors
    if (selectedColors.length > 0) {
      filtered = filtered.filter(card => {
        if (!card.colors || card.colors.length === 0) {
          return selectedColors.includes('C'); // Colorless
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
    
    // Filter by set
    if (setFilter) {
      filtered = filtered.filter(card => 
        card.set_code?.toLowerCase() === setFilter.toLowerCase()
      );
    }
    
    return filtered;
  }, [allCards, selectedColors, typeFilter, setFilter]);

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
    setSetFilter('');
  };

  const hasActiveFilters = selectedColors.length > 0 || typeFilter || setFilter;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
          Card Search
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Search through Magic: The Gathering cards
        </p>
      </div>

      <div className="space-y-4">
        <div className="max-w-2xl">
          <SearchInput
            placeholder="Search for cards (e.g., Lightning Bolt, Jace, etc.)"
            value={searchQuery}
            onChange={setSearchQuery}
          />
        </div>

        <div className="flex items-center gap-4">
          <Button
            onClick={() => setShowFilters(!showFilters)}
            variant="outline"
            size="sm"
          >
            {showFilters ? 'Hide' : 'Show'} Filters
          </Button>
          {hasActiveFilters && (
            <Button
              onClick={clearFilters}
              variant="outline"
              size="sm"
            >
              Clear Filters
            </Button>
          )}
        </div>

        {showFilters && (
          <div className="bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Colors
              </label>
              <div className="flex flex-wrap gap-2">
                {COLORS.map(color => (
                  <button
                    key={color}
                    onClick={() => toggleColor(color)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      selectedColors.includes(color)
                        ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                        : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-card-border)]'
                    }`}
                  >
                    {COLOR_NAMES[color]}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Type (contains)
              </label>
              <Input
                type="text"
                placeholder="e.g., Creature, Instant, Artifact"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="max-w-xs"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Set Code
              </label>
              <Input
                type="text"
                placeholder="e.g., M21, CMR"
                value={setFilter}
                onChange={(e) => setSetFilter(e.target.value.toUpperCase())}
                className="max-w-xs"
              />
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {error}
        </div>
      )}

      {loading ? (
        <CardGridSkeleton count={20} />
      ) : (
        <>
          {searchQuery && filteredCards.length === 0 && total === 0 ? (
            <Card variant="elevated">
              <EmptyState
                icon={SearchX}
                title="No cards found"
                description={`No cards match your search "${searchQuery}". Try adjusting your search query or filters to find what you're looking for.`}
              />
            </Card>
          ) : (
            <>
              {searchQuery && (
                <div className="text-[color:var(--theme-text-secondary)] text-sm">
                  {hasActiveFilters ? (
                    <>Showing {filteredCards.length} of {total} cards (filtered)</>
                  ) : (
                    <>Found {total} {total === 1 ? 'card' : 'cards'}</>
                  )}
                </div>
              )}
              <CardGrid cards={filteredCards} />
            </>
          )}
        </>
      )}
    </div>
  );
}

