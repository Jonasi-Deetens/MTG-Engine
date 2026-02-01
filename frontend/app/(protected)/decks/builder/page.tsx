'use client';

// frontend/app/(protected)/decks/builder/page.tsx

import { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { DndContext, DragOverlay } from '@dnd-kit/core';
import { useDeckBuilder } from '@/features/decks/hooks/useDeckBuilder';
import { useTypeLists } from '@/features/decks/hooks/useTypeLists';
import { useDeckCardHandlers } from '@/features/decks/hooks/useDeckCardHandlers';
import { useDragAndDrop } from '@/features/decks/hooks/useDragAndDrop';
import { useDeckStore } from '@/store/deckStore';
import { Card } from '@/components/ui/Card';
import { CardModal } from '@/components/ui/CardModal';
import { Button } from '@/components/ui/Button';
import { ArchiveSectionHeader } from '@/components/ui/ArchiveSectionHeader';
import { DeckBuilderHeader } from '@/features/decks/components/builder/DeckBuilderHeader';
import { DeckInfoForm } from '@/features/decks/components/builder/DeckInfoForm';
import { DeckBuilderGrid } from '@/features/decks/components/builder/DeckBuilderGrid';
import { CommanderSection } from '@/features/decks/components/builder/CommanderSection';
import { CardPreviewSection } from '@/features/decks/components/builder/CardPreviewSection';
import { UnifiedCardSearch } from '@/features/decks/components/UnifiedCardSearch';
import { DeckValidationPanel } from '@/features/decks/components/DeckValidationPanel';
import { ManaCurveChart } from '@/features/decks/components/ManaCurveChart';
import { CardTypeBreakdown } from '@/features/decks/components/CardTypeBreakdown';
import { DeckImport } from '@/features/decks/components/DeckImport';
import { extractCardId } from '@/utils/dragAndDrop';
import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardData } from '@/components/cards/CardPreview';
import { isEditableTarget } from '@/context/ShortcutContext';

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

  const { typeLists, setTypeLists } = useTypeLists(currentDeck?.id ?? null);

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
    onCommanderRemove: async (_deckId: number, cardId: string) => {
      await handleRemoveCommander(cardId);
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

  const [focusedDeckCard, setFocusedDeckCard] = useState<DeckCardResponse | null>(null);
  const [focusedSearchCard, setFocusedSearchCard] = useState<CardData | null>(null);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.isComposing) return;
      if (isEditableTarget(e.target)) return;
      if (!currentDeck || isModalOpen) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      const key = e.key.toLowerCase();
      if (key === 'a') {
        const card = focusedSearchCard ?? focusedDeckCard?.card;
        if (!card) return;
        e.preventDefault();
        e.stopPropagation();
        handleAddCard(card);
        return;
      }

      if (key === 'x') {
        if (!focusedDeckCard) return;
        const latestCard = currentDeck.cards.find((card) => card.card_id === focusedDeckCard.card_id);
        const currentQty = latestCard?.quantity ?? focusedDeckCard.quantity;
        e.preventDefault();
        e.stopPropagation();
        if (e.shiftKey) {
          handleRemoveCard(focusedDeckCard.card_id);
        } else {
          handleQuantityChange(focusedDeckCard.card_id, currentQty - 1);
        }
        return;
      }

      if (key === '+' || key === '=') {
        if (!focusedDeckCard) return;
        const latestCard = currentDeck.cards.find((card) => card.card_id === focusedDeckCard.card_id);
        const currentQty = latestCard?.quantity ?? focusedDeckCard.quantity;
        e.preventDefault();
        e.stopPropagation();
        handleQuantityChange(focusedDeckCard.card_id, currentQty + 1);
        return;
      }

      if (key === '-' || key === '_') {
        if (!focusedDeckCard) return;
        const latestCard = currentDeck.cards.find((card) => card.card_id === focusedDeckCard.card_id);
        const currentQty = latestCard?.quantity ?? focusedDeckCard.quantity;
        e.preventDefault();
        e.stopPropagation();
        handleQuantityChange(focusedDeckCard.card_id, currentQty - 1);
      }
    };

    window.addEventListener('keydown', onKeyDown, { passive: false });
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [
    currentDeck,
    focusedDeckCard,
    focusedSearchCard,
    handleAddCard,
    handleQuantityChange,
    handleRemoveCard,
    isModalOpen,
  ]);

  const handleDeckCardHover = (card: DeckCardResponse | null) => {
    handleCardHover(card);
    setFocusedDeckCard(card);
  };

  const importModal =
    showImport && currentDeck && typeof document !== 'undefined'
      ? createPortal(
          <div
            className="fixed inset-0 z-[9999] flex items-center justify-center bg-[color:var(--theme-overlay-strong)]/70 backdrop-blur-sm p-4 sm:p-8"
            onClick={() => setShowImport(false)}
            role="dialog"
            aria-modal="true"
            aria-label="Import deck list"
          >
            <div
              className="ui-card relative w-full max-w-2xl max-h-[90vh] overflow-hidden"
              data-variant="default"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="w-full max-h-[90vh] overflow-y-auto p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[color:var(--theme-border-default)] pb-2 lg:pb-3 mb-4">
                <div className="text-xs font-mono tracking-[0.3em] text-[color:var(--theme-text-secondary)]">
                  IMPORT_DECK
                </div>
                <div className="flex w-full justify-end sm:w-auto">
                  <Button
                    onClick={() => setShowImport(false)}
                    variant="frame"
                    size="xs"
                    aria-label="Close import modal"
                    className="w-8 p-0"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </Button>
                </div>
              </div>
              <h2
                className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)] mb-3 nier-glitch"
                data-text="Import Deck List"
              >
                Import Deck List
              </h2>
                <DeckImport
                  deckId={currentDeck.id}
                  onImportSuccess={() => {
                    refreshDeck(currentDeck.id);
                    setShowImport(false);
                  }}
                />
              </div>
            </div>
          </div>,
          document.body
        )
      : null;

  return (
    <div className="space-y-6">
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

      <div className="space-y-6">
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
              <div className="p-4 space-y-4">
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
                    Deck ({currentDeck.card_count} cards)
                  </h3>
                  <UnifiedCardSearch
                    onAddCard={handleAddCard}
                    onAddCommander={deckFormat === 'Commander' ? handleAddCommanderFromSearch : undefined}
                    onCardHover={setFocusedSearchCard}
                    isCommanderFormat={deckFormat === 'Commander'}
                    currentCommanderCount={currentDeck.commanders.length}
                  />
                </div>

                <DeckBuilderGrid
                  cards={currentDeck.cards}
                  typeLists={typeLists}
                  deckFormat={deckFormat || 'Commander'}
                  onQuantityChange={handleQuantityChange}
                  onRemove={handleRemoveCard}
                  onCardHover={handleDeckCardHover}
                  onCardClick={(card) => {
                    setModalCard(card);
                    setIsModalOpen(true);
                  }}
                  onRename={handleRenameTypeList}
                  middleContent={
                    <>
                      {deckFormat === 'Commander' && (
                        <CommanderSection
                          commanders={currentDeck.commanders}
                          onCommanderHover={handleDeckCardHover}
                          onCommanderClick={(card) => {
                            setModalCard(card);
                            setIsModalOpen(true);
                          }}
                          onRemoveCommander={handleRemoveCommander}
                        />
                      )}
                      <CardPreviewSection previewCard={previewCard} />
                    </>
                  }
                />
              </div>
            </Card>

            <DragOverlay>
              {activeId && extractCardId(activeId) && (() => {
                const cardId = extractCardId(activeId)!;
                const draggedDeckCard = currentDeck.cards.find(c => c.card_id === cardId);
                const draggedCommander = currentDeck.commanders.find(c => c.card_id === cardId);
                const card = draggedDeckCard?.card ?? draggedCommander?.card;
                if (!card) return null;
                
                const manaCost = card.mana_cost || '';
                return (
                  <div className="flex items-center gap-2 px-2 py-1 bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg shadow-xl min-w-[180px]">
                    <span className="flex-shrink-0 w-4 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                      {draggedDeckCard?.quantity ?? 1}x
                    </span>
                    <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] text-xs truncate">
                      {card.name}
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
            <div className="p-4 space-y-4">
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
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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

      {importModal}
    </div>
  );
}
