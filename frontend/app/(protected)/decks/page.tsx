'use client';

// frontend/app/(protected)/decks/page.tsx

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { decks, DeckResponse } from '@/lib/decks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
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
          <h1 className="font-heading text-3xl font-bold text-white mb-2">
            My Decks
          </h1>
          <p className="text-slate-400">
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
            className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
          />
        </div>
        <select
          value={formatFilter}
          onChange={(e) => setFormatFilter(e.target.value)}
          className="px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
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
        <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
        </div>
      ) : filteredDecks.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-slate-400 text-lg">No decks found</p>
          <p className="text-slate-500 text-sm mt-2">
            {decksList.length === 0
              ? 'Create your first deck to get started'
              : 'Try adjusting your search or filters'}
          </p>
          {decksList.length === 0 && (
            <Link href="/decks/builder" className="mt-4 inline-block">
              <Button variant="primary">Create New Deck</Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDecks.map((deck) => (
            <Card key={deck.id} variant="elevated">
              <div className="p-6 space-y-4">
                <div>
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-xl font-semibold text-white">
                      {deck.name}
                    </h3>
                    {deck.is_public && (
                      <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                        Public
                      </span>
                    )}
                  </div>
                  {deck.description && (
                    <p className="text-slate-400 text-sm mb-2">
                      {deck.description}
                    </p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-slate-500">
                    <span>Format: {deck.format}</span>
                    <span>{deck.card_count} cards</span>
                    {deck.commander_count > 0 && (
                      <span>{deck.commander_count} commander{deck.commander_count > 1 ? 's' : ''}</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 pt-4 border-t border-slate-700">
                  <Link href={`/decks/${deck.id}`} className="flex-1">
                    <Button variant="primary" size="sm" className="w-full">
                      View
                    </Button>
                  </Link>
                  <Link href={`/decks/builder?deck=${deck.id}`} className="flex-1">
                    <Button variant="outline" size="sm" className="w-full">
                      Edit
                    </Button>
                  </Link>
                  <Button
                    onClick={() => handleDelete(deck.id, deck.name)}
                    variant="outline"
                    size="sm"
                    className="text-red-400 hover:text-red-300"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

