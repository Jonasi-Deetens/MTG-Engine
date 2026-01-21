// frontend/hooks/decks/useTypeLists.ts

import { useState, useEffect, useCallback, useRef } from 'react';
import { DeckCustomListResponse } from '@/lib/decks';
import { decks } from '@/lib/decks';
import { CardType, DEFAULT_TYPE_LABELS } from '@/lib/utils/cardTypes';

export function useTypeLists(deckId: number | null, cardCount: number) {
  const [typeLists, setTypeLists] = useState<DeckCustomListResponse[]>([]);
  const initializedRef = useRef<Set<number>>(new Set());

  // Load type lists when deck loads
  useEffect(() => {
    if (deckId) {
      // Reset initialization flag when deck changes
      initializedRef.current.delete(deckId);
      decks.getCustomLists(deckId)
        .then(setTypeLists)
        .catch(err => {
          console.error('Failed to load type lists:', err);
        });
    } else {
      setTypeLists([]);
    }
  }, [deckId, cardCount]); // Refresh when cards change

  const initializeTypeLists = useCallback(async () => {
    if (!deckId) return;
    
    // Prevent multiple simultaneous initializations for the same deck
    if (initializedRef.current.has(deckId)) {
      return;
    }
    
    initializedRef.current.add(deckId);
    
    try {
      const lists = await decks.getCustomLists(deckId);
      
      // Only create default lists if there are NO lists at all (truly new deck)
      // If lists exist (even if renamed), don't create defaults
      if (lists.length === 0) {
        const typeOrder: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
        
        // Create lists sequentially to avoid timeout
        for (let i = 0; i < typeOrder.length; i++) {
          const type = typeOrder[i];
          const defaultName = DEFAULT_TYPE_LABELS[type];
          try {
            await decks.createCustomList(deckId, { name: defaultName, position: i });
          } catch (err) {
            console.error(`Failed to create list for ${type}:`, err);
            // Continue with other lists even if one fails
          }
        }
        
        // Refresh lists after creating defaults
        const updatedLists = await decks.getCustomLists(deckId);
        setTypeLists(updatedLists);
      } else {
        // Lists already exist, just set them (they may be renamed)
        setTypeLists(lists);
      }
    } catch (err) {
      console.error('Failed to initialize type lists:', err);
      // Don't clear lists on error - keep existing ones
    } finally {
      // Allow re-initialization if deck changes
      initializedRef.current.delete(deckId);
    }
  }, [deckId]);

  return {
    typeLists,
    setTypeLists,
    initializeTypeLists,
  };
}

