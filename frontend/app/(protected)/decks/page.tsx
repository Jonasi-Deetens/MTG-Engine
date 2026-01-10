'use client';

// frontend/app/(protected)/decks/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { decks, DeckResponse } from '@/lib/decks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { EmptyState } from '@/components/ui/EmptyState';
import { DeckCard } from '@/components/decks/DeckCard';
import { BookOpen, SearchX } from 'lucide-react';
import Link from 'next/link';

export default function DecksPage() {
  const router = useRouter();
  const [decksList, setDecksList] = useState<DeckResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formatFilter, setFormatFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const loadDecks = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await decks.getDecks(formatFilter || undefined);
      setDecksList(response);
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to load decks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDecks();
  }, [formatFilter]);

  const filteredDecks = decksList.filter(deck =>
    deck.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      await decks.deleteDeck(id);
      setDecksList(decksList.filter(d => d.id !== id));
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to delete deck');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
            My Decks
          </h1>
          <p className="text-[color:var(--theme-text-secondary)]">
            Create and manage your Magic: The Gathering decks
          </p>
        </div>
        <Link href="/decks/builder">
          <Button variant="primary">
            Create New Deck
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-4 items-center">
        <div className="flex-1">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search decks..."
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
        <select
          value={formatFilter}
          onChange={(e) => setFormatFilter(e.target.value)}
          className="px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
        >
          <option value="">All Formats</option>
          <option value="Commander">Commander</option>
          <option value="Standard">Standard</option>
          <option value="Modern">Modern</option>
          <option value="Pauper">Pauper</option>
          <option value="Legacy">Legacy</option>
          <option value="Vintage">Vintage</option>
        </select>
      </div>

      {error && (
        <div className="p-4 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg text-[color:var(--theme-status-error)]">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
        </div>
      ) : filteredDecks.length === 0 ? (
        <Card variant="elevated">
          {decksList.length === 0 ? (
            <EmptyState
              icon={BookOpen}
              title="No decks yet"
              description="Create your first deck to start building your collection. You can add cards, set commanders, and validate your deck."
              actionLabel="Create New Deck"
              actionHref="/decks/builder"
            />
          ) : (
            <EmptyState
              icon={SearchX}
              title="No decks found"
              description="Try adjusting your search query or format filter to find what you're looking for."
            />
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDecks.map((deck) => (
            <DeckCard
              key={deck.id}
              deck={deck}
              showActions={true}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  );
}

