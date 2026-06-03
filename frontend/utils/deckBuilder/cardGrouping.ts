// frontend/utils/deckBuilder/cardGrouping.ts

import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardType, DEFAULT_TYPE_LABELS, TYPE_ORDER } from '@/lib/utils/cardTypes';

/**
 * Find a list by matching the default type label name (case-insensitive)
 */
export function findListForType(
  type: CardType,
  lists: DeckCustomListResponse[]
): DeckCustomListResponse | null {
  const defaultName = DEFAULT_TYPE_LABELS[type];
  return lists.find(l => l.name.toLowerCase() === defaultName.toLowerCase()) || null;
}

/**
 * Get cards for a specific list by list ID
 */
export function getCardsForList(
  listId: number,
  cards: DeckCardResponse[]
): DeckCardResponse[] {
  return cards.filter(c => c.list_id === listId);
}

/**
 * Get cards for a specific type by finding the matching list and returning its cards
 */
export function getCardsForType(
  type: CardType,
  cards: DeckCardResponse[],
  lists: DeckCustomListResponse[]
): DeckCardResponse[] {
  const list = findListForType(type, lists);
  
  if (list) {
    return getCardsForList(list.id, cards);
  }
  
  // Fallback: return empty array if no matching list found
  return [];
}

/**
 * Group all cards by their list_id
 */
export function groupCardsByList(cards: DeckCardResponse[]): Map<number | null, DeckCardResponse[]> {
  const grouped = new Map<number | null, DeckCardResponse[]>();
  
  cards.forEach(card => {
    const listId = card.list_id ?? null;
    if (!grouped.has(listId)) {
      grouped.set(listId, []);
    }
    grouped.get(listId)!.push(card);
  });
  
  return grouped;
}
