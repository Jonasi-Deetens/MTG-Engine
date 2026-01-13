// frontend/hooks/search/useCardSearch.ts

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { cards } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';
import { getErrorMessage } from '@/lib/utils/errors';
import { PAGE_SIZE } from '@/lib/constants/search';
import { CardData } from '@/components/cards/CardPreview';

interface SearchResponse {
  cards: CardData[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

interface UseCardSearchOptions {
  selectedColors: string[];
  typeFilter: string;
  setFilter: string;
}

export function useCardSearch({ selectedColors, typeFilter, setFilter }: UseCardSearchOptions) {
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

  const debouncedQuery = useDebounce(searchQuery, 500);
  const isBrowseMode = !debouncedQuery.trim();
  const isInitialMount = useRef(true);
  const lastFetchedQuery = useRef<string>('');
  const lastFetchedPage = useRef<number>(0);
  const lastSyncedQuery = useRef<string>('');
  const lastSyncedPage = useRef<number>(0);
  const filtersKey = `${selectedColors.join(',')}-${typeFilter}-${setFilter}`;
  const lastFetchedFilters = useRef<string>('');

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
        if (selectedColors.length > 0) params.set('colors', selectedColors.join(','));
        if (typeFilter) params.set('type', typeFilter);
        if (setFilter) params.set('set_code', setFilter);
        router.replace(`/search?${params.toString()}`, { scroll: false });
        lastSyncedPage.current = targetPage;
        lastSyncedQuery.current = '';
      }
    } else {
      // Search mode
      searchCards(debouncedQuery);
      
      // Update URL only if query changed
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedQuery, isBrowseMode, page, loadBrowseCards, searchCards, router, filtersKey, selectedColors, typeFilter, setFilter]);

  return {
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
  };
}

