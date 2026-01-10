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
import { QuickActions } from '@/components/dashboard/QuickActions';
import { BookOpen, Heart, Folder } from 'lucide-react';

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
      <div className="min-h-screen bg-angel-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="font-heading text-4xl font-bold text-[color:var(--theme-text-primary)] mb-2">
          Welcome Back
        </h1>
        <p className="text-[color:var(--theme-text-secondary)] text-lg">
          Manage your decks, explore cards, and build powerful ability graphs
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card variant="elevated" className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-amber-600/20 to-transparent rounded-bl-full"></div>
          <div className="p-6 relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[color:var(--theme-text-secondary)] text-sm uppercase tracking-wide">Decks</span>
              <div className="p-2 rounded-lg bg-[color:var(--theme-accent-primary)]/10 border border-[color:var(--theme-accent-primary)]/20">
                <BookOpen className="w-6 h-6 text-[color:var(--theme-accent-primary)]" />
              </div>
            </div>
            <div className="text-4xl font-bold text-[color:var(--theme-text-primary)] mb-2">{stats.decks}</div>
            <Link href="/decks" className="text-sm text-[color:var(--theme-accent-primary)] hover:text-theme-accent-hover inline-flex items-center gap-1 transition-colors">
              View all <span>→</span>
            </Link>
          </div>
        </Card>

        <Card variant="elevated" className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-pink-600/20 to-transparent rounded-bl-full"></div>
          <div className="p-6 relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[color:var(--theme-text-muted)] text-sm uppercase tracking-wide">Favorites</span>
              <div className="p-2 rounded-lg bg-pink-500/10 border border-pink-500/20">
                <Heart className="w-6 h-6 text-pink-500" fill="currentColor" />
              </div>
            </div>
            <div className="text-4xl font-bold text-white mb-2">{stats.favorites}</div>
            <Link href="/my-cards/favorites" className="text-sm text-pink-500 hover:text-pink-400 inline-flex items-center gap-1 transition-colors">
              View all <span>→</span>
            </Link>
          </div>
        </Card>

        <Card variant="elevated" className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-600/20 to-transparent rounded-bl-full"></div>
          <div className="p-6 relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[color:var(--theme-text-muted)] text-sm uppercase tracking-wide">Collections</span>
              <div className="p-2 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <Folder className="w-6 h-6 text-blue-500" />
              </div>
            </div>
            <div className="text-4xl font-bold text-white mb-2">{stats.collections}</div>
            <Link href="/my-cards/collections" className="text-sm text-blue-500 hover:text-blue-400 inline-flex items-center gap-1 transition-colors">
              View all <span>→</span>
            </Link>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <QuickActions />

      {/* Recent Decks */}
      {recentDecks.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)]">Recent Decks</h2>
            <Link href="/decks">
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentDecks.map((deck) => (
              <Link key={deck.id} href={`/decks/${deck.id}`}>
                <Card variant="elevated" className="p-6 transition-colors cursor-pointer h-full">
                  <h3 className="font-semibold text-[color:var(--theme-text-primary)] mb-2">{deck.name}</h3>
                  {deck.description && (
                    <p className="text-sm text-[color:var(--theme-text-secondary)] mb-3 line-clamp-2">{deck.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-[color:var(--theme-text-secondary)]">
                    <span>{deck.format}</span>
                    <span>{deck.card_count} cards</span>
                    {deck.commander_count > 0 && (
                      <span>{deck.commander_count} commander{deck.commander_count > 1 ? 's' : ''}</span>
                    )}
                  </div>
                  <div className="mt-3 text-xs text-[color:var(--theme-text-muted)]">
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
            <h2 className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)]">Featured Cards</h2>
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
          <h3 className="text-xl font-semibold text-[color:var(--theme-text-primary)] mb-2">Get Started</h3>
          <p className="text-[color:var(--theme-text-secondary)] mb-6">
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

