import { CostEntry, buildActivationCosts, formatActivationCostLabel } from '@/lib/activationCosts';
import { parseManaCostSymbols, serializeManaCostSymbols } from '@/lib/wardCosts';
import type { EffectGraph } from '@/lib/unifiedEffect';

export type OptionalCastCostOption = {
  tag: string;
  label: string;
  costs: CostEntry[];
  kind: 'kicker' | 'multikicker' | 'buyback' | 'entwine' | 'replicate' | 'conspire';
  repeatable: boolean;
};

export type AlternativeCostOption = {
  tag: string;
  label: string;
};

const OPTIONAL_KEYWORDS: Record<
  OptionalCastCostOption['kind'],
  { repeatable: boolean; label: (costText: string) => string }
> = {
  kicker: { repeatable: false, label: (costText) => `Kicker ${costText}` },
  multikicker: { repeatable: true, label: (costText) => `Multikicker ${costText}` },
  buyback: { repeatable: false, label: (costText) => `Buyback ${costText}` },
  entwine: { repeatable: false, label: (costText) => `Entwine ${costText}` },
  replicate: { repeatable: true, label: (costText) => `Replicate ${costText}` },
  conspire: { repeatable: false, label: () => 'Conspire' },
};

export const deriveOptionalCastCostsFromGraph = (graph?: EffectGraph | null): OptionalCastCostOption[] => {
  if (!graph?.steps?.length) return [];
  // Optional cast costs are not represented in unified EffectGraph yet.
  return [];
};

export const deriveAdditionalCostsFromGraph = (graph?: EffectGraph | null): CostEntry[] => {
  if (!graph?.steps?.length) return [];
  // Spell additional costs are not represented in unified EffectGraph yet.
  return [];
};

export const deriveAlternativeCastCostsFromGraph = (graph?: EffectGraph | null): AlternativeCostOption[] => {
  if (!graph?.steps?.length) return [];
  // Alternative casting costs are not represented in unified EffectGraph yet.
  return [];
};

export const deriveAlternativeExtraCostsFromGraph = (graph: EffectGraph | null, tag: string | null): CostEntry[] => {
  if (!graph?.steps?.length || !tag) return [];
  // Extra costs for alternative casting are not represented in unified EffectGraph yet.
  return [];
};

export const deriveSpliceCardsFromHand = (
  hand: string[],
  cardGraphs: Record<string, EffectGraph> | undefined
): Array<{ cardId: string; costs: CostEntry[] }> => {
  if (!hand.length || !cardGraphs) return [];
  // Splice data is not represented in unified EffectGraph yet.
  return [];
};

export const deriveWardCostsFromGraphs = (graphs?: EffectGraph[]): CostEntry[] => {
  if (!graphs || graphs.length === 0) return [];
  // Ward costs are not represented in unified EffectGraph yet.
  return [];
};

const findKeywordNode = (graph: any, keyword: string) =>
  graph.nodes.find((node: any) => {
    if (node?.type !== 'KEYWORD') return false;
    const name = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
    return name === keyword;
  });

const normalizeCostEntries = (data?: any): CostEntry[] => {
  if (!data) return [];
  const costs: CostEntry[] = [];
  if (Array.isArray(data.costs)) {
    data.costs.forEach((entry: any) => {
      if (entry && typeof entry === 'object' && entry.type) {
        costs.push(entry);
      }
    });
  }
  if (costs.length === 0 && typeof data.cost === 'string' && data.cost.includes('{')) {
    costs.push({ type: 'mana', cost: parseManaCostSymbols(data.cost) });
  }
  if (typeof data.lifeCost === 'number' && data.lifeCost > 0) {
    costs.push({ type: 'life', amount: data.lifeCost });
  }
  if (data.sacrificeCost) {
    costs.push({ type: 'sacrifice' });
  }
  return costs;
};

const formatCostsLabel = (costs: CostEntry[]) => {
  if (!costs.length) return '';
  return buildActivationCosts(costs).map(formatActivationCostLabel).join(', ');
};

const findManaCost = (data?: any) => {
  if (!data) return '';
  const costs = normalizeCostEntries(data);
  const mana = costs.find((entry) => entry.type === 'mana') as CostEntry | undefined;
  if (!mana || !('cost' in mana)) return '';
  return serializeManaCostSymbols(mana.cost as any);
};

const buildCostTag = (costs: CostEntry[]) => {
  if (!costs.length) return '';
  return costs
    .map((cost) => {
      if (cost.type === 'mana') return serializeManaCostSymbols(cost.cost as any);
      if (cost.type === 'life' || cost.type === 'discard' || cost.type === 'exile_graveyard') {
        return `${cost.type}:${cost.amount}`;
      }
      if (cost.type === 'tap_self') return 'tap_self';
      if (cost.type === 'sacrifice_self') return 'sacrifice_self';
      if (cost.type === 'tap') return `tap:${(cost as any).card_type ?? 'permanent'}`;
      if (cost.type === 'sacrifice') return `sacrifice:${(cost as any).card_type ?? 'permanent'}`;
      return cost.type;
    })
    .join('+');
};

