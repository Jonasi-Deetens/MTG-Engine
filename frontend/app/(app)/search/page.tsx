'use client';

// frontend/app/(app)/search/page.tsx

import { useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { SearchInput } from '@/components/ui/SearchInput';
import { CardGrid } from '@/components/cards/CardGrid';
import { Card } from '@/components/ui/Card';
import { Pagination } from '@/components/ui/Pagination';
import { EmptyState } from '@/components/ui/EmptyState';
import { LoadingState } from '@/components/ui/LoadingState';
import { SearchX } from 'lucide-react';
import { cards } from '@/lib/api';
import { useCardSearch } from '@/features/search/hooks/useCardSearch';
import { useSearchFilters } from '@/features/search/hooks/useSearchFilters';
import { applyFilters } from '@/utils/search/filtering';
import { calculatePagination } from '@/utils/search/pagination';
import { SearchHeader } from '@/features/search/components/SearchHeader';
import { SearchFilters } from '@/features/search/components/SearchFilters';
import { PAGE_SIZE } from '@/lib/constants/search';

export default function SearchPage() {
  const router = useRouter();

  const {
    selectedColors,
    typeFilters,
    setFilter,
    rarityFilter,
    languageFilter,
    keywordFilter,
    showFilters,
    setShowFilters,
    hasActiveFilters,
    toggleColor,
    clearFilters,
    setTypeFilters,
    setSetFilter,
    setRarityFilter,
    setLanguageFilter,
    setKeywordFilter,
  } = useSearchFilters();

  const {
    searchQuery,
    setSearchQuery,
    allCards,
    loading,
    error,
    page,
    setPage,
    total,
    hasMore,
    isBrowseMode,
  } = useCardSearch({
    selectedColors,
    typeFilters,
    setFilter,
    rarityFilter,
    languageFilter,
    keywordFilter,
  });

  // Apply client-side filtering only in search mode
  // In browse mode, server-side filtering is already applied
  const filteredCards = useMemo(() => {
    if (isBrowseMode) {
      return allCards;
    }
    return applyFilters(
      allCards,
      selectedColors,
    typeFilters,
      setFilter,
      rarityFilter,
      languageFilter,
      keywordFilter
    );
  }, [allCards, selectedColors, typeFilters, setFilter, rarityFilter, languageFilter, keywordFilter, isBrowseMode]);

  // Paginate filtered cards
  const pagination = useMemo(() => {
    if (!isBrowseMode) {
      // Client-side pagination for search results
      const { startIndex, endIndex } = calculatePagination(filteredCards.length, page);
      return {
        cards: filteredCards.slice(startIndex, endIndex),
        totalPages: Math.ceil(filteredCards.length / PAGE_SIZE),
        displayTotal: filteredCards.length,
      };
    } else {
      // Server-side pagination already applied (browse mode)
      return {
        cards: filteredCards,
        totalPages: Math.ceil(total / PAGE_SIZE),
        displayTotal: total,
      };
    }
  }, [filteredCards, page, isBrowseMode, total]);

  const handlePageChange = useCallback((newPage: number) => {
    if (newPage === page) return;
    
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [page, setPage]);

  const handleRandomCard = useCallback(async () => {
    try {
      const card = await cards.getRandom();
      if (card?.card_id) {
        router.push(`/cards/${card.card_id}`);
      }
    } catch (err) {
      console.error('Failed to get random card:', err);
    }
  }, [router]);

  const handleToggleTypeFilter = useCallback((value: string) => {
    setTypeFilters((prev) =>
      prev.includes(value) ? prev.filter((entry) => entry !== value) : [...prev, value]
    );
    setPage(1);
  }, [setTypeFilters, setPage]);

  const handleSetFilterChange = useCallback((value: string) => {
    setSetFilter(value);
    setPage(1);
  }, [setSetFilter, setPage]);

  const handleRarityFilterChange = useCallback((value: string) => {
    setRarityFilter(value);
    setPage(1);
  }, [setRarityFilter, setPage]);

  const handleLanguageFilterChange = useCallback((value: string) => {
    setLanguageFilter(value);
    setPage(1);
  }, [setLanguageFilter, setPage]);

  const handleKeywordFilterChange = useCallback((value: string) => {
    setKeywordFilter(value);
    setPage(1);
  }, [setKeywordFilter, setPage]);

  const handleToggleColor = useCallback((color: string) => {
    toggleColor(color);
    setPage(1);
  }, [toggleColor, setPage]);

  const handleClearFilters = useCallback(() => {
    clearFilters();
    setPage(1);
  }, [clearFilters, setPage]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1
            className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2 nier-glitch"
            data-text={isBrowseMode ? 'Browse Cards' : 'Card Search'}
          >
            {isBrowseMode ? 'Browse Cards' : 'Card Search'}
          </h1>
          <p className="text-[color:var(--theme-text-secondary)]">
            {isBrowseMode 
              ? 'Explore Magic: The Gathering cards' 
              : 'Search through Magic: The Gathering cards'}
          </p>
        </div>
        <SearchHeader onRandomClick={handleRandomCard} />
      </div>

      <div className="space-y-4">
        <div className="max-w-2xl">
          <SearchInput
            placeholder="Search for cards (e.g., Lightning Bolt, Jace, etc.)"
            value={searchQuery}
            onChange={setSearchQuery}
          />
        </div>

        <SearchFilters
          selectedColors={selectedColors}
          typeFilters={typeFilters}
          setFilter={setFilter}
          rarityFilter={rarityFilter}
          languageFilter={languageFilter}
          keywordFilter={keywordFilter}
          showFilters={showFilters}
          hasActiveFilters={Boolean(hasActiveFilters)}
          onToggleFilters={() => setShowFilters(!showFilters)}
          onToggleColor={handleToggleColor}
          onToggleType={handleToggleTypeFilter}
          onSetFilterChange={handleSetFilterChange}
          onRarityFilterChange={handleRarityFilterChange}
          onLanguageFilterChange={handleLanguageFilterChange}
          onKeywordFilterChange={handleKeywordFilterChange}
          onClearFilters={handleClearFilters}
          isBrowseMode={isBrowseMode}
        />
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {typeof error === 'string' ? error : String(error)}
        </div>
      )}

      {loading ? (
        <LoadingState fullScreen={false} className="py-12" />
      ) : (
        <>
          {pagination.cards.length === 0 ? (
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
              <CardGrid cards={pagination.cards} />
              
              {pagination.totalPages > 1 && (
                <Pagination
                  currentPage={page}
                  totalPages={pagination.totalPages}
                  onPageChange={handlePageChange}
                  pageSize={PAGE_SIZE}
                  total={pagination.displayTotal}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
