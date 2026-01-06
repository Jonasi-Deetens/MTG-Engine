// frontend/lib/conditionTypes.ts

// Structured condition types for engine compatibility

export interface ConditionTypeOption {
  value: string;
  label: string;
  requiresValue?: boolean;
  requiresComparison?: boolean;
  requiresTarget?: boolean;
  requiresType?: boolean;
}

export const CONDITION_TYPE_OPTIONS: ConditionTypeOption[] = [
  { value: 'control_count', label: 'Control Count', requiresValue: true, requiresType: true },
  { value: 'life_total', label: 'Life Total', requiresComparison: true, requiresValue: true },
  { value: 'mana_available', label: 'Mana Available', requiresComparison: true, requiresValue: true },
  { value: 'battlefield_count', label: 'Battlefield Count', requiresValue: true, requiresType: true },
  { value: 'graveyard_count', label: 'Graveyard Count', requiresValue: true, requiresType: true },
  { value: 'hand_count', label: 'Hand Count', requiresValue: true, requiresType: true },
  { value: 'power_comparison', label: 'Power Comparison', requiresComparison: true, requiresValue: true, requiresTarget: true },
  { value: 'toughness_comparison', label: 'Toughness Comparison', requiresComparison: true, requiresValue: true, requiresTarget: true },
  { value: 'is_type', label: 'Is Type', requiresType: true, requiresTarget: true },
  { value: 'is_tapped', label: 'Is Tapped', requiresTarget: true },
  { value: 'is_attacking', label: 'Is Attacking', requiresTarget: true },
  { value: 'is_blocking', label: 'Is Blocking', requiresTarget: true },
  { value: 'has_keyword', label: 'Has Keyword', requiresTarget: true },
  { value: 'has_counter', label: 'Has Counter', requiresValue: true, requiresTarget: true },
  { value: 'was_cast', label: 'Was Cast', requiresTarget: true },
  { value: 'mana_value_comparison', label: 'Mana Value Comparison', requiresComparison: true, requiresValue: true, requiresTarget: true },
];

export const COMPARISON_OPERATORS = [
  { value: '>=', label: 'Greater than or equal (≥)' },
  { value: '>', label: 'Greater than (>)' },
  { value: '<=', label: 'Less than or equal (≤)' },
  { value: '<', label: 'Less than (<)' },
  { value: '==', label: 'Equal (==)' },
  { value: '!=', label: 'Not equal (!=)' },
];

export const PERMANENT_TYPES = [
  { value: 'creature', label: 'Creature' },
  { value: 'artifact', label: 'Artifact' },
  { value: 'enchantment', label: 'Enchantment' },
  { value: 'planeswalker', label: 'Planeswalker' },
  { value: 'land', label: 'Land' },
  { value: 'instant', label: 'Instant' },
  { value: 'sorcery', label: 'Sorcery' },
  { value: 'any', label: 'Any Permanent' },
];

export const CONDITION_TARGET_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'target_creature', label: 'Target Creature' },
  { value: 'target_permanent', label: 'Target Permanent' },
  { value: 'you', label: 'You' },
  { value: 'opponent', label: 'Opponent' },
  { value: 'each_player', label: 'Each Player' },
  { value: 'triggering_source', label: 'Triggering Source' },
  { value: 'triggering_aura', label: 'The Triggering Aura' },
  { value: 'triggering_spell', label: 'The Triggering Spell' },
];

export interface StructuredCondition {
  type: string;
  value?: number;
  comparison?: string;
  target?: string;
  permanentType?: string;
  keyword?: string;
  counterType?: string;
  manaValue?: number;
  source?: string; // For mana value comparison - what to compare against (e.g., "triggering_source")
}

export function formatCondition(condition: StructuredCondition | string): string {
  // Handle legacy string conditions
  if (typeof condition === 'string') {
    return condition;
  }

  const cond = condition as StructuredCondition;
  
  switch (cond.type) {
    case 'control_count':
      const type = cond.permanentType || 'permanent';
      return `Control ${cond.value || 0} or more ${type}${(cond.value || 0) > 1 ? 's' : ''}`;
    
    case 'life_total':
      const op = cond.comparison || '>=';
      const opLabel = COMPARISON_OPERATORS.find(o => o.value === op)?.label.split('(')[0].trim() || op;
      return `Life total ${opLabel} ${cond.value || 0}`;
    
    case 'mana_available':
      const manaOp = cond.comparison || '>=';
      const manaOpLabel = COMPARISON_OPERATORS.find(o => o.value === manaOp)?.label.split('(')[0].trim() || manaOp;
      return `Have ${manaOpLabel} ${cond.value || 0} mana available`;
    
    case 'battlefield_count':
      const bfType = cond.permanentType || 'permanent';
      return `${cond.value || 0} or more ${bfType}${(cond.value || 0) > 1 ? 's' : ''} on battlefield`;
    
    case 'graveyard_count':
      const gyType = cond.permanentType || 'card';
      return `${cond.value || 0} or more ${gyType}${(cond.value || 0) > 1 ? 's' : ''} in graveyard`;
    
    case 'hand_count':
      const handType = cond.permanentType || 'card';
      return `${cond.value || 0} or more ${handType}${(cond.value || 0) > 1 ? 's' : ''} in hand`;
    
    case 'power_comparison':
      const powerOp = cond.comparison || '>=';
      const powerOpLabel = COMPARISON_OPERATORS.find(o => o.value === powerOp)?.label.split('(')[0].trim() || powerOp;
      const powerTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${powerTarget} has power ${powerOpLabel} ${cond.value || 0}`;
    
    case 'toughness_comparison':
      const toughOp = cond.comparison || '>=';
      const toughOpLabel = COMPARISON_OPERATORS.find(o => o.value === toughOp)?.label.split('(')[0].trim() || toughOp;
      const toughTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${toughTarget} has toughness ${toughOpLabel} ${cond.value || 0}`;
    
    case 'is_type':
      const isType = cond.permanentType || 'permanent';
      const isTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${isTarget} is a ${isType}`;
    
    case 'is_tapped':
      const tapTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${tapTarget} is tapped`;
    
    case 'is_attacking':
      const atkTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${atkTarget} is attacking`;
    
    case 'is_blocking':
      const blkTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${blkTarget} is blocking`;
    
    case 'has_keyword':
      const kwTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${kwTarget} has ${cond.keyword || 'keyword'}`;
    
    case 'has_counter':
      const counterTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${counterTarget} has ${cond.value || 0} or more ${cond.counterType || '+1/+1'} counter${(cond.value || 0) > 1 ? 's' : ''}`;
    
    case 'was_cast':
      const castTarget = cond.target ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.target)?.label || cond.target : 'target';
      return `${castTarget} was cast`;
    
    case 'mana_value_comparison':
      const mvOp = cond.comparison || '<=';
      const mvOpLabel = COMPARISON_OPERATORS.find(o => o.value === mvOp)?.label.split('(')[0].trim() || mvOp;
      const mvSource = cond.source ? CONDITION_TARGET_OPTIONS.find(t => t.value === cond.source)?.label || cond.source : 'target';
      if (cond.value !== undefined) {
        return `Mana value ${mvOpLabel} ${cond.value} (compared to ${mvSource})`;
      } else {
        return `Mana value ${mvOpLabel} ${mvSource}'s mana value`;
      }
    
    default:
      return 'Unknown condition';
  }
}

