// frontend/utils/search/filtering.ts

import { CardData } from '@/components/cards/CardPreview';

/**
 * Filter cards by selected colors
 */
export function filterByColors(cards: CardData[], selectedColors: string[]): CardData[] {
  if (selectedColors.length === 0) return cards;
  
  return cards.filter(card => {
    const cardColors = card.color_identity || [];
    // If no color identity, include colorless cards only if 'C' is selected
    if (cardColors.length === 0) {
      return selectedColors.includes('C');
    }
    // Check if any of the card's colors match selected colors
    return cardColors.some(color => selectedColors.includes(color));
  });
}

/**
 * Filter cards by type
 */
export function filterByType(cards: CardData[], typeFilter: string): CardData[] {
  if (!typeFilter) return cards;
  
  const typeLower = typeFilter.toLowerCase();
  return cards.filter(card => {
    const typeLine = card.type_line?.toLowerCase() || '';
    return typeLine.includes(typeLower);
  });
}

/**
 * Filter cards by set code
 */
export function filterBySet(cards: CardData[], setFilter: string): CardData[] {
  if (!setFilter) return cards;
  
  return cards.filter(card => {
    return card.set?.toLowerCase() === setFilter.toLowerCase();
  });
}

/**
 * Apply all filters to cards
 */
export function applyFilters(
  cards: CardData[],
  selectedColors: string[],
  typeFilter: string,
  setFilter: string
): CardData[] {
  let filtered = cards;
  filtered = filterByColors(filtered, selectedColors);
  filtered = filterByType(filtered, typeFilter);
  filtered = filterBySet(filtered, setFilter);
  return filtered;
}

