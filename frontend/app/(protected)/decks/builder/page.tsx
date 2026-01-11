'use client';

// frontend/app/(protected)/decks/builder/page.tsx

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useDeckStore } from '@/store/deckStore';
import { decks } from '@/lib/decks';
import { cards, CardData } from '@/lib/api';
import { useDebounce } from '@/lib/hooks';
import { Button } from '@/components/ui/Button';
import { SearchInput } from '@/components/ui/SearchInput';
import { Card } from '@/components/ui/Card';
import { CardPreview } from '@/components/cards/CardPreview';
import { CardModal } from '@/components/ui/CardModal';
import { CardGridSkeleton } from '@/components/skeletons/CardSkeleton';
import { DeckCardList } from '@/components/decks/DeckCardList';
import { DeckCardResponse } from '@/lib/decks';
import { CommanderSelector } from '@/components/decks/CommanderSelector';
import { FormatSelector } from '@/components/decks/FormatSelector';
import { DeckValidationPanel } from '@/components/decks/DeckValidationPanel';
import { ManaCurveChart } from '@/components/decks/ManaCurveChart';
import { CardTypeBreakdown } from '@/components/decks/CardTypeBreakdown';
import { DeckImport } from '@/components/decks/DeckImport';
import { Collapsible } from '@/components/ui/Collapsible';

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
    refreshDeck,
  } = useDeckStore();

  const [deckName, setDeckName] = useState('');
  const [deckDescription, setDeckDescription] = useState('');
  const [deckFormat, setDeckFormat] = useState('Commander');
  const [isPublic, setIsPublic] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showImport, setShowImport] = useState(false);

  // Card search
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CardData[]>([]);
  const [searching, setSearching] = useState(false);
  const debouncedQuery = useDebounce(searchQuery, 500);
  
  // Hovered card for preview
  const [hoveredCard, setHoveredCard] = useState<DeckCardResponse | null>(null);
  // Modal state
  const [modalCard, setModalCard] = useState<CardData | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

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
    <div className="w-full space-y-3">
      {/* Compact Header */}
      <div className="flex items-center justify-between gap-4 pb-3 border-b border-[color:var(--theme-card-border)]">
        <div className="flex-1">
          <h1 className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)] mb-1">
            {currentDeck ? `Editing: ${currentDeck.name}` : 'Deck Builder'}
          </h1>
        </div>
        <div className="flex gap-2">
          {currentDeck && (
            <>
              <Button
                onClick={() => setShowImport(true)}
                variant="outline"
                size="sm"
              >
                Import
              </Button>
              <Button
                onClick={() => router.push(`/decks/${currentDeck.id}`)}
                variant="outline"
                size="sm"
              >
                View
              </Button>
            </>
          )}
          <Button
            onClick={() => router.push('/decks')}
            variant="outline"
            size="sm"
          >
            Back
          </Button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded text-[color:var(--theme-status-error)] text-sm">
          {error}
        </div>
      )}

      {/* Single Column Layout */}
      <div className="space-y-3">
        {/* Compact Deck Info */}
        <Card variant="elevated">
          <div className="p-3 space-y-2">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <div>
                <label className="block text-xs font-medium text-[color:var(--theme-text-secondary)] mb-1">
                  Deck Name *
                </label>
                <input
                  type="text"
                  value={deckName}
                  onChange={(e) => setDeckName(e.target.value)}
                  placeholder="My Awesome Deck"
                  className="w-full px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[color:var(--theme-text-secondary)] mb-1">
                  Description
                </label>
                <input
                  type="text"
                  value={deckDescription}
                  onChange={(e) => setDeckDescription(e.target.value)}
                  placeholder="Describe your deck..."
                  className="w-full px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
              <div className="flex items-end gap-2">
                <div className="flex-1">
                  <FormatSelector
                    value={deckFormat}
                    onChange={setDeckFormat}
                    disabled={!!currentDeck}
                  />
                </div>
                <div className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    id="isPublic"
                    checked={isPublic}
                    onChange={(e) => setIsPublic(e.target.checked)}
                    className="w-4 h-4 text-[color:var(--theme-accent-primary)] bg-[color:var(--theme-input-bg)] border-[color:var(--theme-input-border)] rounded focus:ring-[color:var(--theme-border-focus)]"
                  />
                  <label htmlFor="isPublic" className="text-xs text-[color:var(--theme-text-secondary)]">
                    Public
                  </label>
                </div>
                <Button
                  onClick={handleSave}
                  disabled={saving || loading || !deckName.trim()}
                  variant="primary"
                  size="sm"
                >
                  {saving ? 'Saving...' : currentDeck ? 'Update' : 'Create'}
                </Button>
              </div>
            </div>
          </div>
        </Card>

        {/* Commanders (for Commander format) */}
        {deckFormat === 'Commander' && (
          <Card variant="elevated">
            <div className="p-3">
              <CommanderSelector
                commanders={currentDeck?.commanders.map(c => c.card) || []}
                onAdd={handleAddCommander}
                onRemove={handleRemoveCommander}
                maxCommanders={2}
              />
            </div>
          </Card>
        )}

        {/* Deck Cards - 3 Column Layout */}
        {currentDeck && (
          <Card variant="elevated">
            <div className="p-3 space-y-3">
              {/* Search Cards - Integrated at top */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
                    Deck ({currentDeck.card_count} cards)
                  </h3>
                </div>
                <SearchInput
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder="Search for cards..."
                />
                {searching ? (
                  <div className="text-xs text-[color:var(--theme-text-secondary)] py-1">Searching...</div>
                ) : searchResults.length > 0 ? (
                  <div className="space-y-0.5 max-h-32 overflow-y-auto border border-[color:var(--theme-card-border)] rounded p-1.5">
                    {searchResults.map((card) => {
                      const manaCost = card.mana_cost || '';
                      
                      return (
                        <button
                          key={card.card_id}
                          onClick={() => handleAddCard(card)}
                          className="w-full text-left px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] rounded text-xs transition-colors"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-[color:var(--theme-text-primary)] flex-1">
                              {card.name}
                            </span>
                            {manaCost && (
                              <span className="text-[color:var(--theme-accent-primary)] font-mono text-xs">
                                {manaCost}
                              </span>
                            )}
                            <span className="text-xs text-[color:var(--theme-accent-primary)]">+ Add</span>
                          </div>
                        </button>
                      );
                    })}
                  </div>
                ) : debouncedQuery ? (
                  <p className="text-xs text-[color:var(--theme-text-secondary)] text-center py-1">No cards found</p>
                ) : null}
              </div>
              <div className="grid grid-cols-3 gap-4">
                {/* Left Section - 2 Columns */}
                <div className="grid grid-cols-2 gap-x-4">
                  {/* Left Column 1 - Creatures */}
                  <div>
                    <DeckCardList
                      cards={currentDeck.cards}
                      onQuantityChange={handleQuantityChange}
                      onRemove={handleRemoveCard}
                      showControls={true}
                      filterTypes={['Creature']}
                      onCardHover={setHoveredCard}
                      onCardClick={(deckCard) => {
                        setModalCard(deckCard.card);
                        setIsModalOpen(true);
                      }}
                    />
                  </div>

                  {/* Left Column 2 - Instants & Sorceries */}
                  <div>
                    <DeckCardList
                      cards={currentDeck.cards}
                      onQuantityChange={handleQuantityChange}
                      onRemove={handleRemoveCard}
                      showControls={true}
                      filterTypes={['Instant', 'Sorcery']}
                      onCardHover={setHoveredCard}
                      onCardClick={(deckCard) => {
                        setModalCard(deckCard.card);
                        setIsModalOpen(true);
                      }}
                    />
                  </div>
                </div>

                {/* Middle Section - Commander above Preview */}
                <div className="space-y-4">
                  {/* Commander (if exists) */}
                  {deckFormat === 'Commander' && currentDeck.commanders.length > 0 && (
                    <div>
                      <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)] mb-2">
                        Commander{currentDeck.commanders.length > 1 ? 's' : ''} ({currentDeck.commanders.length})
                      </div>
                      <div>
                        {currentDeck.commanders.map((commander) => {
                          const manaCost = commander.card.mana_cost || '';
                          return (
                            <div
                              key={commander.card.card_id}
                              className="flex items-center gap-2 px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm cursor-pointer"
                              onMouseEnter={() => setHoveredCard({ card: commander.card, quantity: 1, card_id: commander.card_id })}
                              onMouseLeave={() => setHoveredCard(null)}
                              onClick={() => {
                                setModalCard(commander.card);
                                setIsModalOpen(true);
                              }}
                            >
                              <span className="flex-shrink-0 w-5 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                                1x
                              </span>
                              <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] truncate text-xs">
                                {commander.card.name}
                              </span>
                              {manaCost && (
                                <span className="flex-shrink-0 text-[color:var(--theme-accent-primary)] font-mono text-xs">
                                  {manaCost}
                                </span>
                              )}
                              <div className="flex items-center gap-0.5 flex-shrink-0">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemoveCommander(commander.card.card_id);
                                  }}
                                  className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20 rounded transition-colors text-xs"
                                  title="Remove"
                                >
                                  ×
                                </button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {/* Card Preview */}
                  <div className="flex items-start justify-center min-h-[300px]">
                    {hoveredCard ? (
                      <div className="sticky top-4 w-[280px]">
                        {hoveredCard.card.image_uris?.normal || hoveredCard.card.image_uris?.small || hoveredCard.card.image_uris?.large ? (
                          <>
                            <CardPreview card={hoveredCard.card} disableClick={true} />
                            {hoveredCard.quantity > 1 && (
                              <div className="mt-2 text-center text-xs text-[color:var(--theme-text-secondary)]">
                                Quantity: {hoveredCard.quantity}x
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="aspect-[63/88] bg-[color:var(--theme-card-hover)] rounded-xl flex items-center justify-center text-[color:var(--theme-text-secondary)] text-sm p-4 text-center">
                            <div>
                              <div className="font-medium mb-1">{hoveredCard.card.name}</div>
                              {hoveredCard.card.mana_cost && (
                                <div className="text-xs font-mono text-[color:var(--theme-accent-primary)]">
                                  {hoveredCard.card.mana_cost}
                                </div>
                              )}
                              {hoveredCard.card.type_line && (
                                <div className="text-xs mt-1">{hoveredCard.card.type_line}</div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex items-center justify-center h-full text-sm text-[color:var(--theme-text-secondary)] text-center px-4">
                        Hover over a card to see preview
                      </div>
                    )}
                  </div>
                </div>

                {/* Right Section - 2 Columns */}
                <div className="grid grid-cols-2 gap-x-4">
                  {/* Right Column 1 - Artifacts & Enchantments */}
                  <div>
                    <DeckCardList
                      cards={currentDeck.cards}
                      onQuantityChange={handleQuantityChange}
                      onRemove={handleRemoveCard}
                      showControls={true}
                      filterTypes={['Artifact', 'Enchantment']}
                      onCardHover={setHoveredCard}
                      onCardClick={(deckCard) => {
                        setModalCard(deckCard.card);
                        setIsModalOpen(true);
                      }}
                    />
                  </div>

                  {/* Right Column 2 - Lands, Planeswalkers & Other */}
                  <div>
                    <DeckCardList
                      cards={currentDeck.cards}
                      onQuantityChange={handleQuantityChange}
                      onRemove={handleRemoveCard}
                      showControls={true}
                      filterTypes={['Land', 'Planeswalker', 'Other']}
                      onCardHover={setHoveredCard}
                      onCardClick={(deckCard) => {
                        setModalCard(deckCard.card);
                        setIsModalOpen(true);
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Second Section - Analytics */}
        {currentDeck && (
          <Card variant="elevated">
            <div className="p-3 space-y-3">
              <h3 className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Analytics</h3>
              
              {/* Validation */}
              <div>
                <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)] mb-2">Validation</h4>
                <DeckValidationPanel validation={validation} />
              </div>

              {/* Price */}
              {currentDeck.cards.length > 0 && (() => {
                const totalPrice = currentDeck.cards.reduce((sum, deckCard) => {
                  const price = parseFloat(deckCard.card.prices?.usd || '0');
                  return sum + (price * deckCard.quantity);
                }, 0);
                
                return totalPrice > 0 ? (
                  <div>
                    <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)] mb-1">Deck Price</h4>
                    <div className="text-lg font-semibold text-[color:var(--theme-accent-primary)]">
                      ${totalPrice.toFixed(2)}
                    </div>
                  </div>
                ) : null;
              })()}

              {/* Mana Curve & Card Types */}
              {currentDeck.cards.length > 0 && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)] mb-2">Mana Curve</h4>
                    <ManaCurveChart cards={currentDeck.cards} />
                  </div>
                  <div>
                    <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)] mb-2">Card Types</h4>
                    <CardTypeBreakdown cards={currentDeck.cards} />
                  </div>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Card Modal */}
      {modalCard && modalCard.image_uris && (
        <CardModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setModalCard(null);
          }}
          card={modalCard}
          imageUrl={modalCard.image_uris.normal || modalCard.image_uris.small || modalCard.image_uris.large || ''}
        />
      )}

      {/* Import Modal */}
      {showImport && currentDeck && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card variant="elevated" className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-[color:var(--theme-text-primary)]">Import Deck List</h2>
                <Button
                  onClick={() => setShowImport(false)}
                  variant="outline"
                  size="sm"
                >
                  Close
                </Button>
              </div>
              <DeckImport
                deckId={currentDeck.id}
                onImportSuccess={() => {
                  refreshDeck(currentDeck.id);
                  setShowImport(false);
                }}
              />
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

