'use client';

// frontend/app/(protected)/my-cards/favorites/page.tsx

import { useState, useEffect } from 'react';
import { collections, FavoriteResponse } from '@/lib/collections';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { EmptyState } from '@/components/ui/EmptyState';
import { Card } from '@/components/ui/Card';
import { Heart } from 'lucide-react';
import Link from 'next/link';

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  const loadFavorites = async (pageNum: number = 1) => {
    setLoading(true);
    setError('');
    try {
      const response = await collections.getFavorites(pageNum, 24);
      const cards = response.map(fav => fav.card);
      setFavorites(pageNum === 1 ? cards : [...favorites, ...cards]);
      setHasMore(response.length === 24);
      setPage(pageNum);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to load favorites');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFavorites(1);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link href="/my-cards" className="text-slate-400 hover:text-white transition-colors mb-2 inline-block">
            ← Back to My Cards
          </Link>
          <h1 className="font-heading text-3xl font-bold text-white mb-2">
            Favorites
          </h1>
          <p className="text-slate-400">
            {favorites.length} favorite card{favorites.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {loading && favorites.length === 0 ? (
        <CardGridSkeleton count={24} />
      ) : favorites.length === 0 ? (
        <Card variant="elevated">
          <EmptyState
            icon={Heart}
            title="No favorites yet"
            description="Start adding cards to your favorites by clicking the heart icon on any card. Your favorite cards will appear here for easy access."
            actionLabel="Browse Cards"
            actionHref="/browse"
          />
        </Card>
      ) : (
        <>
          <CardGrid cards={favorites} />
          
          {/* Pagination */}
          <div className="flex items-center justify-center gap-4">
            <Button
              onClick={() => loadFavorites(page - 1)}
              disabled={page <= 1 || loading}
              variant="outline"
            >
              Previous
            </Button>
            <span className="text-slate-400">
              Page {page}
            </span>
            <Button
              onClick={() => loadFavorites(page + 1)}
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

