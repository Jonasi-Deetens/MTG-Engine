'use client';

// frontend/app/(protected)/decks/builder/page.tsx

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent } from '@dnd-kit/core';
import { useDeckStore } from '@/store/deckStore';
import { CardData } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { CardPreview } from '@/components/cards/CardPreview';
import { CardModal } from '@/components/ui/CardModal';
import { DeckCardList } from '@/components/decks/DeckCardList';
import { DeckCardResponse, DeckCustomListResponse, decks } from '@/lib/decks';
import { FormatSelector } from '@/components/decks/FormatSelector';
import { DeckValidationPanel } from '@/components/decks/DeckValidationPanel';
import { ManaCurveChart } from '@/components/decks/ManaCurveChart';
import { CardTypeBreakdown } from '@/components/decks/CardTypeBreakdown';
import { DeckImport } from '@/components/decks/DeckImport';
import { UnifiedCardSearch } from '@/components/decks/UnifiedCardSearch';
import { EditableTypeList, getCardType, type CardType, DEFAULT_TYPE_LABELS } from '@/components/decks/EditableTypeList';
import { DroppableList } from '@/components/decks/DroppableList';

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
    createCustomList,
    updateCustomList,
    deleteCustomList,
    moveCardToList,
  } = useDeckStore();

  const [deckName, setDeckName] = useState('');
  const [deckDescription, setDeckDescription] = useState('');
  const [deckFormat, setDeckFormat] = useState('Commander');
  const [isPublic, setIsPublic] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showImport, setShowImport] = useState(false);

  // Type-based lists (editable)
  const [typeLists, setTypeLists] = useState<DeckCustomListResponse[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  // Card preview: only update when hovering a card, don't clear on mouse leave.
  const [previewCard, setPreviewCard] = useState<DeckCardResponse | null>(null);

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

  // Load and initialize type-based lists when deck loads
  useEffect(() => {
    if (currentDeck) {
      initializeTypeLists();
    }
  }, [currentDeck?.id]); // Only re-run when deck ID changes

  // Refresh type lists when deck data changes
  useEffect(() => {
    if (currentDeck) {
      decks.getCustomLists(currentDeck.id)
        .then(setTypeLists)
        .catch(err => {
          console.error('Failed to load type lists:', err);
        });
    }
  }, [currentDeck?.id, currentDeck?.cards.length]); // Refresh when cards change

  const initializeTypeLists = async () => {
    if (!currentDeck) return;
    
    try {
      const lists = await decks.getCustomLists(currentDeck.id);
      const typeOrder: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
      
      // Create lists for each type if they don't exist
      const existingLists = new Set(lists.map(l => l.name.toLowerCase()));
      const newLists: Promise<DeckCustomListResponse>[] = [];
      
      for (let i = 0; i < typeOrder.length; i++) {
        const type = typeOrder[i];
        const defaultName = DEFAULT_TYPE_LABELS[type];
        if (!existingLists.has(defaultName.toLowerCase())) {
          newLists.push(decks.createCustomList(currentDeck.id, { name: defaultName, position: i }));
        }
      }
      
      if (newLists.length > 0) {
        await Promise.all(newLists);
        const updatedLists = await decks.getCustomLists(currentDeck.id);
        setTypeLists(updatedLists);
      } else {
        setTypeLists(lists);
      }
    } catch (err) {
      console.error('Failed to initialize type lists:', err);
      setTypeLists([]);
    }
  };

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
      // Determine card type
      const cardType = getCardType(card.type_line);
      const defaultName = DEFAULT_TYPE_LABELS[cardType];
      
      // Only find list if it matches the EXACT default name (not renamed)
      // If a list has been renamed, it won't be found here
      let typeList = typeLists.find(l => 
        l.name.toLowerCase() === defaultName.toLowerCase()
      );
      
      // If no list found with default name, the column was renamed
      // Add card to "Other" instead
      if (!typeList) {
        const otherDefaultName = DEFAULT_TYPE_LABELS['Other'];
        typeList = typeLists.find(l => 
          l.name.toLowerCase() === otherDefaultName.toLowerCase()
        );
        
        // Create "Other" list if it doesn't exist
        if (!typeList) {
          const newList = await decks.createCustomList(currentDeck.id, { 
            name: otherDefaultName, 
            position: typeLists.length 
          });
          typeList = newList;
          setTypeLists([...typeLists, newList]);
        }
      }
      
      await addCard(currentDeck.id, card.card_id, 1, typeList.id);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to add card');
    }
  };

  const handleAddCommanderFromSearch = async (card: CardData) => {
    if (!currentDeck) {
      alert('Please save the deck first');
      return;
    }
    try {
      await addCommander(currentDeck.id, card.card_id, currentDeck.commanders.length);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to add commander');
    }
  };

  const handleRenameTypeList = async (type: CardType, newName: string, listId?: number) => {
    if (!currentDeck) return;
    const defaultName = DEFAULT_TYPE_LABELS[type];
    
    // Find list for this type - prefer listId if provided, otherwise search by name/type
    let typeList: DeckCustomListResponse | undefined;
    
    if (listId) {
      typeList = typeLists.find(l => l.id === listId);
    }
    
    if (!typeList) {
      // Try to find by checking which list has cards of this type
      const currentCards = currentDeck.cards.filter(c => {
        if (c.list_id) {
          // Check if this card's list has cards of this type
          const cardType = getCardType(c.card.type_line);
          return cardType === type;
        }
        return false;
      });
      
      if (currentCards.length > 0) {
        const listIdFromCards = currentCards[0].list_id;
        if (listIdFromCards) {
          typeList = typeLists.find(l => l.id === listIdFromCards);
        }
      }
    }
    
    if (!typeList) {
      // Fallback: find by name
      typeList = typeLists.find(l => 
        l.name.toLowerCase() === defaultName.toLowerCase() || 
        l.name.toLowerCase() === type.toLowerCase()
      );
    }
    
    if (typeList) {
      try {
        await updateCustomList(currentDeck.id, typeList.id, { name: newName });
        const lists = await decks.getCustomLists(currentDeck.id);
        setTypeLists(lists);
        // Refresh deck to ensure UI updates
        await refreshDeck(currentDeck.id);
      } catch (err: any) {
        alert(err?.data?.detail || 'Failed to rename list');
      }
    } else {
      // Create new list if it doesn't exist
      try {
        const newList = await decks.createCustomList(currentDeck.id, { 
          name: newName, 
          position: typeLists.length 
        });
        setTypeLists([...typeLists, newList]);
        // Refresh deck to ensure UI updates
        await refreshDeck(currentDeck.id);
      } catch (err: any) {
        alert(err?.data?.detail || 'Failed to create list');
      }
    }
  };

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || !currentDeck) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Don't do anything if dropped on the same list
    const cardData = active.data.current as { card: DeckCardResponse } | undefined;
    if (cardData) {
      const currentListId = cardData.card.list_id;
      if (overId.startsWith('list-')) {
        const targetListId = parseInt(overId.replace('list-', ''));
        if (currentListId === targetListId) return;
      } else if (overId.startsWith('type-')) {
        // Check if card is already in a list for this type
        const type = overId.replace('type-', '') as CardType;
        const defaultName = DEFAULT_TYPE_LABELS[type];
        const typeList = typeLists.find(l => 
          l.name.toLowerCase() === defaultName.toLowerCase() || 
          l.name.toLowerCase() === type.toLowerCase()
        );
        if (typeList && currentListId === typeList.id) return;
      }
    }

    // Extract card_id from activeId (format: "card-{card_id}")
    if (activeId.startsWith('card-')) {
      const cardId = activeId.replace('card-', '');
      
      // Extract list_id from overId (format: "list-{list_id}" or "type-{type}")
      if (overId.startsWith('list-')) {
        const listId = parseInt(overId.replace('list-', ''));
        try {
          await moveCardToList(currentDeck.id, cardId, listId);
          // Refresh deck to get updated card positions
          await refreshDeck(currentDeck.id);
        } catch (err: any) {
          alert(err?.data?.detail || 'Failed to move card');
        }
      } else if (overId.startsWith('type-')) {
        // Dropped on a type list - find or create the list
        const type = overId.replace('type-', '') as CardType;
        const defaultName = DEFAULT_TYPE_LABELS[type];
        
        let typeList = typeLists.find(l => 
          l.name.toLowerCase() === defaultName.toLowerCase() || 
          l.name.toLowerCase() === type.toLowerCase()
        );
        
        if (!typeList) {
          // Create list for this type
          try {
            const newList = await decks.createCustomList(currentDeck.id, { 
              name: defaultName, 
              position: typeLists.length 
            });
            typeList = newList;
            setTypeLists([...typeLists, newList]);
          } catch (err: any) {
            alert(err?.data?.detail || 'Failed to create list');
            return;
          }
        }
        
        try {
          await moveCardToList(currentDeck.id, cardId, typeList.id);
          // Refresh deck to get updated card positions
          await refreshDeck(currentDeck.id);
        } catch (err: any) {
          alert(err?.data?.detail || 'Failed to move card');
        }
      } else if (overId === 'commander-list') {
        // Dropped on commander list - add as commander
        if (deckFormat === 'Commander') {
          try {
            await addCommander(currentDeck.id, cardId, currentDeck.commanders.length);
            // Remove from deck cards if it was there
            const deckCard = currentDeck.cards.find(c => c.card_id === cardId);
            if (deckCard) {
              await removeCard(currentDeck.id, cardId);
            }
            await refreshDeck(currentDeck.id);
          } catch (err: any) {
            alert(err?.data?.detail || 'Failed to add commander');
          }
        }
      }
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

  // Handler for hovering a card in lists or commander
  const handleCardHover = (card: DeckCardResponse | null) => {
    if (card) setPreviewCard(card);
    // Do not clear previewCard on mouse leave (card === null)
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


        {/* Deck Cards */}
        {currentDeck && (
          <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <Card variant="elevated">
              <div className="p-3 space-y-3">
                {/* Header with search */}
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
                {(() => {
                  // Group cards by their list_id, then by type for cards without list_id
                  const typeOrder: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
                  const cardsByList = new Map<number | null, DeckCardResponse[]>();
                  const cardsByType = new Map<CardType, DeckCardResponse[]>();
                  
                  // Initialize maps
                  typeOrder.forEach(type => {
                    cardsByType.set(type, []);
                  });
                  
                  // Group cards - prioritize list_id, fallback to type
                  currentDeck.cards.forEach(card => {
                    if (card.list_id !== null && card.list_id !== undefined) {
                      // Card has a list_id - group by list
                      if (!cardsByList.has(card.list_id)) {
                        cardsByList.set(card.list_id, []);
                      }
                      cardsByList.get(card.list_id)!.push(card);
                    } else {
                      // Cards without list_id - group by type
                      const type = getCardType(card.card.type_line);
                      cardsByType.get(type)!.push(card);
                    }
                  });
                  
                  return (
                  <div className="grid grid-cols-3 gap-4">
                    {/* Left Section - 2 Columns */}
                    <div className="grid grid-cols-2 gap-x-4">
                      {/* Left Column 1 - Creatures */}
                      <div className="min-w-0">
                        {(() => {
                          const type: CardType = 'Creature';
                          // Find list - only match if name is exactly the default name (not renamed)
                          let list = typeLists.find(l => 
                            l.name.toLowerCase() === DEFAULT_TYPE_LABELS[type].toLowerCase()
                          );
                          
                          // If no list found by default name, try to find by checking which list has cards of this type
                          // This handles cases where list was renamed but still has cards
                          if (!list) {
                            const listWithCards = Array.from(cardsByList.entries()).find(([listId, cards]) => 
                              cards.some(c => getCardType(c.card.type_line) === type)
                            );
                            if (listWithCards) {
                              list = typeLists.find(l => l.id === listWithCards[0]);
                            }
                          }
                          
                          // Get cards for this list ID, or cards without list_id that match this type
                          const listCards = list ? (cardsByList.get(list.id) || []) : [];
                          const typeCards = cardsByType.get(type) || [];
                          // Show cards with this list_id, or if no list, show cards without list_id of this type
                          const cards = list ? listCards : typeCards;
                          return (
                            <EditableTypeList
                              type={type}
                              list={list || null}
                              cards={cards}
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
                          // Find list - only match if name is exactly the default name (not renamed)
                          let list = typeLists.find(l => 
                            l.name.toLowerCase() === DEFAULT_TYPE_LABELS[type].toLowerCase()
                          );
                          
                          // If no list found by default name, try to find by checking which list has cards of this type
                          // This handles cases where list was renamed but still has cards
                          if (!list) {
                            const listWithCards = Array.from(cardsByList.entries()).find(([listId, cards]) => 
                              cards.some(c => getCardType(c.card.type_line) === type)
                            );
                            if (listWithCards) {
                              list = typeLists.find(l => l.id === listWithCards[0]);
                            }
                          }
                          
                          // Get cards for this list ID, or cards without list_id that match this type
                          const listCards = list ? (cardsByList.get(list.id) || []) : [];
                          const typeCards = cardsByType.get(type) || [];
                          // Show cards with this list_id, or if no list, show cards without list_id of this type
                          const cards = list ? listCards : typeCards;
                          return (
                            <EditableTypeList
                              key={type}
                              type={type}
                              list={list || null}
                              cards={cards}
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

                    {/* Middle Section - Commander above Preview */}
                    <div className="space-y-4">
                      {/* Commander (if exists) */}
                      {deckFormat === 'Commander' && (
                        <DroppableList id="commander-list" className="space-y-2">
                          <div>
                            <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)] mb-2">
                              Commander{currentDeck.commanders.length > 1 ? 's' : ''} ({currentDeck.commanders.length})
                            </div>
                            {currentDeck.commanders.length > 0 ? (
                              <div>
                                {currentDeck.commanders.map((commander) => {
                                  const manaCost = commander.card.mana_cost || '';
                                  return (
                                    <div
                                      key={commander.card.card_id}
                                      className="flex items-center gap-2 px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm cursor-pointer"
                                      onMouseEnter={() => setPreviewCard({ card: commander.card, quantity: 1, card_id: commander.card_id })}
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
                            ) : (
                              <div className="text-center py-4 text-[color:var(--theme-text-secondary)] text-sm">
                                <p>Drop cards here to add as commander</p>
                              </div>
                            )}
                          </div>
                        </DroppableList>
                      )}

                      {/* Card Preview */}
                      <div className="flex items-start justify-center min-h-[300px]">
                        {previewCard ? (
                          <div className="sticky top-4 w-[280px]">
                            {previewCard.card.image_uris?.normal || previewCard.card.image_uris?.small || previewCard.card.image_uris?.large ? (
                              <>
                                <CardPreview card={previewCard.card} disableClick={true} />
                                {previewCard.quantity > 1 && (
                                  <div className="mt-2 text-center text-xs text-[color:var(--theme-text-secondary)]">
                                    Quantity: {previewCard.quantity}x
                                  </div>
                                )}
                              </>
                            ) : (
                              <div className="aspect-[63/88] bg-[color:var(--theme-card-hover)] rounded-xl flex items-center justify-center text-[color:var(--theme-text-secondary)] text-sm p-4 text-center">
                                <div>
                                  <div className="font-medium mb-1">{previewCard.card.name}</div>
                                  {previewCard.card.mana_cost && (
                                    <div className="text-xs font-mono text-[color:var(--theme-accent-primary)]">
                                      {previewCard.card.mana_cost}
                                    </div>
                                  )}
                                  {previewCard.card.type_line && (
                                    <div className="text-xs mt-1">{previewCard.card.type_line}</div>
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
                      <div className="space-y-2 min-w-0">
                        {(['Artifact', 'Enchantment'] as CardType[]).map((type) => {
                          // Find list - only match if name is exactly the default name (not renamed)
                          let list = typeLists.find(l => 
                            l.name.toLowerCase() === DEFAULT_TYPE_LABELS[type].toLowerCase()
                          );
                          
                          // If no list found by default name, try to find by checking which list has cards of this type
                          // This handles cases where list was renamed but still has cards
                          if (!list) {
                            const listWithCards = Array.from(cardsByList.entries()).find(([listId, cards]) => 
                              cards.some(c => getCardType(c.card.type_line) === type)
                            );
                            if (listWithCards) {
                              list = typeLists.find(l => l.id === listWithCards[0]);
                            }
                          }
                          
                          // Get cards for this list ID, or cards without list_id that match this type
                          const listCards = list ? (cardsByList.get(list.id) || []) : [];
                          const typeCards = cardsByType.get(type) || [];
                          // Show cards with this list_id, or if no list, show cards without list_id of this type
                          const cards = list ? listCards : typeCards;
                          return (
                            <EditableTypeList
                              key={type}
                              type={type}
                              list={list || null}
                              cards={cards}
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
                          // Find list - only match if name is exactly the default name (not renamed)
                          let list = typeLists.find(l => 
                            l.name.toLowerCase() === DEFAULT_TYPE_LABELS[type].toLowerCase()
                          );
                          
                          // If no list found by default name, try to find by checking which list has cards of this type
                          // This handles cases where list was renamed but still has cards
                          if (!list) {
                            const listWithCards = Array.from(cardsByList.entries()).find(([listId, cards]) => 
                              cards.some(c => getCardType(c.card.type_line) === type)
                            );
                            if (listWithCards) {
                              list = typeLists.find(l => l.id === listWithCards[0]);
                            }
                          }
                          
                          // Get cards for this list ID, or cards without list_id that match this type
                          const listCards = list ? (cardsByList.get(list.id) || []) : [];
                          const typeCards = cardsByType.get(type) || [];
                          // Show cards with this list_id, or if no list, show cards without list_id of this type
                          const cards = list ? listCards : typeCards;
                          return (
                            <EditableTypeList
                              key={type}
                              type={type}
                              list={list || null}
                              cards={cards}
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
                  );
                })()}
              </div>
            </Card>
            <DragOverlay>
              {activeId && activeId.startsWith('card-') && (() => {
                const cardId = activeId.replace('card-', '');
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

