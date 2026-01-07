'use client';

// frontend/app/(protected)/dashboard/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { decks } from '@/lib/decks';
import { collections } from '@/lib/collections';
import { cards } from '@/lib/api';
import { DeckResponse } from '@/lib/decks';
import { CardData } from '@/components/cards/CardPreview';
import { CardPreview } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState({
    decks: 0,
    favorites: 0,
    collections: 0,
  });
  const [recentDecks, setRecentDecks] = useState<DeckResponse[]>([]);
  const [featuredCards, setFeaturedCards] = useState<CardData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      setLoading(true);
      try {
        // Load stats and recent decks in parallel
        const [decksList, favoritesList, collectionsList, randomCards] = await Promise.all([
          decks.getDecks().catch(() => []),
          collections.getFavorites(1, 100).catch(() => []), // Get up to 100 for count
          collections.getCollections().catch(() => []),
          Promise.all(
            Array.from({ length: 3 }, () => 
              cards.getRandom().catch(() => null)
            )
          ),
        ]);

        setStats({
          decks: decksList.length,
          favorites: favoritesList.length,
          collections: collectionsList.length,
        });

        // Get most recent decks (sorted by updated_at)
        const sortedDecks = [...decksList].sort(
          (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
        setRecentDecks(sortedDecks.slice(0, 5));

        // Filter out nulls from random cards
        setFeaturedCards(randomCards.filter((card): card is CardData => card !== null));
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="font-heading text-4xl font-bold text-white mb-2">
          Welcome Back
        </h1>
        <p className="text-slate-400 text-lg">
          Manage your decks, explore cards, and build powerful ability graphs
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card variant="elevated">
          <div className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm uppercase tracking-wide">Decks</span>
              <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="text-3xl font-bold text-white">{stats.decks}</div>
            <Link href="/decks" className="text-sm text-amber-500 hover:text-amber-400 mt-2 inline-block">
              View all →
            </Link>
          </div>
        </Card>

        <Card variant="elevated">
          <div className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm uppercase tracking-wide">Favorites</span>
              <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <div className="text-3xl font-bold text-white">{stats.favorites}</div>
            <Link href="/my-cards/favorites" className="text-sm text-amber-500 hover:text-amber-400 mt-2 inline-block">
              View all →
            </Link>
          </div>
        </Card>

        <Card variant="elevated">
          <div className="p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-slate-400 text-sm uppercase tracking-wide">Collections</span>
              <svg className="w-6 h-6 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div className="text-3xl font-bold text-white">{stats.collections}</div>
            <Link href="/my-cards/collections" className="text-sm text-amber-500 hover:text-amber-400 mt-2 inline-block">
              View all →
            </Link>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="font-heading text-2xl font-bold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link href="/search">
            <Card variant="elevated" className="p-6 hover:bg-slate-700 transition-colors cursor-pointer h-full">
              <div className="text-center">
                <svg className="w-12 h-12 text-amber-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h3 className="font-semibold text-white mb-1">Search Cards</h3>
                <p className="text-sm text-slate-400">Find cards by name or filters</p>
              </div>
            </Card>
          </Link>

          <Link href="/decks/builder">
            <Card variant="elevated" className="p-6 hover:bg-slate-700 transition-colors cursor-pointer h-full">
              <div className="text-center">
                <svg className="w-12 h-12 text-amber-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <h3 className="font-semibold text-white mb-1">Create Deck</h3>
                <p className="text-sm text-slate-400">Build a new deck from scratch</p>
              </div>
            </Card>
          </Link>

          <Link href="/builder">
            <Card variant="elevated" className="p-6 hover:bg-slate-700 transition-colors cursor-pointer h-full">
              <div className="text-center">
                <svg className="w-12 h-12 text-amber-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
                <h3 className="font-semibold text-white mb-1">Ability Builder</h3>
                <p className="text-sm text-slate-400">Create ability graphs</p>
              </div>
            </Card>
          </Link>

          <Link href="/browse">
            <Card variant="elevated" className="p-6 hover:bg-slate-700 transition-colors cursor-pointer h-full">
              <div className="text-center">
                <svg className="w-12 h-12 text-amber-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
                <h3 className="font-semibold text-white mb-1">Browse Cards</h3>
                <p className="text-sm text-slate-400">Explore all cards</p>
              </div>
            </Card>
          </Link>
        </div>
      </div>

      {/* Recent Decks */}
      {recentDecks.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-2xl font-bold text-white">Recent Decks</h2>
            <Link href="/decks">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentDecks.map((deck) => (
              <Link key={deck.id} href={`/decks/${deck.id}`}>
                <Card variant="elevated" className="p-6 hover:bg-slate-700 transition-colors cursor-pointer h-full">
                  <h3 className="font-semibold text-white mb-2">{deck.name}</h3>
                  {deck.description && (
                    <p className="text-sm text-slate-400 mb-3 line-clamp-2">{deck.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-slate-500">
                    <span>{deck.format}</span>
                    <span>{deck.card_count} cards</span>
                    {deck.commander_count > 0 && (
                      <span>{deck.commander_count} commander{deck.commander_count > 1 ? 's' : ''}</span>
                    )}
                  </div>
                  <div className="mt-3 text-xs text-slate-500">
                    Updated {new Date(deck.updated_at).toLocaleDateString()}
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Featured Cards */}
      {featuredCards.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-2xl font-bold text-white">Featured Cards</h2>
            <Button
              variant="outline"
              size="sm"
              onClick={async () => {
                try {
                  const card = await cards.getRandom();
                  if (card?.card_id) {
                    router.push(`/cards/${card.card_id}`);
                  }
                } catch (err) {
                  console.error('Failed to get random card:', err);
                }
              }}
            >
              Random Card
            </Button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl">
            {featuredCards.map((card) => (
              <div key={card.card_id} className="flex justify-center">
                <div className="w-48">
                  <CardPreview card={card} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State for New Users */}
      {stats.decks === 0 && stats.favorites === 0 && stats.collections === 0 && (
        <Card variant="bordered" className="p-8 text-center">
          <h3 className="text-xl font-semibold text-white mb-2">Get Started</h3>
          <p className="text-slate-400 mb-6">
            Start by searching for cards, creating your first deck, or exploring the ability builder.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/search">
              <Button variant="primary">Search Cards</Button>
            </Link>
            <Link href="/getting-started">
              <Button variant="outline">Getting Started Guide</Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}

