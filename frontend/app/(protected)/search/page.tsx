'use client';

// frontend/app/(protected)/search/page.tsx

import { useState, useEffect, useCallback } from 'react';
import { Input } from '@/components/ui/Input';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { api } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';

interface SearchResponse {
  cards: CardData[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [cards, setCards] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const debouncedQuery = useDebounce(searchQuery, 500);

  const searchCards = useCallback(async (query: string, pageNum: number = 1) => {
    if (!query.trim()) {
      setCards([]);
      setTotal(0);
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.get<SearchResponse>(
        `/api/cards/search?q=${encodeURIComponent(query)}&page=${pageNum}&page_size=20`
      );
      setCards(response.cards);
      setTotal(response.total);
      setHasMore(response.has_more);
      setPage(pageNum);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to search cards');
      setCards([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    searchCards(debouncedQuery, 1);
  }, [debouncedQuery, searchCards]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-white mb-2">
          Card Search
        </h1>
        <p className="text-slate-400">
          Search through Magic: The Gathering cards
        </p>
      </div>

      <div className="max-w-2xl">
        <Input
          type="text"
          placeholder="Search for cards (e.g., Lightning Bolt, Jace, etc.)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <CardGridSkeleton count={20} />
      ) : (
        <>
          {searchQuery && (
            <div className="text-slate-400 text-sm">
              Found {total} {total === 1 ? 'card' : 'cards'}
            </div>
          )}
          <CardGrid cards={cards} />
        </>
      )}
    </div>
  );
}

