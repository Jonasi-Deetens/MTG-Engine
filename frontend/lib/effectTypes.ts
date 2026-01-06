// frontend/lib/effectTypes.ts

// Shared effect type definitions for ability forms

export interface EffectTypeOption {
  value: string;
  label: string;
  requiresAmount?: boolean;
  requiresTarget?: boolean;
  requiresManaType?: boolean; // For mana abilities
  requiresUntapTarget?: boolean; // For untap effects
  requiresSearchFilters?: boolean; // For library search effects
  requiresAttachTarget?: boolean; // For attach effects
  requiresZone?: boolean; // For search effects
}

export const EFFECT_TYPE_OPTIONS: EffectTypeOption[] = [
  { value: 'damage', label: 'Deal Damage', requiresAmount: true, requiresTarget: true },
  { value: 'draw', label: 'Draw Cards', requiresAmount: true },
  { value: 'token', label: 'Create Token', requiresAmount: true },
  { value: 'counters', label: 'Add Counters', requiresAmount: true },
  { value: 'life', label: 'Gain Life', requiresAmount: true },
  { value: 'mana', label: 'Add Mana', requiresManaType: true },
  { value: 'untap', label: 'Untap', requiresUntapTarget: true },
  { value: 'tap', label: 'Tap', requiresUntapTarget: true },
  { value: 'destroy', label: 'Destroy', requiresTarget: true },
  { value: 'exile', label: 'Exile', requiresTarget: true },
  { value: 'return', label: 'Return to Hand', requiresTarget: true },
  { value: 'sacrifice', label: 'Sacrifice', requiresTarget: true },
  { value: 'search', label: 'Search', requiresSearchFilters: true, requiresZone: true },
  { value: 'put_onto_battlefield', label: 'Put onto Battlefield', requiresTarget: false }, // Can use fromEffect instead
  { value: 'attach', label: 'Attach', requiresAttachTarget: true }, // Can use fromEffect or attachTo
  { value: 'shuffle', label: 'Shuffle Library', requiresTarget: false },
];

export const TARGET_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'any', label: 'Any Target' },
  { value: 'creature', label: 'Target Creature' },
  { value: 'player', label: 'Target Player' },
  { value: 'planeswalker', label: 'Target Planeswalker' },
  { value: 'artifact', label: 'Target Artifact' },
  { value: 'enchantment', label: 'Target Enchantment' },
  { value: 'permanent', label: 'Target Permanent' },
  { value: 'spell', label: 'Target Spell' },
];

export const ATTACH_TARGET_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'target_creature', label: 'Target Creature' },
  { value: 'target_permanent', label: 'Target Permanent' },
  { value: 'triggering_aura', label: 'The Triggering Aura\'s Target' },
  { value: 'triggering_source', label: 'The Triggering Source' },
];

export const SEARCH_ZONE_OPTIONS = [
  { value: 'library', label: 'Library' },
  { value: 'graveyard', label: 'Graveyard' },
  { value: 'hand', label: 'Hand' },
  { value: 'exile', label: 'Exile' },
];

export const CARD_TYPE_FILTERS = [
  { value: 'any', label: 'Any Card' },
  { value: 'creature', label: 'Creature' },
  { value: 'artifact', label: 'Artifact' },
  { value: 'enchantment', label: 'Enchantment' },
  { value: 'aura', label: 'Aura' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'planeswalker', label: 'Planeswalker' },
  { value: 'land', label: 'Land' },
  { value: 'instant', label: 'Instant' },
  { value: 'sorcery', label: 'Sorcery' },
];

export const COMPARE_AGAINST_ZONE_OPTIONS = [
  { value: 'controlled', label: 'Cards You Control' },
  { value: 'battlefield', label: 'On Battlefield' },
  { value: 'graveyard', label: 'In Graveyard' },
  { value: 'hand', label: 'In Hand' },
  { value: 'library', label: 'In Library' },
  { value: 'exile', label: 'In Exile' },
];

export const MANA_TYPE_OPTIONS = [
  { value: 'C', label: 'Colorless (C)' },
  { value: 'W', label: 'White (W)' },
  { value: 'U', label: 'Blue (U)' },
  { value: 'B', label: 'Black (B)' },
  { value: 'R', label: 'Red (R)' },
  { value: 'G', label: 'Green (G)' },
  { value: 'any', label: 'Any Color' },
];

export const UNTAP_TARGET_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'target_creature', label: 'Target Creature' },
  { value: 'target_artifact', label: 'Target Artifact' },
  { value: 'target_permanent', label: 'Target Permanent' },
];

