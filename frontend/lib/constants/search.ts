// frontend/lib/constants/search.ts

export const COLORS = ['W', 'U', 'B', 'R', 'G', 'C'];

export const COLOR_NAMES: Record<string, string> = {
  'W': 'White',
  'U': 'Blue',
  'B': 'Black',
  'R': 'Red',
  'G': 'Green',
  'C': 'Colorless',
};

export const RARITY_OPTIONS = [
  { value: '', label: 'Any Rarity' },
  { value: 'common', label: 'Common' },
  { value: 'uncommon', label: 'Uncommon' },
  { value: 'rare', label: 'Rare' },
  { value: 'mythic', label: 'Mythic' },
];

export const CARD_TYPE_OPTIONS = [
  { value: 'creature', label: 'Creature' },
  { value: 'instant', label: 'Instant' },
  { value: 'sorcery', label: 'Sorcery' },
  { value: 'artifact', label: 'Artifact' },
  { value: 'enchantment', label: 'Enchantment' },
  { value: 'planeswalker', label: 'Planeswalker' },
  { value: 'land', label: 'Land' },
  { value: 'battle', label: 'Battle' },
  { value: 'aura', label: 'Aura' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'legendary', label: 'Legendary' },
];

export const LANGUAGE_OPTIONS = [
  { value: '', label: 'Any Language' },
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
  { value: 'it', label: 'Italian' },
  { value: 'pt', label: 'Portuguese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'ru', label: 'Russian' },
  { value: 'zhs', label: 'Simplified Chinese' },
  { value: 'zht', label: 'Traditional Chinese' },
];

export const PAGE_SIZE = 24;

