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
  requiresChoiceValue?: boolean; // For fixed choice values
  requiresProtectionType?: boolean; // For protection effects
  requiresKeyword?: boolean; // For gain keyword effects
  requiresPowerToughness?: boolean; // For change power/toughness effects
  requiresTwoTargets?: boolean; // For fight, redirect damage effects
  requiresDiscardType?: boolean; // For discard effects
  requiresPosition?: boolean; // For look at effects
  requiresTypeList?: boolean;
  requiresTypeName?: boolean;
  requiresColorList?: boolean;
  requiresColor?: boolean;
  requiresCdaSource?: boolean;
  requiresCdaSet?: boolean;
  requiresFromZone?: boolean;
  requiresToZone?: boolean;
  requiresReplacementZone?: boolean;
  requiresUses?: boolean;
  requiresCopyDuration?: boolean;
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
  { value: 'enter_copy', label: 'As Enters Copy Target', requiresTarget: true },
  { value: 'enter_choice', label: 'As Enters Choose', requiresChoice: true, requiresChoiceValue: true },
  { value: 'copy_permanent', label: 'Copy Permanent (this becomes a copy)', requiresTarget: true, requiresDuration: true },
  { value: 'counter_spell', label: 'Counter Spell', requiresTarget: true },
  { value: 'regenerate', label: 'Regenerate', requiresTarget: true },
  { value: 'phase_out', label: 'Phase Out', requiresTarget: true },
  { value: 'transform', label: 'Transform', requiresTarget: true },
  { value: 'flicker', label: 'Flicker (Exile & Return)', requiresTarget: true },
  { value: 'change_control', label: 'Change Control', requiresTarget: true, requiresDuration: true },
  { value: 'prevent_damage', label: 'Prevent Damage', requiresTarget: true, requiresAmount: true },
  { value: 'redirect_damage', label: 'Redirect Damage', requiresTwoTargets: true, requiresAmount: true },
  { value: 'set_types', label: 'Set Types', requiresTarget: true, requiresTypeList: true, requiresDuration: true },
  { value: 'add_type', label: 'Add Type', requiresTarget: true, requiresTypeName: true, requiresDuration: true },
  { value: 'remove_type', label: 'Remove Type', requiresTarget: true, requiresTypeName: true, requiresDuration: true },
  { value: 'set_colors', label: 'Set Colors', requiresTarget: true, requiresColorList: true, requiresDuration: true },
  { value: 'add_color', label: 'Add Color', requiresTarget: true, requiresColor: true, requiresDuration: true },
  { value: 'remove_color', label: 'Remove Color', requiresTarget: true, requiresColor: true, requiresDuration: true },
  { value: 'cda_power_toughness', label: 'CDA Power/Toughness', requiresCdaSource: true, requiresCdaSet: true },
  {
    value: 'replace_zone_change',
    label: 'Replace Zone Change',
    requiresTarget: true,
    requiresDuration: true,
    requiresFromZone: true,
    requiresToZone: true,
    requiresReplacementZone: true,
    requiresUses: true,
  },
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

