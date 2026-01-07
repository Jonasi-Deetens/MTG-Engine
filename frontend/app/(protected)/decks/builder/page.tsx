'use client';

// frontend/app/(protected)/decks/builder/page.tsx

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDeckStore } from '@/store/deckStore';
import { decks } from '@/lib/decks';
import { cards, CardData } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { CardPreview } from '@/components/cards/CardPreview';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { DeckCardList } from '@/components/decks/DeckCardList';
import { CommanderSelector } from '@/components/decks/CommanderSelector';
import { FormatSelector } from '@/components/decks/FormatSelector';
import { DeckValidationPanel } from '@/components/decks/DeckValidationPanel';
import { ManaCurveChart } from '@/components/decks/ManaCurveChart';
import { CardTypeBreakdown } from '@/components/decks/CardTypeBreakdown';

export default function DeckBuilderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const deckIdParam = searchParams.get('deck');
  
  const {
    currentDeck,
    validation,
    loading,
    error,
    loadDeck,
    createDeck,
    updateDeck,
    addCard,
    updateCardQuantity,
    removeCard,
    addCommander,
    removeCommander,
    validateDeck,
    clearDeck,
  } = useDeckStore();

  const [deckName, setDeckName] = useState('');
  const [deckDescription, setDeckDescription] = useState('');
  const [deckFormat, setDeckFormat] = useState('Commander');
  const [isPublic, setIsPublic] = useState(false);
  const [saving, setSaving] = useState(false);

  // Card search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CardData[]>([]);
  const [searching, setSearching] = useState(false);
  const debouncedQuery = useDebounce(searchQuery, 500);

  // Load existing deck if deckId is provided
  useEffect(() => {
    if (deckIdParam) {
      const id = parseInt(deckIdParam);
      if (!isNaN(id)) {
        loadDeck(id);
      }
    }
    return () => clearDeck();
  }, [deckIdParam, loadDeck, clearDeck]);

  // Update form when deck loads
  useEffect(() => {
    if (currentDeck) {
      setDeckName(currentDeck.name);
      setDeckDescription(currentDeck.description || '');
      setDeckFormat(currentDeck.format);
      setIsPublic(currentDeck.is_public);
    }
  }, [currentDeck]);

  // Search cards
  useEffect(() => {
    if (debouncedQuery.trim()) {
      setSearching(true);
      cards.search(debouncedQuery, 1, 20)
        .then(response => {
          setSearchResults(response.cards);
        })
        .catch(err => {
          console.error('Search failed:', err);
        })
        .finally(() => {
          setSearching(false);
        });
    } else {
      setSearchResults([]);
    }
  }, [debouncedQuery]);

  const handleSave = async () => {
    if (!deckName.trim()) {
      alert('Please enter a deck name');
      return;
    }

    setSaving(true);
    try {
      if (currentDeck) {
        await updateDeck(currentDeck.id, {
          name: deckName,
          description: deckDescription || undefined,
          format: deckFormat,
          is_public: isPublic,
        });
      } else {
        const newDeckId = await createDeck(deckName, deckFormat, deckDescription);
        router.push(`/decks/builder?deck=${newDeckId}`);
      }
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to save deck');
    } finally {
      setSaving(false);
    }
  };

  const handleAddCard = async (card: CardData) => {
    if (!currentDeck) {
      alert('Please save the deck first');
      return;
    }
    try {
      await addCard(currentDeck.id, card.card_id, 1);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to add card');
    }
  };

  const handleQuantityChange = async (cardId: string, quantity: number) => {
    if (!currentDeck) return;
    try {
      await updateCardQuantity(currentDeck.id, cardId, quantity);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to update quantity');
    }
  };

  const handleRemoveCard = async (cardId: string) => {
    if (!currentDeck) return;
    try {
      await removeCard(currentDeck.id, cardId);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove card');
    }
  };

  const handleAddCommander = async (cardId: string, position: number) => {
    if (!currentDeck) {
      alert('Please save the deck first');
      return;
    }
    try {
      await addCommander(currentDeck.id, cardId, position);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to add commander');
    }
  };

  const handleRemoveCommander = async (cardId: string) => {
    if (!currentDeck) return;
    try {
      await removeCommander(currentDeck.id, cardId);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to remove commander');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-heading text-3xl font-bold text-white mb-2">
            Deck Builder
          </h1>
          <p className="text-slate-400">
            {currentDeck ? `Editing: ${currentDeck.name}` : 'Create a new deck'}
          </p>
        </div>
        <div className="flex gap-2">
          {currentDeck && (
            <Button
              onClick={() => router.push(`/decks/${currentDeck.id}`)}
              variant="outline"
            >
              View Deck
            </Button>
          )}
          <Button
            onClick={() => router.push('/decks')}
            variant="outline"
          >
            Back to Decks
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Deck Info & Cards */}
        <div className="lg:col-span-2 space-y-6">
          {/* Deck Info */}
          <Card variant="elevated">
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Deck Name *
                </label>
                <input
                  type="text"
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  placeholder="My Awesome Deck"
                  className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Description
                </label>
                <textarea
                  value={deckDescription}
                  onChange={(e) => setDeckDescription(e.target.value)}
                  placeholder="Describe your deck..."
                  rows={3}
                  className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
                />
              </div>
              <FormatSelector
                value={deckFormat}
                onChange={setDeckFormat}
                disabled={!!currentDeck}
              />
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="isPublic"
                  checked={isPublic}
                  onChange={(e) => setIsPublic(e.target.checked)}
                  className="w-4 h-4 text-amber-600 bg-slate-700 border-slate-600 rounded focus:ring-amber-500"
                />
                <label htmlFor="isPublic" className="text-sm text-slate-300">
                  Make deck public
                </label>
              </div>
              <Button
                onClick={handleSave}
                disabled={saving || loading || !deckName.trim()}
                variant="primary"
                className="w-full"
              >
                {saving ? 'Saving...' : currentDeck ? 'Update Deck' : 'Create Deck'}
              </Button>
            </div>
          </Card>

          {/* Commanders (for Commander format) */}
          {deckFormat === 'Commander' && (
            <Card variant="elevated">
              <div className="p-6">
                <CommanderSelector
                  commanders={currentDeck?.commanders.map(c => c.card) || []}
                  onAdd={handleAddCommander}
                  onRemove={handleRemoveCommander}
                  maxCommanders={2}
                />
              </div>
            </Card>
          )}

          {/* Card Search */}
          <Card variant="elevated">
            <div className="p-6 space-y-4">
              <h3 className="text-lg font-semibold text-white">Search Cards</h3>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for cards..."
                className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
              />
              {searching ? (
                <CardGridSkeleton count={8} />
              ) : searchResults.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {searchResults.map((card) => (
                    <div
                      key={card.card_id}
                      className="cursor-pointer hover:scale-105 transition-transform"
                      onClick={() => handleAddCard(card)}
                    >
                      <CardPreview card={card} />
                    </div>
                  ))}
                </div>
              ) : debouncedQuery ? (
                <p className="text-slate-400 text-center py-4">No cards found</p>
              ) : null}
            </div>
          </Card>

          {/* Deck Cards List */}
          {currentDeck && (
            <Card variant="elevated">
              <div className="p-6 space-y-4">
                <h3 className="text-lg font-semibold text-white">
                  Deck ({currentDeck.card_count} cards)
                </h3>
                <DeckCardList
                  cards={currentDeck.cards}
                  onQuantityChange={handleQuantityChange}
                  onRemove={handleRemoveCard}
                  showControls={true}
                />
              </div>
            </Card>
          )}
        </div>

        {/* Right Column - Analytics & Validation */}
        <div className="space-y-6">
          {/* Validation */}
          {currentDeck && (
            <Card variant="elevated">
              <div className="p-6">
                <DeckValidationPanel validation={validation} />
              </div>
            </Card>
          )}

          {/* Mana Curve */}
          {currentDeck && currentDeck.cards.length > 0 && (
            <Card variant="elevated">
              <div className="p-6">
                <ManaCurveChart cards={currentDeck.cards} />
              </div>
            </Card>
          )}

          {/* Card Type Breakdown */}
          {currentDeck && currentDeck.cards.length > 0 && (
            <Card variant="elevated">
              <div className="p-6">
                <CardTypeBreakdown cards={currentDeck.cards} />
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

