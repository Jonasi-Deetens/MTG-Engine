// frontend/utils/deckBuilder/cardGrouping.ts

import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardType, getCardType, DEFAULT_TYPE_LABELS } from '@/lib/utils/cardTypes';

/**
 * Group cards by their type (Creature, Instant, etc.)
 * Only includes cards without a list_id (cards in default type groups)
 */
export function groupCardsByType(cards: DeckCardResponse[]): Map<CardType, DeckCardResponse[]> {
  const grouped = new Map<CardType, DeckCardResponse[]>();
  
  // Initialize all types
  const types: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
  types.forEach(type => grouped.set(type, []));
  
  // Group cards without list_id by type
  cards.forEach(card => {
    if (!card.list_id) {
      const type = getCardType(card.card.type_line);
      grouped.get(type)!.push(card);
    }
  });
  
  return grouped;
}

/**
 * Group cards by their list_id
 * Includes cards with list_id (assigned to custom lists)
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

/**
 * Find the list that corresponds to a specific card type
 * Simple strategy: Use position-based matching if we have exactly 8 lists
 * This ensures each list maintains its type association even after renaming
 */
export function findListForType(
  type: CardType,
  lists: DeckCustomListResponse[],
  cards: DeckCardResponse[],
  defaultLabels: Record<CardType, string> = DEFAULT_TYPE_LABELS
): DeckCustomListResponse | null {
  const typeOrder: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
  const typeIndex = typeOrder.indexOf(type);
  
  // If we have exactly 8 lists (one per type), use position-based matching
  // This is the simplest and most reliable way - each list keeps its type by position
  if (lists.length === 8 && typeIndex >= 0) {
    // Sort lists by position, then match by index
    const sortedLists = [...lists].sort((a, b) => (a.position ?? 0) - (b.position ?? 0));
    if (sortedLists[typeIndex]) {
      return sortedLists[typeIndex];
    }
  }
  
  // Fallback: try to find by default name (for decks with custom lists)
  const defaultName = defaultLabels[type];
  return lists.find(l => l.name.toLowerCase() === defaultName.toLowerCase()) || null;
}

/**
 * Get cards for a specific type, considering both list_id and type grouping
 */
export function getCardsForType(
  type: CardType,
  cards: DeckCardResponse[],
  lists: DeckCustomListResponse[],
  defaultLabels: Record<CardType, string> = DEFAULT_TYPE_LABELS
): DeckCardResponse[] {
  const cardsByList = groupCardsByList(cards);
  const cardsByType = groupCardsByType(cards);
  
  const list = findListForType(type, lists, cards, defaultLabels);
  
  // If list exists, return cards from that list, otherwise return type-based cards
  if (list) {
    return cardsByList.get(list.id) || [];
  }
  
  return cardsByType.get(type) || [];
}

