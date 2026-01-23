// frontend/hooks/decks/useDragAndDrop.ts

import { useState } from 'react';
import { DragStartEvent, DragEndEvent } from '@dnd-kit/core';
import { DeckDetailResponse, DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardType, DEFAULT_TYPE_LABELS } from '@/lib/utils/cardTypes';
import { extractCardId, extractListId, extractType, isCommanderList } from '@/utils/dragAndDrop';
import { decks } from '@/lib/decks';

interface UseDragAndDropOptions {
  currentDeck: DeckDetailResponse | null;
  typeLists: DeckCustomListResponse[];
  deckFormat: string;
  onCardMove: (deckId: number, cardId: string, listId: number | null) => Promise<void>;
  onCommanderAdd: (deckId: number, cardId: string, position: number) => Promise<void>;
  onCommanderRemove: (deckId: number, cardId: string) => Promise<void>;
  onCardRemove: (deckId: number, cardId: string) => Promise<void>;
  onRefresh: (deckId: number) => Promise<void>;
  onTypeListsUpdate: (lists: DeckCustomListResponse[]) => void;
}

export function useDragAndDrop({
  currentDeck,
  typeLists,
  deckFormat,
  onCardMove,
  onCommanderAdd,
  onCommanderRemove,
  onCardRemove,
  onRefresh,
  onTypeListsUpdate,
}: UseDragAndDropOptions) {
  const [activeId, setActiveId] = useState<string | null>(null);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over || !currentDeck) return;

    const activeId = active.id as string;
    const overId = over.id as string;

    // Extract card ID
    const cardId = extractCardId(activeId);
    if (!cardId) return;

    // Get card data to check current list
    const cardData = active.data.current as { card: DeckCardResponse; isCommander?: boolean } | undefined;
    const currentListId = cardData?.card.list_id ?? null;
    const isCommanderDrag = cardData?.isCommander === true;

    // Check if dropped on the same list
    const listId = extractListId(overId);
    if (listId !== null && currentListId === listId) return;

    // Handle different drop targets
    if (isCommanderList(overId)) {
      // Dropped on commander list
      if (deckFormat === 'Commander' && !isCommanderDrag) {
        try {
          await onCommanderAdd(currentDeck.id, cardId, currentDeck.commanders.length);
          // Remove from deck cards if it was there
          const deckCard = currentDeck.cards.find(c => c.card_id === cardId);
          if (deckCard) {
            await onCardRemove(currentDeck.id, cardId);
          }
          await onRefresh(currentDeck.id);
        } catch (err: any) {
          alert(err?.data?.detail || 'Failed to add commander');
        }
      }
    } else if (listId !== null) {
      // Dropped on a specific list
      try {
        if (isCommanderDrag) {
          const existingCard = currentDeck.cards.find(c => c.card_id === cardId);
          if (existingCard) {
            await onCardMove(currentDeck.id, cardId, listId);
          } else {
            await decks.addCard(currentDeck.id, { card_id: cardId, list_id: listId });
          }
          await onCommanderRemove(currentDeck.id, cardId);
        } else {
          await onCardMove(currentDeck.id, cardId, listId);
        }
        await onRefresh(currentDeck.id);
      } catch (err: any) {
        alert(err?.data?.detail || 'Failed to move card');
      }
    } else {
      // Dropped on a type list - find or create the list
      const typeStr = extractType(overId);
      if (typeStr) {
        const type = typeStr as CardType;
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
            onTypeListsUpdate([...typeLists, newList]);
          } catch (err: any) {
            alert(err?.data?.detail || 'Failed to create list');
            return;
          }
        }
        
        // Check if already in this list
        if (currentListId === typeList.id) return;
        
        try {
          if (isCommanderDrag) {
            const existingCard = currentDeck.cards.find(c => c.card_id === cardId);
            if (existingCard) {
              await onCardMove(currentDeck.id, cardId, typeList.id);
            } else {
              await decks.addCard(currentDeck.id, { card_id: cardId, list_id: typeList.id });
            }
            await onCommanderRemove(currentDeck.id, cardId);
          } else {
            await onCardMove(currentDeck.id, cardId, typeList.id);
          }
          await onRefresh(currentDeck.id);
        } catch (err: any) {
          alert(err?.data?.detail || 'Failed to move card');
        }
      }
    }
  };

  return {
    activeId,
    handleDragStart,
    handleDragEnd,
  };
}

