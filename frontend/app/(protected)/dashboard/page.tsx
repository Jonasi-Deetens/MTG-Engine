'use client';

// frontend/app/(protected)/dashboard/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { decks, DeckDetailResponse } from '@/lib/decks';
import { collections } from '@/lib/collections';
import { cards } from '@/lib/api';
import { DeckResponse } from '@/lib/decks';
import { CardData } from '@/components/cards/CardPreview';
import { CardPreview } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { DeckCard } from '@/components/decks/DeckCard';
import { DashboardSkeleton } from '@/components/skeletons/DashboardSkeleton';
import { BookOpen, Heart, Folder } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState({
    decks: 0,
    favorites: 0,
    collections: 0,
  });
  const [recentDecks, setRecentDecks] = useState<DeckResponse[]>([]);
  const [deckDetails, setDeckDetails] = useState<Record<number, DeckDetailResponse>>({});
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
        const topDecks = sortedDecks.slice(0, 5);
        setRecentDecks(topDecks);

        // Fetch deck details for all decks to get commander/first card images
        const allDeckDetails: Record<number, DeckDetailResponse> = {};
        await Promise.all(
          topDecks.map(async (deck) => {
            try {
              const detail = await decks.getDeck(deck.id);
              allDeckDetails[deck.id] = detail;
            } catch (err) {
              console.error(`Failed to load details for deck ${deck.id}:`, err);
            }
          })
        );
        setDeckDetails(allDeckDetails);

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
    return <DashboardSkeleton />;
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
              <div className="p-2 rounded-lg">
                <BookOpen className="w-6 h-6 text-[color:var(--theme-accent-primary)]" />
              </div>
            </div>
            <div className="text-4xl font-bold text-[color:var(--theme-text-primary)] mb-4">{stats.decks}</div>
            <div className="flex flex-col gap-2">
              <Link href="/decks">
                <Button variant="primary" size="sm" className="w-full">
                  View All
                </Button>
              </Link>
              <Link href="/decks/builder">
                <Button variant="outline" size="sm" className="w-full">
                  Create New
                </Button>
              </Link>
            </div>
          </div>
        </Card>

        <Card variant="elevated" className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-pink-600/20 to-transparent rounded-bl-full"></div>
          <div className="p-6 relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[color:var(--theme-text-secondary)] text-sm uppercase tracking-wide">Favorites</span>
              <div className="p-2 rounded-lg">
                <Heart className="w-6 h-6 text-pink-500" fill="currentColor" />
              </div>
            </div>
            <div className="text-4xl font-bold text-[color:var(--theme-text-primary)] mb-4">{stats.favorites}</div>
            <Link href="/my-cards/favorites">
              <Button variant="primary" size="sm" className="w-full">
                View All
              </Button>
            </Link>
          </div>
        </Card>

        <Card variant="elevated" className="relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-600/20 to-transparent rounded-bl-full"></div>
          <div className="p-6 relative">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[color:var(--theme-text-secondary)] text-sm uppercase tracking-wide">Collections</span>
              <div className="p-2 rounded-lg">
                <Folder className="w-6 h-6 text-blue-500" />
              </div>
            </div>
            <div className="text-4xl font-bold text-[color:var(--theme-text-primary)] mb-4">{stats.collections}</div>
            <div className="flex flex-col gap-2">
              <Link href="/my-cards/collections">
                <Button variant="primary" size="sm" className="w-full">
                  View All
                </Button>
              </Link>
              <Link href="/my-cards/collections">
                <Button variant="outline" size="sm" className="w-full">
                  Create New
                </Button>
              </Link>
            </div>
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
            {recentDecks.map((deck) => {
              const detail = deckDetails[deck.id];
              return (
                <Link key={deck.id} href={`/decks/${deck.id}`} className="block flex">
                  <DeckCard
                    deck={deck}
                    deckDetail={detail}
                    showActions={false}
                  />
                </Link>
              );
            })}
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