export function formatEffect(effect: any): string {
  if (effect.type === 'damage') {
    return `Deal ${effect.amount || 0} damage${effect.target ? ` to ${effect.target}` : ''}`;
  }
  if (effect.type === 'draw') {
    return `Draw ${effect.amount || 1} card${(effect.amount || 1) > 1 ? 's' : ''}`;
  }
  if (effect.type === 'token') {
    return `Create ${effect.amount || 1} token${(effect.amount || 1) > 1 ? 's' : ''}`;
  }
  if (effect.type === 'counters') {
    return `Put ${effect.amount || 1} +1/+1 counter${(effect.amount || 1) > 1 ? 's' : ''}`;
  }
  if (effect.type === 'life') {
    return `Gain ${effect.amount || 0} life`;
  }
  if (effect.type === 'mana') {
    const amount = effect.amount || 1;
    const manaType = effect.manaType || 'C';
    const manaSymbol = manaType === 'C' ? 'C' : manaType;
    return `Add ${'{' + manaSymbol + '}'.repeat(amount)}`;
  }
  if (effect.type === 'untap') {
    const target = effect.untapTarget || 'self';
    if (target === 'self') {
      return 'Untap this permanent';
    }
      return `Untap ${target.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}`;
    }
    if (effect.type === 'tap') {
      const target = effect.untapTarget || 'self';
      if (target === 'self') {
        return 'Tap this permanent';
      }
      return `Tap ${target.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}`;
  }
  if (effect.type === 'destroy') {
    return `Destroy ${effect.target || 'target'}`;
  }
  if (effect.type === 'exile') {
    return `Exile ${effect.target || 'target'}`;
  }
  if (effect.type === 'return') {
    return `Return ${effect.target || 'target'} to hand`;
  }
  if (effect.type === 'sacrifice') {
    return `Sacrifice ${effect.target || 'target'}`;
  }
  if (effect.type === 'search') {
    const zone = effect.zone || 'library';
    const zoneLabel = zone === 'library' ? 'library' : zone;
    const filters = [];
    if (effect.cardType && effect.cardType !== 'any') {
      filters.push(effect.cardType);
    }
    if (effect.manaValueComparison) {
      if (effect.manaValueComparisonSource) {
        const sourceLabel = effect.manaValueComparisonSource === 'triggering_source' ? 'triggering source' : effect.manaValueComparisonSource;
        const op = effect.manaValueComparison === '<=' ? '≤' : effect.manaValueComparison;
        filters.push(`mana value ${op} ${sourceLabel}'s mana value`);
      } else if (effect.manaValueComparisonValue !== undefined) {
        const op = effect.manaValueComparison === '<=' ? '≤' : effect.manaValueComparison;
        filters.push(`mana value ${op} ${effect.manaValueComparisonValue}`);
      }
    }
    if (effect.differentName) {
      if (typeof effect.differentName === 'object' && effect.differentName.enabled) {
        const typeText = effect.differentName.compareAgainstType && effect.differentName.compareAgainstType !== 'any'
          ? `${effect.differentName.compareAgainstType} `
          : '';
        const zoneText = effect.differentName.compareAgainstZone === 'controlled'
          ? 'you control'
          : effect.differentName.compareAgainstZone === 'battlefield'
          ? 'on the battlefield'
          : effect.differentName.compareAgainstZone
          ? `in ${effect.differentName.compareAgainstZone}`
          : 'you control';
        filters.push(`different name than each ${typeText}card ${zoneText}`);
      } else {
        filters.push('different name');
      }
    }
    const filterText = filters.length > 0 ? ` for ${filters.join(', ')}` : '';
    return `Search your ${zoneLabel}${filterText}`;
  }
  if (effect.type === 'put_onto_battlefield') {
    if (effect.fromEffect !== undefined) {
      return `Put the card from effect ${effect.fromEffect + 1} onto the battlefield`;
    }
    return `Put ${effect.target || 'target'} onto the battlefield`;
  }
  if (effect.type === 'attach') {
    const attachTo = effect.attachTo || 'target';
    if (effect.fromEffect !== undefined) {
      return `Attach the card from effect ${effect.fromEffect + 1} to ${attachTo}`;
    }
    return `Attach to ${attachTo}`;
  }
  if (effect.type === 'shuffle') {
    return 'Shuffle your library';
  }
  return effect.type || 'Unknown effect';
}

