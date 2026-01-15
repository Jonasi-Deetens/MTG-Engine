'use client';

// frontend/app/(protected)/decks/builder/page.tsx

import { useEffect } from 'react';
import { DndContext, DragOverlay } from '@dnd-kit/core';
import { useDeckBuilder } from '@/hooks/decks/useDeckBuilder';
import { useTypeLists } from '@/hooks/decks/useTypeLists';
import { useDeckCardHandlers } from '@/hooks/decks/useDeckCardHandlers';
import { useDragAndDrop } from '@/hooks/decks/useDragAndDrop';
import { useDeckStore } from '@/store/deckStore';
import { Card } from '@/components/ui/Card';
import { CardModal } from '@/components/ui/CardModal';
import { Button } from '@/components/ui/Button';
import { DeckBuilderHeader } from '@/components/decks/builder/DeckBuilderHeader';
import { DeckInfoForm } from '@/components/decks/builder/DeckInfoForm';
import { CommanderSection } from '@/components/decks/builder/CommanderSection';
import { CardPreviewSection } from '@/components/decks/builder/CardPreviewSection';
import { UnifiedCardSearch } from '@/components/decks/UnifiedCardSearch';
import { DeckValidationPanel } from '@/components/decks/DeckValidationPanel';
import { ManaCurveChart } from '@/components/decks/ManaCurveChart';
import { CardTypeBreakdown } from '@/components/decks/CardTypeBreakdown';
import { DeckImport } from '@/components/decks/DeckImport';
import { EditableTypeList } from '@/components/decks/EditableTypeList';
import { extractCardId } from '@/utils/dragAndDrop';
import { DeckCustomListResponse } from '@/lib/decks';
import { CardType } from '@/lib/utils/cardTypes';
import { findListForType, getCardsForType } from '@/utils/deckBuilder/cardGrouping';

