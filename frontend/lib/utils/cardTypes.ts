// frontend/lib/utils/cardTypes.ts

export type CardType = 'Creature' | 'Instant' | 'Sorcery' | 'Artifact' | 'Enchantment' | 'Planeswalker' | 'Land' | 'Other';

/**
 * Determine card type from type line
 */
export function getCardType(typeLine: string | null | undefined): CardType {
  if (!typeLine) return 'Other';
  
  const typeLineLower = typeLine.toLowerCase();
  
  if (typeLineLower.includes('creature')) return 'Creature';
  if (typeLineLower.includes('instant')) return 'Instant';
  if (typeLineLower.includes('sorcery')) return 'Sorcery';
  if (typeLineLower.includes('planeswalker')) return 'Planeswalker';
  if (typeLineLower.includes('land')) return 'Land';
  if (typeLineLower.includes('enchantment') && !typeLineLower.includes('creature')) return 'Enchantment';
  if (typeLineLower.includes('artifact') && !typeLineLower.includes('creature')) return 'Artifact';
  
  return 'Other';
}

/**
 * Default labels for card types
 */
export const DEFAULT_TYPE_LABELS: Record<CardType, string> = {
  'Creature': 'Creatures',
  'Instant': 'Instants',
  'Sorcery': 'Sorceries',
  'Artifact': 'Artifacts',
  'Enchantment': 'Enchantments',
  'Planeswalker': 'Planeswalkers',
  'Land': 'Lands',
  'Other': 'Other',
};

