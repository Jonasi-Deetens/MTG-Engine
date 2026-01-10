'use client';

// frontend/app/(app)/browse/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { cards } from '@/lib/api';
import { CardData } from '@/components/cards/CardPreview';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { Button } from '@/components/ui/Button';

interface BrowseResponse {
  cards: CardData[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export default function BrowsePage() {
  const router = useRouter();
  const [cardsData, setCardsData] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const loadCards = async (pageNum: number = 1) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await cards.list(pageNum, 24) as BrowseResponse;
      setCardsData(response.cards);
      setTotal(response.total);
      setHasMore(response.has_more);
      setPage(pageNum);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to load cards');
      setCardsData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards(1);
  }, []);

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
            Browse Cards
          </h1>
          <p className="text-[color:var(--theme-text-secondary)]">
            Explore Magic: The Gathering cards
          </p>
        </div>
        <Button onClick={handleRandomCard} variant="primary">
          Random Card
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {error}
        </div>
      )}

      {loading ? (
        <CardGridSkeleton count={24} />
      ) : (
        <>
          <div className="text-[color:var(--theme-text-secondary)] text-sm">
            Showing {cardsData.length} of {total} cards (Page {page})
          </div>
          <CardGrid cards={cardsData} />
          
          {/* Pagination */}
          <div className="flex items-center justify-center gap-4">
            <Button
              onClick={() => loadCards(page - 1)}
              disabled={page <= 1 || loading}
              variant="outline"
            >
              Previous
            </Button>
            <span className="text-[color:var(--theme-text-secondary)]">
              Page {page}
            </span>
            <Button
              onClick={() => loadCards(page + 1)}
              disabled={!hasMore || loading}
              variant="outline"
            >
              Next
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

