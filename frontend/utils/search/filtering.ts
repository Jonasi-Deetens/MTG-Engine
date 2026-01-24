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
export function filterByType(cards: CardData[], typeFilters: string[]): CardData[] {
  if (!typeFilters.length) return cards;

  const normalized = typeFilters.map((value) => value.toLowerCase());
  return cards.filter(card => {
    const typeLine = card.type_line?.toLowerCase() || '';
    const cardTypes = (card.card_types || []).map((entry) => entry.toLowerCase());
    return normalized.some((value) => cardTypes.includes(value) || typeLine.includes(value));
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
 * Filter cards by rarity
 */
export function filterByRarity(cards: CardData[], rarityFilter: string): CardData[] {
  if (!rarityFilter) return cards;

  const rarityLower = rarityFilter.toLowerCase();
  return cards.filter(card => (card.rarity || '').toLowerCase() === rarityLower);
}

/**
 * Filter cards by language
 */
export function filterByLanguage(cards: CardData[], languageFilter: string): CardData[] {
  if (!languageFilter) return cards;

  const langLower = languageFilter.toLowerCase();
  return cards.filter(card => (card.lang || '').toLowerCase() === langLower);
}

/**
 * Filter cards by keywords
 */
export function filterByKeywords(cards: CardData[], keywordFilter: string): CardData[] {
  if (!keywordFilter) return cards;

  const keywords = keywordFilter
    .split(',')
    .map(keyword => keyword.trim().toLowerCase())
    .filter(Boolean);

  if (keywords.length === 0) return cards;

  return cards.filter(card => {
    const cardKeywords = (card.keywords || []).map(keyword => keyword.toLowerCase());
    return keywords.some(keyword => cardKeywords.includes(keyword));
  });
}

/**
 * Apply all filters to cards
 */
export function applyFilters(
  cards: CardData[],
  selectedColors: string[],
  typeFilters: string[],
  setFilter: string,
  rarityFilter: string,
  languageFilter: string,
  keywordFilter: string
): CardData[] {
  let filtered = cards;
  filtered = filterByColors(filtered, selectedColors);
  filtered = filterByType(filtered, typeFilters);
  filtered = filterBySet(filtered, setFilter);
  filtered = filterByRarity(filtered, rarityFilter);
  filtered = filterByLanguage(filtered, languageFilter);
  filtered = filterByKeywords(filtered, keywordFilter);
  return filtered;
}

