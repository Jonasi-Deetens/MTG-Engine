import { CostEntry, buildActivationCosts, formatActivationCostLabel } from '@/lib/activationCosts';
import { parseManaCostSymbols, serializeManaCostSymbols } from '@/lib/wardCosts';

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

export const deriveOptionalCastCostsFromGraph = (graph?: any): OptionalCastCostOption[] => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  const options: OptionalCastCostOption[] = [];
  graph.nodes.forEach((node: any) => {
    if (node?.type !== 'KEYWORD') return;
    const keyword = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
    if (!keyword || !(keyword in OPTIONAL_KEYWORDS)) return;
    const kind = keyword as OptionalCastCostOption['kind'];
    const costs = normalizeCostEntries(node?.data);
    const costLabel = formatCostsLabel(costs);
    const costTag = buildCostTag(costs);
    const tag = costTag ? `${kind}:${costTag}` : kind;
    options.push({
      tag,
      label: OPTIONAL_KEYWORDS[kind].label(costLabel),
      costs,
      kind,
      repeatable: OPTIONAL_KEYWORDS[kind].repeatable,
    });
  });
  return options;
};

export const deriveAdditionalCostsFromGraph = (graph?: any): CostEntry[] => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  const costs: CostEntry[] = [];
  graph.nodes.forEach((node: any) => {
    if (node?.type !== 'KEYWORD') return;
    const keyword = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
    if (!['additional cost', 'additional_cost', 'additional'].includes(keyword)) return;
    costs.push(...normalizeCostEntries(node?.data));
  });
  return costs;
};

export const deriveAlternativeCastCostsFromGraph = (graph?: any): AlternativeCostOption[] => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  const options: AlternativeCostOption[] = [];
  graph.nodes.forEach((node: any) => {
    if (node?.type !== 'KEYWORD') return;
    const keyword = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
  const costText = typeof node?.data?.cost === 'string' ? node.data.cost.trim() : findManaCost(node?.data);
    if (keyword === 'flashback' && costText) {
      options.push({ tag: `flashback:${costText}`, label: `Flashback ${costText}` });
    }
    if (keyword === 'overload' && costText) {
      options.push({ tag: `overload:${costText}`, label: `Overload ${costText}` });
    }
    if (keyword === 'escape' && costText) {
      options.push({ tag: `escape:${costText}`, label: `Escape ${costText}` });
    }
    if (
      ['alternative cost', 'alternative_cost', 'alternate cost', 'alternate_cost', 'alternate'].includes(keyword) &&
      costText
    ) {
      options.push({ tag: costText, label: `Cast for ${costText}` });
    }
    if (keyword === 'jump-start') {
      options.push({ tag: 'jump-start', label: 'Jump-start' });
    }
    if (keyword === 'free' || keyword === 'free-cast' || keyword === 'free_cast') {
      options.push({ tag: 'free', label: 'Cast without paying its mana cost' });
    }
  });
  return options;
};

export const deriveAlternativeExtraCostsFromGraph = (graph: any, tag: string | null): CostEntry[] => {
  if (!graph || !tag || !Array.isArray(graph.nodes)) return [];
  const [keywordBase] = tag.split(':');
  if (keywordBase === 'jump-start') {
    return [{ type: 'discard', amount: 1 }];
  }
  if (keywordBase === 'escape') {
    const node = findKeywordNode(graph, 'escape');
    if (!node) return [];
    const amount = typeof node?.data?.number === 'number' ? node.data.number : null;
    if (amount && amount > 0) {
      return [{ type: 'exile_graveyard', amount, other: true }];
    }
  }
  const node = findKeywordNode(graph, keywordBase);
  if (!node) return [];
  const extra = node?.data?.extraCosts ?? node?.data?.extra_costs ?? [];
  if (Array.isArray(extra)) {
    return extra.filter((entry) => entry && typeof entry === 'object');
  }
  return [];
};

export const deriveSpliceCardsFromHand = (
  hand: string[],
  cardGraphs: Record<string, any> | undefined
): Array<{ cardId: string; costs: CostEntry[] }> => {
  if (!hand.length || !cardGraphs) return [];
  const results: Array<{ cardId: string; costs: CostEntry[] }> = [];
  hand.forEach((cardId) => {
    const graph = cardGraphs[cardId];
    if (!graph || !Array.isArray(graph.nodes)) return;
    const spliceNode = graph.nodes.find((node: any) => {
      if (node?.type !== 'KEYWORD') return false;
      const keyword = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
      return keyword === 'splice';
    });
    if (!spliceNode) return;
    const costs = normalizeCostEntries(spliceNode?.data);
    if (!costs.length) return;
    results.push({ cardId, costs });
  });
  return results;
};

export const deriveWardCostsFromGraphs = (graphs?: any[]): CostEntry[] => {
  if (!graphs || graphs.length === 0) return [];
  const costs: CostEntry[] = [];
  graphs.forEach((graph) => {
    if (!graph || !Array.isArray(graph.nodes)) return;
    graph.nodes.forEach((node: any) => {
      if (node?.type !== 'KEYWORD') return;
      const keyword = typeof node?.data?.keyword === 'string' ? node.data.keyword.trim().toLowerCase() : '';
      if (keyword !== 'ward') return;
      costs.push(...normalizeCostEntries(node?.data));
    });
  });
  return costs;
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