export const ZONE_OPTIONS = [
  { value: 'battlefield', label: 'Battlefield' },
  { value: 'graveyard', label: 'Graveyard' },
  { value: 'hand', label: 'Hand' },
  { value: 'library', label: 'Library' },
  { value: 'exile', label: 'Exile' },
  { value: 'command', label: 'Command' },
  { value: 'stack', label: 'Stack' },
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

export const COLOR_OPTIONS = [
  { value: 'W', label: 'White (W)' },
  { value: 'U', label: 'Blue (U)' },
  { value: 'B', label: 'Black (B)' },
  { value: 'R', label: 'Red (R)' },
  { value: 'G', label: 'Green (G)' },
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

export const CDA_SOURCE_OPTIONS = [
  { value: 'controlled', label: 'Count permanents you control' },
  { value: 'zone', label: 'Count cards in a zone' },
];

export const CDA_TYPE_OPTIONS = [
  { value: 'Permanent', label: 'Permanent' },
  { value: 'Creature', label: 'Creature' },
  { value: 'Land', label: 'Land' },
  { value: 'Artifact', label: 'Artifact' },
  { value: 'Enchantment', label: 'Enchantment' },
  { value: 'Planeswalker', label: 'Planeswalker' },
];

export const CDA_ZONE_OPTIONS = [
  { value: 'hand', label: 'Your hand' },
  { value: 'graveyard', label: 'Your graveyard' },
  { value: 'all_graveyards', label: 'All graveyards' },
];

export const CDA_SET_OPTIONS = [
  { value: 'both', label: 'Power and Toughness' },
  { value: 'power', label: 'Power only' },
  { value: 'toughness', label: 'Toughness only' },
];

export const CDA_TEMPLATE_OPTIONS = [
  {
    value: 'creatures_you_control',
    label: 'Creatures you control',
    config: { cdaSource: 'controlled', cdaType: 'Creature', cdaSet: 'both' },
  },
  {
    value: 'permanents_you_control',
    label: 'Permanents you control',
    config: { cdaSource: 'controlled', cdaType: 'Permanent', cdaSet: 'both' },
  },
  {
    value: 'cards_in_hand',
    label: 'Cards in your hand',
    config: { cdaSource: 'zone', cdaZone: 'hand', cdaSet: 'both' },
  },
  {
    value: 'cards_in_graveyard',
    label: 'Cards in your graveyard',
    config: { cdaSource: 'zone', cdaZone: 'graveyard', cdaSet: 'both' },
  },
  {
    value: 'cards_in_all_graveyards',
    label: 'Cards in all graveyards',
    config: { cdaSource: 'zone', cdaZone: 'all_graveyards', cdaSet: 'both' },
  },
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
  const maxTargetsText = effect.maxTargets ? ` (up to ${effect.maxTargets})` : '';
  if (effect.type === 'damage') {
    return `Deal ${effect.amount || 0} damage${effect.target ? ` to ${effect.target}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'draw') {
    return `Draw ${effect.amount || 1} card${(effect.amount || 1) > 1 ? 's' : ''}`;
  }
  if (effect.type === 'token') {
    return `Create ${effect.amount || 1} token${(effect.amount || 1) > 1 ? 's' : ''}`;
  }
  if (effect.type === 'counters') {
    return `Put ${effect.amount || 1} +1/+1 counter${(effect.amount || 1) > 1 ? 's' : ''}${maxTargetsText}`;
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
      return `Untap this permanent${maxTargetsText}`;
    }
      return `Untap ${target.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}${maxTargetsText}`;
    }
    if (effect.type === 'tap') {
      const target = effect.untapTarget || 'self';
      if (target === 'self') {
        return `Tap this permanent${maxTargetsText}`;
      }
      return `Tap ${target.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}${maxTargetsText}`;
  }
  if (effect.type === 'destroy') {
    return `Destroy ${effect.target || 'target'}${maxTargetsText}`;
  }
  if (effect.type === 'exile') {
    return `Exile ${effect.target || 'target'}${maxTargetsText}`;
  }
  if (effect.type === 'return') {
    return `Return ${effect.target || 'target'} to hand${maxTargetsText}`;
  }
  if (effect.type === 'sacrifice') {
    return `Sacrifice ${effect.target || 'target'}${maxTargetsText}`;
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
    return `Target ${target} gains protection from ${protectionLabel}${duration ? ` ${duration}` : ''}${choiceText}${maxTargetsText}`;
  }
  
  // Gain Keyword
  if (effect.type === 'gain_keyword') {
    const target = effect.target || 'target creature';
    const keyword = effect.keyword || 'keyword';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gains ${keyword}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  
  // Change Power/Toughness
  if (effect.type === 'change_power_toughness') {
    const target = effect.target || 'target creature';
    const powerChange = effect.powerChange || 0;
    const toughnessChange = effect.toughnessChange || 0;
    const powerSign = powerChange >= 0 ? '+' : '';
    const toughnessSign = toughnessChange >= 0 ? '+' : '';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gets ${powerSign}${powerChange}/${toughnessSign}${toughnessChange}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }

  if (effect.type === 'cda_power_toughness') {
    const cdaSet = effect.cdaSet || 'both';
    const setLabel = cdaSet === 'power'
      ? 'Power is'
      : cdaSet === 'toughness'
      ? 'Toughness is'
      : 'Power and toughness are each';
    if (effect.cdaSource === 'zone') {
      const zoneLabel = CDA_ZONE_OPTIONS.find(opt => opt.value === effect.cdaZone)?.label || 'your hand';
      return `${setLabel} equal to the number of cards in ${zoneLabel.toLowerCase()}`;
    }
    const typeLabel = CDA_TYPE_OPTIONS.find(opt => opt.value === effect.cdaType)?.label || 'permanents';
    return `${setLabel} equal to the number of ${typeLabel.toLowerCase()} you control`;
  }

  if (effect.type === 'replace_zone_change') {
    const fromZone = ZONE_OPTIONS.find(opt => opt.value === effect.fromZone)?.label || 'Battlefield';
    const toZone = ZONE_OPTIONS.find(opt => opt.value === effect.toZone)?.label || 'Graveyard';
    const replacement = ZONE_OPTIONS.find(opt => opt.value === effect.replacementZone)?.label || 'Exile';
    const usesText = effect.uses ? ` (next ${effect.uses})` : '';
    const duration = formatDuration(effect.duration);
    return `If it would move from ${fromZone} to ${toZone}, put it into ${replacement} instead${duration ? ` ${duration}` : ''}${usesText}`;
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
    return `Target ${target} mills ${amount} card${amount > 1 ? 's' : ''}${maxTargetsText}`;
  }
  
  // Discard
  if (effect.type === 'discard') {
    const target = effect.target || 'target player';
    const amount = effect.amount || 1;
    const discardType = effect.discardType || 'chosen';
    const discardTypeLabel = DISCARD_TYPE_OPTIONS.find(opt => opt.value === discardType)?.label || discardType;
    return `Target ${target} discards ${amount} card${amount > 1 ? 's' : ''} (${discardTypeLabel})${maxTargetsText}`;
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
    return `Reveal ${target}${maxTargetsText}`;
  }
  
  // Copy Spell
  if (effect.type === 'copy_spell') {
    const target = effect.target || 'target spell';
    return `Copy ${target}${maxTargetsText}`;
  }
  if (effect.type === 'enter_copy') {
    const target = effect.target || 'target permanent';
    return `As this enters, it becomes a copy of ${target}${maxTargetsText}`;
  }
  if (effect.type === 'enter_choice') {
    const choice = effect.choice || 'choice';
    const value = effect.choiceValue ? ` (${effect.choiceValue})` : '';
    return `As this enters, choose ${choice}${value}`;
  }
  if (effect.type === 'copy_permanent') {
    const target = effect.target || 'target permanent';
    const duration = formatDuration(effect.duration);
    return `This becomes a copy of ${target}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'counter_spell') {
    const target = effect.target || 'target spell';
    return `Counter ${target}${maxTargetsText}`;
  }
  
  // Regenerate
  if (effect.type === 'regenerate') {
    const target = effect.target || 'target creature';
    return `Regenerate ${target}${maxTargetsText}`;
  }
  
  // Phase Out
  if (effect.type === 'phase_out') {
    const target = effect.target || 'target permanent';
    return `Target ${target} phases out${maxTargetsText}`;
  }
  
  // Transform
  if (effect.type === 'transform') {
    const target = effect.target || 'target permanent';
    return `Transform ${target}${maxTargetsText}`;
  }
  
  // Flicker
  if (effect.type === 'flicker') {
    const target = effect.target || 'target permanent';
    const ownerText = effect.returnUnderOwner ? " under its owner's control" : '';
    return `Exile ${target}, then return it to the battlefield${ownerText}${maxTargetsText}`;
  }
  
  // Change Control
  if (effect.type === 'change_control') {
    const target = effect.target || 'target permanent';
    const duration = formatDuration(effect.duration);
    return `Gain control of ${target}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  
  // Prevent Damage
  if (effect.type === 'prevent_damage') {
    const target = effect.target || 'target';
    const amount = effect.amount || 1;
    return `Prevent the next ${amount} damage that would be dealt to ${target} this turn${maxTargetsText}`;
  }
  if (effect.type === 'set_types') {
    const target = effect.target || 'target permanent';
    const types = Array.isArray(effect.types)
      ? effect.types
          .map((type: string) => (type === 'chosen_card_type' ? 'chosen card type' : type))
          .join(', ')
      : 'types';
    const duration = formatDuration(effect.duration);
    return `Target ${target} becomes ${types}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'add_type') {
    const target = effect.target || 'target permanent';
    const typeName = effect.typeName === 'chosen_card_type' ? 'chosen card type' : effect.typeName || 'type';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gains ${typeName}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'remove_type') {
    const target = effect.target || 'target permanent';
    const typeName = effect.typeName === 'chosen_card_type' ? 'chosen card type' : effect.typeName || 'type';
    const duration = formatDuration(effect.duration);
    return `Target ${target} loses ${typeName}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'set_colors') {
    const target = effect.target || 'target permanent';
    const colors = Array.isArray(effect.colors)
      ? effect.colors
          .map((color: string) => (color === 'chosen_color' ? 'chosen color' : color))
          .join(', ')
      : 'colors';
    const duration = formatDuration(effect.duration);
    return `Target ${target} becomes ${colors}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'add_color') {
    const target = effect.target || 'target permanent';
    const color = effect.color === 'chosen_color' ? 'chosen color' : effect.color || 'color';
    const duration = formatDuration(effect.duration);
    return `Target ${target} gains ${color}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
  }
  if (effect.type === 'remove_color') {
    const target = effect.target || 'target permanent';
    const color = effect.color === 'chosen_color' ? 'chosen color' : effect.color || 'color';
    const duration = formatDuration(effect.duration);
    return `Target ${target} loses ${color}${duration ? ` ${duration}` : ''}${maxTargetsText}`;
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

