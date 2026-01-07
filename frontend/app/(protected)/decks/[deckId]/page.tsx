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
import { DeckImportExport } from '@/components/decks/DeckImportExport';
import { CardPreview } from '@/components/cards/CardPreview';

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
  const [showImportExport, setShowImportExport] = useState(false);

  useEffect(() => {
    if (!isNaN(deckId)) {
      loadDeck(deckId);
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

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  if (error || !currentDeck) {
    return (
      <div className="min-h-screen bg-slate-900 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-900/50 border border-red-600 rounded-lg p-6 text-red-200">
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
          <h1 className="font-heading text-3xl font-bold text-white mb-2">
            {currentDeck.name}
          </h1>
          {currentDeck.description && (
            <p className="text-slate-400 mb-2">{currentDeck.description}</p>
          )}
          <div className="flex items-center gap-4 text-sm text-slate-500">
            <span>Format: {currentDeck.format}</span>
            <span>{currentDeck.card_count} cards</span>
            {currentDeck.commander_count > 0 && (
              <span>{currentDeck.commander_count} commander{currentDeck.commander_count > 1 ? 's' : ''}</span>
            )}
            {currentDeck.is_public && (
              <span className="bg-green-600 text-white px-2 py-1 rounded text-xs">Public</span>
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
            onClick={() => setShowImportExport(!showImportExport)}
            variant="outline"
          >
            {showImportExport ? 'Hide' : 'Import/Export'}
          </Button>
          <Button
            onClick={handleDelete}
            variant="outline"
            className="text-red-400 hover:text-red-300"
          >
            Delete
          </Button>
        </div>
      </div>

      {showImportExport && (
        <Card variant="elevated">
          <div className="p-6">
            <DeckImportExport deckId={deckId} onImportSuccess={() => loadDeck(deckId)} />
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Commanders */}
          {currentDeck.commanders.length > 0 && (
            <Card variant="elevated">
              <div className="p-6 space-y-4">
                <h2 className="text-xl font-semibold text-white">Commanders</h2>
                <div className="flex gap-4">
                  {currentDeck.commanders.map((commander, index) => (
                    <div key={commander.card_id} className="text-center">
                      <CardPreview card={commander.card} />
                      <p className="text-xs text-slate-400 mt-1">
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
              <h2 className="text-xl font-semibold text-white">
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

