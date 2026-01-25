import { CostEntry } from '@/lib/activationCosts';
import { parseManaCostSymbols, serializeManaCostSymbols } from '@/lib/wardCosts';
import type { EffectGraph } from '@/lib/unifiedEffect';
import { formatOptionalCostLabel, normalizeOptionalCostEntry, OptionalCostEntry } from '@/lib/optionalCosts';

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

export const deriveOptionalCastCostsFromGraph = (graph?: EffectGraph | null): OptionalCastCostOption[] => {
  if (!graph?.steps?.length) return [];
  const raw = graph.optionalCosts ?? [];
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((entry) => entry && typeof entry === 'object')
    .map((entry) => normalizeOptionalCostEntry(entry as OptionalCostEntry))
    .map((entry) => ({
      tag: entry.tag ?? '',
      label: formatOptionalCostLabel(entry),
      costs: entry.costs ?? [],
      kind: entry.kind,
      repeatable: !!entry.repeatable,
    }))
    .filter((entry) => entry.tag);
};

export const deriveAdditionalCostsFromGraph = (graph?: EffectGraph | null): CostEntry[] => {
  if (!graph?.steps?.length) return [];
  const additionalCosts = graph.additionalCosts ?? [];
  return Array.isArray(additionalCosts) ? additionalCosts : [];
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

const findManaCost = (data?: any) => {
  if (!data) return '';
  const costs = normalizeCostEntries(data);
  const mana = costs.find((entry) => entry.type === 'mana') as CostEntry | undefined;
  if (!mana || !('cost' in mana)) return '';
  return serializeManaCostSymbols(mana.cost as any);
};

