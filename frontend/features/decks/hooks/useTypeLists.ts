// frontend/features/decks/hooks/useTypeLists.ts

import { useState, useEffect } from 'react';
import { DeckCustomListResponse, decks } from '@/lib/decks';

/**
 * Hook for loading deck custom lists.
 * Lists are created by the backend when a deck is created,
 * so this hook only needs to load them.
 */
export function useTypeLists(deckId: number | null) {
  const [typeLists, setTypeLists] = useState<DeckCustomListResponse[]>([]);

  useEffect(() => {
    if (deckId) {
      decks.getCustomLists(deckId)
        .then(setTypeLists)
        .catch(err => {
          console.error('Failed to load type lists:', err);
        });
    } else {
      setTypeLists([]);
    }
  }, [deckId]);

  return { typeLists, setTypeLists };
}
