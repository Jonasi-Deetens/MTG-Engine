'use client';

// frontend/app/(app)/search/page.tsx

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { SearchInput } from '@/components/ui/SearchInput';
import { Input } from '@/components/ui/Input';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { cards } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Pagination } from '@/components/ui/Pagination';
import { SearchX, Sparkles } from 'lucide-react';

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

const PAGE_SIZE = 24;

// Helper function to safely convert error to string
function getErrorMessage(err: any): string {
  try {
    if (!err) return 'An unknown error occurred';
    
    // If it's already a string, return it
    if (typeof err === 'string') return err;
    
    // Check for error message first
    if (err.message && typeof err.message === 'string' && err.message !== '[object Object]') {
      return err.message;
    }
    
    // Check if err.data is an array (validation errors from FastAPI/Pydantic)
    if (Array.isArray(err.data)) {
      const messages = err.data
        .map((e: any) => {
          if (typeof e === 'string') return e;
          if (e.msg && typeof e.msg === 'string') return e.msg;
          if (e.detail && typeof e.detail === 'string') return e.detail;
          if (e.message && typeof e.message === 'string') return e.message;
          // Try to create a readable message from validation error
          if (Array.isArray(e.loc) && e.msg && typeof e.msg === 'string') {
            return `${e.loc.join('.')}: ${e.msg}`;
          }
          // Last resort for this item
          try {
            const str = String(e);
            return str !== '[object Object]' ? str : null;
          } catch {
            return null;
          }
        })
        .filter((msg: any): msg is string => Boolean(msg) && typeof msg === 'string');
      return messages.length > 0 ? messages.join(', ') : 'Validation error';
    }
    
    // Check for data.detail (could be string or array of validation errors)
    if (err.data) {
      const data = err.data;
      
      // If data.detail exists
      if (data.detail !== undefined) {
        const detail = data.detail;
        if (typeof detail === 'string') return detail;
        if (Array.isArray(detail)) {
          // Handle validation error array
          const messages = detail
            .map((e: any) => {
              if (typeof e === 'string') return e;
              if (e.msg && typeof e.msg === 'string') return e.msg;
              if (e.detail && typeof e.detail === 'string') return e.detail;
              if (Array.isArray(e.loc) && e.msg && typeof e.msg === 'string') {
                return `${e.loc.join('.')}: ${e.msg}`;
              }
              try {
                const str = String(e);
                return str !== '[object Object]' ? str : null;
              } catch {
                return null;
              }
            })
            .filter((msg: any): msg is string => Boolean(msg) && typeof msg === 'string');
          return messages.length > 0 ? messages.join(', ') : 'Validation error';
        }
        // If detail is an object, try to stringify it safely
        if (typeof detail === 'object') {
          try {
            const str = JSON.stringify(detail);
            return str !== '{}' ? str : null;
          } catch {
            // Ignore
          }
        }
      }
      
      // If data itself is a string
      if (typeof data === 'string') {
        return data;
      }
      
      // If data is an object, try to extract meaningful info
      if (typeof data === 'object' && !Array.isArray(data)) {
        if (data.message && typeof data.message === 'string') return data.message;
        if (data.error && typeof data.error === 'string') return data.error;
      }
    }
    
    // Last resort: try to get a meaningful string representation
    if (err.toString && typeof err.toString === 'function') {
      try {
        const str = err.toString();
        if (str && str !== '[object Object]' && typeof str === 'string') {
          return str;
        }
      } catch {
        // Ignore
      }
    }
    
    // Final fallback
    return 'An error occurred while loading cards. Please try again.';
  } catch (parseError) {
    // If even error parsing fails, return a safe message
    console.error('Error parsing error message:', parseError);
    return 'An error occurred while loading cards. Please try again.';
  }
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const urlQuery = searchParams.get('q') || '';
  const urlPage = parseInt(searchParams.get('page') || '1', 10);
  
  const [searchQuery, setSearchQuery] = useState(urlQuery);
  const [allCards, setAllCards] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(urlPage);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  // Filters
  const [selectedColors, setSelectedColors] = useState<string[]>([]);
  const [typeFilter, setTypeFilter] = useState('');
  const [setFilter, setSetFilter] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const debouncedQuery = useDebounce(searchQuery, 500);
  const isBrowseMode = !debouncedQuery.trim();
  const isInitialMount = useRef(true);
  const lastFetchedQuery = useRef<string>('');
  const lastFetchedPage = useRef<number>(0);
  const lastSyncedQuery = useRef<string>('');
  const lastSyncedPage = useRef<number>(0);
  const lastFetchedFilters = useRef<string>(''); // Track filter state to detect changes

  // Check if any filters are active
  const hasActiveFilters = selectedColors.length > 0 || typeFilter || setFilter;
  const filtersKey = `${selectedColors.join(',')}-${typeFilter}-${setFilter}`;

  // Initialize state from URL on mount only
  useEffect(() => {
    if (isInitialMount.current) {
      if (urlQuery !== searchQuery) {
        setSearchQuery(urlQuery);
      }
      if (urlPage !== page && urlPage > 0) {
        setPage(urlPage);
      }
      isInitialMount.current = false;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount

  // Browse mode: Load cards with server-side filtering
  const loadBrowseCards = useCallback(async (pageNum: number = 1) => {
    // Prevent duplicate fetches only if no filters changed
    if (lastFetchedPage.current === pageNum && lastFetchedQuery.current === '' && lastFetchedFilters.current === filtersKey) {
      return;
    }
    
    // If filters changed, reset to page 1
    if (lastFetchedFilters.current !== filtersKey && pageNum !== 1) {
      setPage(1);
      return; // Will be called again with page 1
    }
    
    setLoading(true);
    setError('');
    
    try {
      // Build filter object for API call
      const filters: { colors?: string[], type?: string, set_code?: string } = {};
      if (selectedColors.length > 0) {
        filters.colors = selectedColors;
      }
      if (typeFilter) {
        filters.type = typeFilter;
      }
      if (setFilter) {
        filters.set_code = setFilter;
      }
      
      // Use server-side filtering - backend will handle filtering and pagination
      const response = await cards.list(pageNum, PAGE_SIZE, Object.keys(filters).length > 0 ? filters : undefined) as SearchResponse;
      setAllCards(response.cards);
      setTotal(response.total);
      setHasMore(response.has_more);
      lastFetchedPage.current = pageNum;
      lastFetchedQuery.current = '';
      lastFetchedFilters.current = filtersKey;
    } catch (err: any) {
      console.error('Error loading cards:', err);
      const errorMsg = getErrorMessage(err);
      console.error('Error message:', errorMsg);
      // Ensure we always set a string
      setError(typeof errorMsg === 'string' ? errorMsg : 'Failed to load cards');
      setAllCards([]);
    } finally {
      setLoading(false);
    }
  }, [selectedColors, typeFilter, setFilter, filtersKey]);

  // Search mode: Load search results (fetch more for client-side filtering)
  const searchCards = useCallback(async (query: string) => {
    if (!query.trim()) {
      setAllCards([]);
      setTotal(0);
      lastFetchedQuery.current = '';
      lastFetchedPage.current = 0;
      return;
    }

    // Prevent duplicate fetches
    if (lastFetchedQuery.current === query) {
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      // Fetch more results to allow client-side filtering
      const response = await cards.search(query, 1, 100) as SearchResponse;
      setAllCards(response.cards);
      setTotal(response.total);
      setHasMore(response.has_more);
      lastFetchedQuery.current = query;
      lastFetchedPage.current = 0;
    } catch (err: any) {
      console.error('Error searching cards:', err);
      const errorMsg = getErrorMessage(err);
      // Ensure we always set a string
      setError(typeof errorMsg === 'string' ? errorMsg : 'Failed to search cards');
      setAllCards([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load cards based on mode
  useEffect(() => {
    if (isBrowseMode) {
      // When switching to browse mode, reset to page 1 if coming from search or filters changed
      const wasInSearchMode = lastSyncedQuery.current !== '';
      const filtersChanged = lastFetchedFilters.current !== filtersKey;
      const targetPage = (wasInSearchMode || filtersChanged) ? 1 : page;
      
      if ((wasInSearchMode || filtersChanged) && page !== 1) {
        setPage(1);
      }
      
      loadBrowseCards(targetPage);
      
      // Update URL only if we haven't already synced this page
      if (lastSyncedPage.current !== targetPage) {
        const params = new URLSearchParams();
        params.set('page', targetPage.toString());
        router.replace(`/search?${params.toString()}`, { scroll: false });
        lastSyncedPage.current = targetPage;
        lastSyncedQuery.current = '';
      }
    } else {
      searchCards(debouncedQuery);
      // Update URL only if we haven't already synced this query
      if (lastSyncedQuery.current !== debouncedQuery) {
        const params = new URLSearchParams();
        params.set('q', debouncedQuery);
        params.set('page', '1');
        router.replace(`/search?${params.toString()}`, { scroll: false });
        lastSyncedQuery.current = debouncedQuery;
        lastSyncedPage.current = 0;
        if (page !== 1) setPage(1);
      }
    }
  }, [isBrowseMode, debouncedQuery, page, loadBrowseCards, searchCards, router, filtersKey]);

  // In browse mode with filters, server-side filtering is used, so no client-side filtering needed
  // In search mode, we still need client-side filtering for the search results
  const filteredCards = useMemo(() => {
    // If in browse mode, cards are already filtered by the backend
    if (isBrowseMode) {
      return allCards;
    }
    
    // In search mode, apply client-side filters to search results
    let filtered = [...allCards];
    
    // Filter by colors
    if (selectedColors.length > 0) {
      filtered = filtered.filter(card => {
        if (!card.colors || card.colors.length === 0) {
          return selectedColors.includes('C'); // Colorless
        }
        return selectedColors.some(color => 
          card.colors?.some(cardColor => cardColor.toUpperCase() === color.toUpperCase())
        );
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
  }, [allCards, selectedColors, typeFilter, setFilter, isBrowseMode]);

  // Paginate filtered cards
  // Use client-side pagination only in search mode
  // In browse mode, server-side pagination is always used (with or without filters)
  const paginatedCards = useMemo(() => {
    if (!isBrowseMode) {
      // Client-side pagination for search results
      const startIndex = (page - 1) * PAGE_SIZE;
      const endIndex = startIndex + PAGE_SIZE;
      return filteredCards.slice(startIndex, endIndex);
    } else {
      // Server-side pagination already applied (browse mode)
      return filteredCards;
    }
  }, [filteredCards, page, isBrowseMode]);

  // Calculate total pages
  const totalPages = useMemo(() => {
    if (!isBrowseMode) {
      // Client-side pagination for search results
      return Math.ceil(filteredCards.length / PAGE_SIZE);
    } else {
      // Server-side pagination (browse mode)
      return Math.ceil(total / PAGE_SIZE);
    }
  }, [isBrowseMode, total, filteredCards.length]);

  // Calculate display total
  const displayTotal = useMemo(() => {
    if (!isBrowseMode) {
      // Client-side pagination for search results
      return filteredCards.length;
    } else {
      // Server-side pagination (browse mode)
      return total;
    }
  }, [isBrowseMode, total, filteredCards.length]);

  const toggleColor = (color: string) => {
    setSelectedColors(prev => 
      prev.includes(color) 
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
    // Reset to page 1 when filters change
    setPage(1);
    // Clear fetch cache to force reload
    if (isBrowseMode) {
      lastFetchedFilters.current = '';
      lastFetchedPage.current = 0;
    }
  };

  const clearFilters = () => {
    setSelectedColors([]);
    setTypeFilter('');
    setSetFilter('');
    // Reset to page 1 when filters are cleared
    setPage(1);
    // Clear fetch cache to force reload
    if (isBrowseMode) {
      lastFetchedFilters.current = '';
      lastFetchedPage.current = 0;
    }
  };

  const handlePageChange = (newPage: number) => {
    if (newPage === page) return; // Prevent unnecessary updates
    
    setPage(newPage);
    // Scroll to top on page change
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Update URL and ref
    const params = new URLSearchParams();
    params.set('page', newPage.toString());
    if (isBrowseMode) {
      lastSyncedPage.current = newPage;
      lastSyncedQuery.current = '';
    }
    router.replace(`/search?${params.toString()}`, { scroll: false });
  };

  const handleRandomCard = async () => {
    try {
      const card = await cards.getRandom();
      if (card?.card_id) {
        router.push(`/cards/${card.card_id}`);
      }
    } catch (err) {
      console.error('Failed to get random card:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
            {isBrowseMode ? 'Browse Cards' : 'Card Search'}
          </h1>
          <p className="text-[color:var(--theme-text-secondary)]">
            {isBrowseMode 
              ? 'Explore Magic: The Gathering cards' 
              : 'Search through Magic: The Gathering cards'}
          </p>
        </div>
        <Button onClick={handleRandomCard} variant="primary">
          <Sparkles className="w-4 h-4 mr-2" />
          Random Card
        </Button>
      </div>

      <div className="space-y-4">
        <div className="max-w-2xl">
          <SearchInput
            placeholder={isBrowseMode 
              ? "Search for cards (e.g., Lightning Bolt, Jace, etc.)" 
              : "Search for cards (e.g., Lightning Bolt, Jace, etc.)"}
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
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors cursor-pointer ${
                      selectedColors.includes(color)
                        ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                        : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
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
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setPage(1);
                  // Clear fetch cache to force reload in browse mode
                  if (isBrowseMode) {
                    lastFetchedFilters.current = '';
                    lastFetchedPage.current = 0;
                  }
                }}
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
                onChange={(e) => {
                  setSetFilter(e.target.value.toUpperCase());
                  setPage(1);
                  // Clear fetch cache to force reload in browse mode
                  if (isBrowseMode) {
                    lastFetchedFilters.current = '';
                    lastFetchedPage.current = 0;
                  }
                }}
                className="max-w-xs"
              />
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {typeof error === 'string' ? error : String(error)}
        </div>
      )}

      {loading ? (
        <CardGridSkeleton count={PAGE_SIZE} />
      ) : (
        <>
          {paginatedCards.length === 0 ? (
            <Card variant="elevated">
              <EmptyState
                icon={SearchX}
                title="No cards found"
                description={
                  isBrowseMode
                    ? "No cards match your filters. Try adjusting your filters to find what you're looking for."
                    : `No cards match your search "${searchQuery}". Try adjusting your search query or filters to find what you're looking for.`
                }
              />
            </Card>
          ) : (
            <>
              <CardGrid cards={paginatedCards} />
              
              {totalPages > 1 && (
                <Pagination
                  currentPage={page}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                  pageSize={PAGE_SIZE}
                  total={displayTotal}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
