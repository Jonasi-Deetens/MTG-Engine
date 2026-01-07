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
  requiresDuration?: boolean; // For temporary effects
  requiresChoice?: boolean; // For effects requiring player choice
  requiresProtectionType?: boolean; // For protection effects
  requiresKeyword?: boolean; // For gain keyword effects
  requiresPowerToughness?: boolean; // For change power/toughness effects
  requiresTwoTargets?: boolean; // For fight, redirect damage effects
  requiresDiscardType?: boolean; // For discard effects
  requiresPosition?: boolean; // For look at effects
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
  // New effect types
  { value: 'protection', label: 'Gain Protection', requiresTarget: true, requiresDuration: true, requiresProtectionType: true, requiresChoice: true },
  { value: 'gain_keyword', label: 'Gain Keyword', requiresTarget: true, requiresDuration: true, requiresKeyword: true },
  { value: 'change_power_toughness', label: 'Change Power/Toughness', requiresTarget: true, requiresDuration: true, requiresPowerToughness: true },
  { value: 'fight', label: 'Fight', requiresTwoTargets: true },
  { value: 'mill', label: 'Mill', requiresTarget: true, requiresAmount: true },
  { value: 'discard', label: 'Discard', requiresTarget: true, requiresAmount: true, requiresDiscardType: true },
  { value: 'scry', label: 'Scry', requiresAmount: true },
  { value: 'look_at', label: 'Look At', requiresAmount: true, requiresZone: true, requiresPosition: true },
  { value: 'reveal', label: 'Reveal', requiresTarget: true },
  { value: 'copy_spell', label: 'Copy Spell', requiresTarget: true },
  { value: 'regenerate', label: 'Regenerate', requiresTarget: true },
  { value: 'phase_out', label: 'Phase Out', requiresTarget: true },
  { value: 'transform', label: 'Transform', requiresTarget: true },
  { value: 'flicker', label: 'Flicker (Exile & Return)', requiresTarget: true },
  { value: 'change_control', label: 'Change Control', requiresTarget: true, requiresDuration: true },
  { value: 'prevent_damage', label: 'Prevent Damage', requiresTarget: true, requiresAmount: true },
  { value: 'redirect_damage', label: 'Redirect Damage', requiresTwoTargets: true, requiresAmount: true },
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
  { value: 'commander', label: 'Target Commander' },
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

export const DURATION_OPTIONS = [
  { value: 'permanent', label: 'Permanent' },
  { value: 'until_end_of_turn', label: 'Until End of Turn' },
  { value: 'until_end_of_your_next_turn', label: 'Until End of Your Next Turn' },
  { value: 'until_end_of_combat', label: 'Until End of Combat' },
  { value: 'until_your_next_upkeep', label: 'Until Your Next Upkeep' },
];

export const CHOICE_TYPE_OPTIONS = [
  { value: 'color', label: 'Choose a Color' },
  { value: 'creature_type', label: 'Choose a Creature Type' },
  { value: 'card_type', label: 'Choose a Card Type' },
  { value: 'target', label: 'Choose a Target' },
];

export const PROTECTION_TYPE_OPTIONS = [
  { value: 'white', label: 'White' },
  { value: 'blue', label: 'Blue' },
  { value: 'black', label: 'Black' },
  { value: 'red', label: 'Red' },
  { value: 'green', label: 'Green' },
  { value: 'colorless', label: 'Colorless' },
  { value: 'all_colors', label: 'All Colors' },
  { value: 'artifact', label: 'Artifact' },
  { value: 'enchantment', label: 'Enchantment' },
  { value: 'creature', label: 'Creature' },
  { value: 'instant', label: 'Instant' },
  { value: 'sorcery', label: 'Sorcery' },
  { value: 'planeswalker', label: 'Planeswalker' },
  { value: 'land', label: 'Land' },
  { value: 'chosen_color', label: 'Chosen Color (Player Choice)' },
];

export const DISCARD_TYPE_OPTIONS = [
  { value: 'random', label: 'Random' },
  { value: 'chosen', label: 'Chosen by Player' },
  { value: 'all_of_type', label: 'All Cards of Chosen Type' },
];

export const LOOK_AT_POSITION_OPTIONS = [
  { value: 'top', label: 'Top' },
  { value: 'bottom', label: 'Bottom' },
  { value: 'random', label: 'Random' },
];

