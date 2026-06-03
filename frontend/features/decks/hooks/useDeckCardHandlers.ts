// frontend/features/decks/hooks/useDeckCardHandlers.ts

import { CardData } from '@/components/cards/CardPreview';
import { DeckDetailResponse, DeckCustomListResponse, decks } from '@/lib/decks';
import { getCardType, DEFAULT_TYPE_LABELS, CardType } from '@/lib/utils/cardTypes';
import { useDeckStore } from '@/store/deckStore';

interface UseDeckCardHandlersOptions {
  currentDeck: DeckDetailResponse | null;
  typeLists: DeckCustomListResponse[];
  setTypeLists: (lists: DeckCustomListResponse[]) => void;
}

/**
 * Find a list by matching the default type label name (case-insensitive)
 */
function findListByTypeName(
  type: CardType,
  lists: DeckCustomListResponse[]
): DeckCustomListResponse | null {
  const defaultName = DEFAULT_TYPE_LABELS[type];
  return lists.find(l => l.name.toLowerCase() === defaultName.toLowerCase()) || null;
}

export function useDeckCardHandlers({
  currentDeck,
  typeLists,
  setTypeLists,
}: UseDeckCardHandlersOptions) {
  const { addCard, addCommander, refreshDeck, updateCustomList } = useDeckStore();

  const handleAddCard = async (card: CardData) => {
    if (!currentDeck) {
      alert('Please save the deck first');
      return;
    }
    
    try {
      // Determine card type and find matching list by name
      const cardType = getCardType(card.type_line);
      const typeList = findListByTypeName(cardType, typeLists);
      
      // Add to matching list (or null if not found - unlikely since backend creates lists)
      await addCard(currentDeck.id, card.card_id, 1, typeList?.id ?? null);
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
    if (!currentDeck || !listId) {
      console.warn('Cannot rename list: no deck or listId');
      return;
    }
    
    const typeList = typeLists.find(l => l.id === listId);
    if (!typeList) {
      console.warn(`List with ID ${listId} not found`);
      return;
    }
    
    try {
      await updateCustomList(currentDeck.id, listId, { name: newName });
      // Refresh lists to get updated name
      const updatedLists = await decks.getCustomLists(currentDeck.id);
      setTypeLists(updatedLists);
      await refreshDeck(currentDeck.id);
    } catch (err: any) {
      console.error('Failed to rename list:', err);
      alert(err?.data?.detail || 'Failed to rename list');
      // Refresh lists on error to ensure consistent state
      try {
        const lists = await decks.getCustomLists(currentDeck.id);
        setTypeLists(lists);
      } catch (refreshErr) {
        console.error('Failed to refresh lists:', refreshErr);
      }
    }
  };

  return {
    handleAddCard,
    handleAddCommanderFromSearch,
    handleRenameTypeList,
  };
}