export default function DeckBuilderPage() {
  const {
    currentDeck,
    validation,
    loading,
    error,
    deckName,
    deckDescription,
    deckFormat,
    isPublic,
    saving,
    showImport,
    previewCard,
    modalCard,
    isModalOpen,
    setDeckName,
    setDeckDescription,
    setDeckFormat,
    setIsPublic,
    setShowImport,
    setModalCard,
    setIsModalOpen,
    handleSave,
    handleQuantityChange,
    handleRemoveCard,
    handleRemoveCommander,
    handleCardHover,
    addCommander,
    refreshDeck,
    router,
  } = useDeckBuilder();

  const { typeLists, setTypeLists, initializeTypeLists } = useTypeLists(
    currentDeck?.id ?? null,
    currentDeck?.cards.length ?? 0
  );

  const { handleAddCard, handleAddCommanderFromSearch, handleRenameTypeList } = useDeckCardHandlers({
    currentDeck,
    typeLists,
    setTypeLists,
  });

  const { moveCardToList, removeCard: removeCardFromStore } = useDeckStore();

  const { activeId, handleDragStart, handleDragEnd } = useDragAndDrop({
    currentDeck,
    typeLists,
    deckFormat: deckFormat || 'Commander',
    onCardMove: async (deckId: number, cardId: string, listId: number | null) => {
      await moveCardToList(deckId, cardId, listId);
    },
    onCommanderAdd: async (deckId: number, cardId: string, position: number) => {
      await addCommander(deckId, cardId, position);
    },
    onCardRemove: async (deckId: number, cardId: string) => {
      await removeCardFromStore(deckId, cardId);
    },
    onRefresh: async (deckId: number) => {
      await refreshDeck(deckId);
    },
    onTypeListsUpdate: (lists: DeckCustomListResponse[]) => {
      setTypeLists(lists);
    },
  });

  // Initialize type lists when deck loads (only for new decks with no lists)
  useEffect(() => {
    if (currentDeck && typeLists.length === 0) {
      initializeTypeLists();
    }
  }, [currentDeck?.id, typeLists.length, initializeTypeLists]);

  return (
    <div className="w-full space-y-3">
      <DeckBuilderHeader
        deckName={currentDeck?.name ?? null}
        onImportClick={() => setShowImport(true)}
        deckId={currentDeck?.id}
      />

      {error && (
        <div className="p-3 bg-[color:var(--theme-status-error)]/20 border border-[color:var(--theme-status-error)]/50 rounded text-[color:var(--theme-status-error)] text-sm">
          {error}
        </div>
      )}

      <div className="space-y-3">
        <DeckInfoForm
          deckName={deckName}
          deckDescription={deckDescription}
          deckFormat={deckFormat}
          isPublic={isPublic}
          saving={saving}
          loading={loading}
          hasDeck={!!currentDeck}
          onNameChange={setDeckName}
          onDescriptionChange={setDeckDescription}
          onFormatChange={setDeckFormat}
          onPublicChange={setIsPublic}
          onSave={handleSave}
        />

        {currentDeck && (
          <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <Card variant="elevated">
              <div className="p-3 space-y-3">
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
                    Deck ({currentDeck.card_count} cards)
                  </h3>
                  <UnifiedCardSearch
                    onAddCard={handleAddCard}
                    onAddCommander={deckFormat === 'Commander' ? handleAddCommanderFromSearch : undefined}
                    isCommanderFormat={deckFormat === 'Commander'}
                    currentCommanderCount={currentDeck.commanders.length}
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  {/* Left Section - 2 Columns */}
                  <div className="grid grid-cols-2 gap-x-4 min-w-0">
                    {/* Left Column 1 - Creatures */}
                    <div className="min-w-0">
                      {(() => {
                        const type: CardType = 'Creature';
                        const list = findListForType(type, typeLists, currentDeck.cards);
                        const typeCards = getCardsForType(type, currentDeck.cards, typeLists);
                        return (
                          <EditableTypeList
                            type={type}
                            list={list || null}
                            cards={typeCards}
                            onQuantityChange={handleQuantityChange}
                            onRemove={handleRemoveCard}
                            onCardHover={handleCardHover}
                            onCardClick={(deckCard) => {
                              setModalCard(deckCard.card);
                              setIsModalOpen(true);
                            }}
                            onRename={handleRenameTypeList}
                            showControls={true}
                          />
                        );
                      })()}
                    </div>

                    {/* Left Column 2 - Instants & Sorceries */}
                    <div className="space-y-2 min-w-0">
                      {(['Instant', 'Sorcery'] as CardType[]).map((type) => {
                        const list = findListForType(type, typeLists, currentDeck.cards);
                        const typeCards = getCardsForType(type, currentDeck.cards, typeLists);
                        return (
                          <EditableTypeList
                            key={type}
                            type={type}
                            list={list || null}
                            cards={typeCards}
                            onQuantityChange={handleQuantityChange}
                            onRemove={handleRemoveCard}
                            onCardHover={handleCardHover}
                            onCardClick={(deckCard) => {
                              setModalCard(deckCard.card);
                              setIsModalOpen(true);
                            }}
                            onRename={handleRenameTypeList}
                            showControls={true}
                          />
                        );
                      })}
                    </div>
                  </div>

                  {/* Middle Section - Commander and Preview */}
                  <div className="space-y-4">
                    {deckFormat === 'Commander' && (
                      <CommanderSection
                        commanders={currentDeck.commanders}
                        onCommanderHover={handleCardHover}
                        onCommanderClick={(card) => {
                          setModalCard(card);
                          setIsModalOpen(true);
                        }}
                        onRemoveCommander={handleRemoveCommander}
                      />
                    )}
                    <CardPreviewSection previewCard={previewCard} />
                  </div>

                  {/* Right Section - 2 Columns */}
                  <div className="grid grid-cols-2 gap-x-4 min-w-0">
                    {/* Right Column 1 - Artifacts & Enchantments */}
                    <div className="space-y-2 min-w-0">
                      {(['Artifact', 'Enchantment'] as CardType[]).map((type) => {
                        const list = findListForType(type, typeLists, currentDeck.cards);
                        const typeCards = getCardsForType(type, currentDeck.cards, typeLists);
                        return (
                          <EditableTypeList
                            key={type}
                            type={type}
                            list={list || null}
                            cards={typeCards}
                            onQuantityChange={handleQuantityChange}
                            onRemove={handleRemoveCard}
                            onCardHover={handleCardHover}
                            onCardClick={(deckCard) => {
                              setModalCard(deckCard.card);
                              setIsModalOpen(true);
                            }}
                            onRename={handleRenameTypeList}
                            showControls={true}
                          />
                        );
                      })}
                    </div>

                    {/* Right Column 2 - Lands, Planeswalkers & Other */}
                    <div className="space-y-2 min-w-0">
                      {(['Land', 'Planeswalker', 'Other'] as CardType[]).map((type) => {
                        const list = findListForType(type, typeLists, currentDeck.cards);
                        const typeCards = getCardsForType(type, currentDeck.cards, typeLists);
                        return (
                          <EditableTypeList
                            key={type}
                            type={type}
                            list={list || null}
                            cards={typeCards}
                            onQuantityChange={handleQuantityChange}
                            onRemove={handleRemoveCard}
                            onCardHover={handleCardHover}
                            onCardClick={(deckCard) => {
                              setModalCard(deckCard.card);
                              setIsModalOpen(true);
                            }}
                            onRename={handleRenameTypeList}
                            showControls={true}
                          />
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <DragOverlay>
              {activeId && extractCardId(activeId) && (() => {
                const cardId = extractCardId(activeId)!;
                const draggedCard = currentDeck.cards.find(c => c.card_id === cardId);
                if (!draggedCard) return null;
                
                const manaCost = draggedCard.card.mana_cost || '';
                return (
                  <div className="flex items-center gap-2 px-2 py-1 bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg shadow-xl min-w-[180px]">
                    <span className="flex-shrink-0 w-4 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                      {draggedCard.quantity}x
                    </span>
                    <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] text-xs truncate">
                      {draggedCard.card.name}
                    </span>
                    {manaCost && (
                      <span className="flex-shrink-0 text-[color:var(--theme-accent-primary)] font-mono text-xs">
                        {manaCost}
                      </span>
                    )}
                  </div>
                );
              })()}
            </DragOverlay>
          </DndContext>
        )}

        {/* Analytics Section */}
        {currentDeck && (
          <Card variant="elevated">
            <div className="p-3 space-y-3">
              <h3 className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Analytics</h3>
              
              <div>
                <h4 className="text-xs font-semibold text-[color:var(--theme-text-primary)] mb-2">Validation</h4>
                <DeckValidationPanel validation={validation} />
              </div>

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
        <div className="fixed inset-0 bg-[color:var(--theme-overlay)] z-50 flex items-center justify-center p-4">
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