// Helper function to format duration
export function formatDuration(duration: string | undefined): string {
  if (!duration || duration === 'permanent') {
    return '';
  }
  const durationMap: Record<string, string> = {
    'until_end_of_turn': 'until end of turn',
    'until_end_of_your_next_turn': 'until end of your next turn',
    'until_end_of_combat': 'until end of combat',
    'until_your_next_upkeep': 'until your next upkeep',
  };
  return durationMap[duration] || duration;
}

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
  
  // Protection
  if (effect.type === 'protection') {
    const target = effect.target || 'target creature';
    const protectionType = effect.protectionType || 'white';
    const protectionLabel = PROTECTION_TYPE_OPTIONS.find(opt => opt.value === protectionType)?.label || protectionType;
    const duration = formatDuration(effect.duration);
    const choiceText = effect.choice ? ` (player chooses ${effect.choice})` : '';
    return `Target ${target} gains protection from ${protectionLabel}${duration ? ` ${duration}` : ''}${choiceText}`;
  }
  
  // Gain Keyword
  if (effect.type === 'gain_keyword') {
    const target = effect.target || 'target creature';
    const keyword = effect.keyword || 'keyword';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gains ${keyword}${duration ? ` ${duration}` : ''}`;
  }
  
  // Change Power/Toughness
  if (effect.type === 'change_power_toughness') {
    const target = effect.target || 'target creature';
    const powerChange = effect.powerChange || 0;
    const toughnessChange = effect.toughnessChange || 0;
    const powerSign = powerChange >= 0 ? '+' : '';
    const toughnessSign = toughnessChange >= 0 ? '+' : '';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gets ${powerSign}${powerChange}/${toughnessSign}${toughnessChange}${duration ? ` ${duration}` : ''}`;
  }
  
  // Fight
  if (effect.type === 'fight') {
    const yourCreature = effect.yourCreature || 'target creature you control';
    const opponentCreature = effect.opponentCreature || 'target creature you don\'t control';
    return `Target ${yourCreature} fights target ${opponentCreature}`;
  }
  
  // Mill
  if (effect.type === 'mill') {
    const target = effect.target || 'target player';
    const amount = effect.amount || 1;
    return `Target ${target} mills ${amount} card${amount > 1 ? 's' : ''}`;
  }
  
  // Discard
  if (effect.type === 'discard') {
    const target = effect.target || 'target player';
    const amount = effect.amount || 1;
    const discardType = effect.discardType || 'chosen';
    const discardTypeLabel = DISCARD_TYPE_OPTIONS.find(opt => opt.value === discardType)?.label || discardType;
    return `Target ${target} discards ${amount} card${amount > 1 ? 's' : ''} (${discardTypeLabel})`;
  }
  
  // Scry
  if (effect.type === 'scry') {
    const amount = effect.amount || 1;
    return `Scry ${amount}`;
  }
  
  // Look At
  if (effect.type === 'look_at') {
    const amount = effect.amount || 1;
    const zone = effect.zone || 'library';
    const position = effect.position || 'top';
    const positionLabel = LOOK_AT_POSITION_OPTIONS.find(opt => opt.value === position)?.label || position;
    const zoneLabel = zone === 'library' ? 'your library' : `your ${zone}`;
    return `Look at the ${positionLabel} ${amount} card${amount > 1 ? 's' : ''} of ${zoneLabel}`;
  }
  
  // Reveal
  if (effect.type === 'reveal') {
    const target = effect.target || 'target';
    return `Reveal ${target}`;
  }
  
  // Copy Spell
  if (effect.type === 'copy_spell') {
    const target = effect.target || 'target spell';
    return `Copy ${target}`;
  }
  
  // Regenerate
  if (effect.type === 'regenerate') {
    const target = effect.target || 'target creature';
    return `Regenerate ${target}`;
  }
  
  // Phase Out
  if (effect.type === 'phase_out') {
    const target = effect.target || 'target permanent';
    return `Target ${target} phases out`;
  }
  
  // Transform
  if (effect.type === 'transform') {
    const target = effect.target || 'target permanent';
    return `Transform ${target}`;
  }
  
  // Flicker
  if (effect.type === 'flicker') {
    const target = effect.target || 'target permanent';
    const ownerText = effect.returnUnderOwner ? " under its owner's control" : '';
    return `Exile ${target}, then return it to the battlefield${ownerText}`;
  }
  
  // Change Control
  if (effect.type === 'change_control') {
    const target = effect.target || 'target permanent';
    const duration = formatDuration(effect.duration);
    return `Gain control of ${target}${duration ? ` ${duration}` : ''}`;
  }
  
  // Prevent Damage
  if (effect.type === 'prevent_damage') {
    const target = effect.target || 'target';
    const amount = effect.amount || 1;
    return `Prevent the next ${amount} damage that would be dealt to ${target} this turn`;
  }
  
  // Redirect Damage
  if (effect.type === 'redirect_damage') {
    const sourceTarget = effect.sourceTarget || 'target';
    const redirectTarget = effect.redirectTarget || 'another target';
    const amount = effect.amount || 1;
    return `The next ${amount} damage that would be dealt to ${sourceTarget} is dealt to ${redirectTarget} instead`;
  }
  
  return effect.type || 'Unknown effect';
}

