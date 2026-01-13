// frontend/hooks/decks/useDeckCardHandlers.ts

import { CardData } from '@/components/cards/CardPreview';
import { DeckDetailResponse, DeckCustomListResponse, decks } from '@/lib/decks';
import { getCardType, DEFAULT_TYPE_LABELS, CardType } from '@/lib/utils/cardTypes';
import { findListForType } from '@/utils/deckBuilder/cardGrouping';
import { useDeckStore } from '@/store/deckStore';

interface UseDeckCardHandlersOptions {
  currentDeck: DeckDetailResponse | null;
  typeLists: DeckCustomListResponse[];
  setTypeLists: (lists: DeckCustomListResponse[]) => void;
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
      // Determine card type
      const cardType = getCardType(card.type_line);
      const defaultName = DEFAULT_TYPE_LABELS[cardType];
      
      // Find list for this type using position-based matching
      let typeList = findListForType(cardType, typeLists, currentDeck.cards);
      
      // Check if the list name matches the default type name
      // If renamed, add to "Others" instead
      if (typeList && typeList.name.toLowerCase() !== defaultName.toLowerCase()) {
        // List was renamed, use "Others" instead
        typeList = findListForType('Other', typeLists, currentDeck.cards);
      }
      
      // If no list found, use "Other" list
      if (!typeList) {
        typeList = findListForType('Other', typeLists, currentDeck.cards);
        
        // If "Other" list doesn't exist, create it
        if (!typeList) {
          const otherDefaultName = DEFAULT_TYPE_LABELS['Other'];
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
        // Update the list name - only edit existing lists
        await updateCustomList(currentDeck.id, typeList.id, { name: newName });
        // Refresh lists to get updated name
        const updatedLists = await decks.getCustomLists(currentDeck.id);
        setTypeLists(updatedLists);
        // Refresh deck to ensure everything is in sync
        await refreshDeck(currentDeck.id);
      } catch (err: any) {
        console.error('Failed to rename list:', err);
        alert(err?.data?.detail || 'Failed to rename list');
        // Refresh lists even on error to ensure state is consistent
        try {
          const lists = await decks.getCustomLists(currentDeck.id);
          setTypeLists(lists);
        } catch (refreshErr) {
          console.error('Failed to refresh lists after rename error:', refreshErr);
        }
      }
    } else {
      // If list not found, try to find it by listId if provided (should always be provided)
      if (listId) {
        const listById = typeLists.find(l => l.id === listId);
        if (listById) {
          try {
            await updateCustomList(currentDeck.id, listById.id, { name: newName });
            const updatedLists = await decks.getCustomLists(currentDeck.id);
            setTypeLists(updatedLists);
            await refreshDeck(currentDeck.id);
          } catch (err: any) {
            console.error('Failed to rename list:', err);
            alert(err?.data?.detail || 'Failed to rename list');
          }
        } else {
          console.warn(`List with ID ${listId} not found in typeLists`);
        }
      } else {
        console.warn('Cannot rename list: no listId provided and list not found');
      }
    }
  };

  return {
    handleAddCard,
    handleAddCommanderFromSearch,
    handleRenameTypeList,
  };
}

