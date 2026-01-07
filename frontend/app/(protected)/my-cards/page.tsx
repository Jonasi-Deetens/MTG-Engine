'use client';

// frontend/app/(protected)/my-cards/page.tsx

import { useState, useEffect } from 'react';
import { collections, FavoriteResponse } from '@/lib/collections';
import { CardGrid } from '@/components/cards/CardGrid';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import Link from 'next/link';

export default function MyCardsPage() {
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

  const handleRemoveFavorite = async (cardId: string) => {
    try {
      await collections.removeFavorite(cardId);
      setFavorites(favorites.filter(card => card.card_id !== cardId));
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove favorite');
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-white mb-2">
          My Cards
        </h1>
        <p className="text-slate-400">
          Your favorite cards and collections
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <Card variant="elevated">
          <Link href="/my-cards/favorites" className="block p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-white mb-1">Favorites</h3>
                <p className="text-slate-400 text-sm">{favorites.length} cards</p>
              </div>
              <svg className="w-8 h-8 text-amber-500" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </div>
          </Link>
        </Card>

        <Card variant="elevated">
          <Link href="/my-cards/collections" className="block p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-white mb-1">Collections</h3>
                <p className="text-slate-400 text-sm">Organize your cards</p>
              </div>
              <svg className="w-8 h-8 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
          </Link>
        </Card>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Recent Favorites</h2>
        {error && (
          <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 mb-4">
            {error}
          </div>
        )}
        {loading && favorites.length === 0 ? (
          <CardGridSkeleton count={12} />
        ) : favorites.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-400 text-lg">No favorites yet</p>
            <p className="text-slate-500 text-sm mt-2">
              Start adding cards to your favorites to see them here
            </p>
            <Link href="/browse" className="mt-4 inline-block">
              <Button variant="primary">Browse Cards</Button>
            </Link>
          </div>
        ) : (
          <>
            <CardGrid cards={favorites.slice(0, 12)} />
            {favorites.length > 12 && (
              <div className="mt-4 text-center">
                <Link href="/my-cards/favorites">
                  <Button variant="outline">View All Favorites</Button>
                </Link>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

