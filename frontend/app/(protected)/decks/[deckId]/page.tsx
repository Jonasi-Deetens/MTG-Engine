'use client';

// frontend/app/(protected)/decks/[deckId]/page.tsx

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useDeckStore } from '@/store/deckStore';
import { decks } from '@/lib/decks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { DeckCardList } from '@/components/decks/DeckCardList';
import { DeckValidationPanel } from '@/components/decks/DeckValidationPanel';
import { ManaCurveChart } from '@/components/decks/ManaCurveChart';
import { CardTypeBreakdown } from '@/components/decks/CardTypeBreakdown';
import { CardPreview } from '@/components/cards/CardPreview';
import { DeckDetailSkeleton } from '@/components/skeletons/DeckDetailSkeleton';

export default function DeckDetailPage() {
  const params = useParams();
  const router = useRouter();
  const deckId = parseInt(params.deckId as string);
  
  const {
    currentDeck,
    validation,
    loading,
    error,
    loadDeck,
    deleteDeck,
    validateDeck,
  } = useDeckStore();

  const [exporting, setExporting] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    if (!isNaN(deckId)) {
      setIsInitialLoad(true);
      loadDeck(deckId).finally(() => {
        setIsInitialLoad(false);
      });
    }
  }, [deckId, loadDeck]);

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${currentDeck?.name}"?`)) return;
    
    try {
      await deleteDeck(deckId);
      router.push('/decks');
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to delete deck');
    }
  };

  const handleExport = async (format: 'text' | 'json') => {
    setExporting(true);
    try {
      const result = await decks.exportDeck(deckId, format);
      const blob = new Blob([result.data], { type: format === 'json' ? 'application/json' : 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${result.deck_name.replace(/\s+/g, '_')}.${format === 'json' ? 'json' : 'txt'}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to export deck');
    } finally {
      setExporting(false);
    }
  };

  if (loading || (isInitialLoad && !currentDeck && !error)) {
    return <DeckDetailSkeleton />;
  }

  if (error || !currentDeck) {
    return (
      <div className="min-h-screen bg-[color:var(--theme-bg-primary)] p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded-lg p-6 text-[color:var(--theme-status-error)]">
            <h1 className="text-2xl font-bold mb-2">Error</h1>
            <p>{error || 'Deck not found'}</p>
            <Button
              onClick={() => router.push('/decks')}
              variant="outline"
              className="mt-4"
            >
              Back to Decks
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Button
            onClick={() => router.push('/decks')}
            variant="outline"
            className="mb-2"
          >
            ← Back to Decks
          </Button>
          <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
            {currentDeck.name}
          </h1>
          {currentDeck.description && (
            <p className="text-[color:var(--theme-text-secondary)] mb-2">{currentDeck.description}</p>
          )}
          <div className="flex items-center gap-4 text-sm text-[color:var(--theme-text-secondary)]">
            <span>Format: {currentDeck.format}</span>
            <span>{currentDeck.card_count} cards</span>
            {currentDeck.commander_count > 0 && (
              <span>{currentDeck.commander_count} commander{currentDeck.commander_count > 1 ? 's' : ''}</span>
            )}
            {currentDeck.is_public && (
              <span className="bg-[color:var(--theme-status-success)] text-[color:var(--theme-button-primary-text)] px-2 py-1 rounded text-xs">Public</span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => router.push(`/decks/builder?deck=${deckId}`)}
            variant="primary"
          >
            Edit Deck
          </Button>
          <Button
            onClick={handleDelete}
            variant="outline"
            className="text-[color:var(--theme-status-error)] hover:opacity-90"
          >
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Commanders */}
          {currentDeck.commanders.length > 0 && (
            <Card variant="elevated">
              <div className="p-6 space-y-4">
                <h2 className="text-xl font-semibold text-[color:var(--theme-text-primary)]">Commanders</h2>
                <div className="flex gap-4">
                  {currentDeck.commanders.map((commander, index) => (
                    <div key={commander.card_id} className="text-center">
                      <CardPreview card={commander.card} />
                      <p className="text-xs text-[color:var(--theme-text-secondary)] mt-1">
                        Commander {index + 1}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
          )}

          {/* Deck List */}
          <Card variant="elevated">
            <div className="p-6 space-y-4">
              <h2 className="text-xl font-semibold text-[color:var(--theme-text-primary)]">
                Deck List ({currentDeck.card_count} cards)
              </h2>
              <DeckCardList
                cards={currentDeck.cards}
                showControls={false}
              />
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Validation */}
          <Card variant="elevated">
            <div className="p-6">
              <DeckValidationPanel validation={validation} />
            </div>
          </Card>

          {/* Price Summary */}
          {currentDeck.cards.length > 0 && (() => {
            const cardsWithPrices = currentDeck.cards.filter(
              (dc) => dc.card.prices?.usd
            );
            if (cardsWithPrices.length === 0) return null;

            const totalPrice = currentDeck.cards.reduce((sum, dc) => {
              const price = dc.card.prices?.usd
                ? parseFloat(dc.card.prices.usd) * dc.quantity
                : 0;
              return sum + price;
            }, 0);

            const cardCount = currentDeck.cards.reduce(
              (sum, dc) => sum + dc.quantity,
              0
            );
            const avgPrice = totalPrice / cardCount;

            const mostExpensive = [...currentDeck.cards]
              .filter((dc) => dc.card.prices?.usd)
              .sort(
                (a, b) =>
                  parseFloat(b.card.prices!.usd!) -
                  parseFloat(a.card.prices!.usd!)
              )
              .slice(0, 3);

            return (
              <Card variant="elevated">
                <div className="p-6 space-y-4">
                  <h2 className="text-xl font-semibold text-[color:var(--theme-text-primary)]">
                    Price Summary
                  </h2>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm text-[color:var(--theme-text-secondary)] mb-1">
                        Total Deck Price
                      </div>
                      <div className="text-2xl font-bold text-[color:var(--theme-accent-primary)]">
                        ${totalPrice.toFixed(2)}
                      </div>
                    </div>
                    <div className="pt-2 border-t border-[color:var(--theme-border-default)]/50">
                      <div className="text-sm text-[color:var(--theme-text-secondary)] mb-1">
                        Average Card Price
                      </div>
                      <div className="text-lg font-semibold text-[color:var(--theme-text-secondary)]">
                        ${avgPrice.toFixed(2)}
                      </div>
                    </div>
                    {mostExpensive.length > 0 && (
                      <div className="pt-2 border-t border-[color:var(--theme-border-default)]/50">
                        <div className="text-sm text-[color:var(--theme-text-secondary)] mb-2">
                          Most Expensive Cards
                        </div>
                        <div className="space-y-1">
                          {mostExpensive.map((dc) => (
                            <div
                              key={dc.card_id}
                              className="flex items-center justify-between text-sm"
                            >
                              <span className="text-[color:var(--theme-text-secondary)] truncate flex-1">
                                {dc.card.name}
                              </span>
                              <span className="text-[color:var(--theme-accent-primary)] font-semibold ml-2">
                                ${parseFloat(dc.card.prices!.usd!).toFixed(2)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            );
          })()}

          {/* Mana Curve */}
          {currentDeck.cards.length > 0 && (
            <Card variant="elevated">
              <div className="p-6">
                <ManaCurveChart cards={currentDeck.cards} />
              </div>
            </Card>
          )}

          {/* Card Type Breakdown */}
          {currentDeck.cards.length > 0 && (
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

