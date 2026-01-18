import { parseManaCostSymbols, formatManaCostLabel } from '@/lib/wardCosts';

export type CostEntry =
  | { type: 'mana'; cost: string }
  | { type: 'tap_self' }
  | { type: 'life'; amount: number }
  | { type: 'discard'; amount: number }
  | { type: 'sacrifice'; card_type?: string; nonland?: boolean }
  | { type: 'sacrifice_self' }
  | { type: 'tap'; card_type?: string; nonland?: boolean }
  | { type: 'exile_graveyard'; amount: number; other?: boolean };

export type ActivationCost =
  | { type: 'mana'; costText: string; cost: ReturnType<typeof parseManaCostSymbols> }
  | { type: 'tap_self' }
  | { type: 'life'; amount: number }
  | { type: 'discard'; amount: number }
  | { type: 'sacrifice'; card_type?: string; nonland?: boolean }
  | { type: 'sacrifice_self' }
  | { type: 'tap'; card_type?: string; nonland?: boolean }
  | { type: 'exile_graveyard'; amount: number; other?: boolean };

export const buildActivationCosts = (costs: CostEntry[]): ActivationCost[] =>
  costs.map((entry) => {
    if (entry.type === 'mana') {
      const costText = entry.cost;
      return { type: 'mana', costText, cost: parseManaCostSymbols(costText) };
    }
    return entry;
  });

export const formatActivationCostLabel = (cost: ActivationCost) => {
  if (cost.type === 'mana') return formatManaCostLabel(cost.cost);
  if (cost.type === 'life') return `pay ${cost.amount} life`;
  if (cost.type === 'discard') return `discard ${cost.amount} card${cost.amount === 1 ? '' : 's'}`;
  if (cost.type === 'sacrifice') return `sacrifice ${cost.nonland ? 'nonland ' : ''}${cost.card_type ?? 'permanent'}`;
  if (cost.type === 'sacrifice_self') return 'sacrifice this';
  if (cost.type === 'tap') return `tap ${cost.nonland ? 'nonland ' : ''}${cost.card_type ?? 'permanent'}`;
  if (cost.type === 'tap_self') return 'tap this';
  if (cost.type === 'exile_graveyard') {
    return `exile ${cost.amount} card${cost.amount === 1 ? '' : 's'} from your graveyard`;
  }
  return 'cost';
};

