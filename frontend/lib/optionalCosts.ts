import { CostEntry, buildActivationCosts, formatActivationCostLabel } from './activationCosts';
import { serializeManaCostSymbols } from './wardCosts';

export type OptionalCostKind =
  | 'kicker'
  | 'multikicker'
  | 'buyback'
  | 'entwine'
  | 'replicate'
  | 'conspire';

export type OptionalCostEntry = {
  kind: OptionalCostKind;
  costs: CostEntry[];
  repeatable?: boolean;
  tag?: string;
};

export const OPTIONAL_COST_KIND_OPTIONS: Array<{
  value: OptionalCostKind;
  label: string;
  repeatable: boolean;
}> = [
  { value: 'kicker', label: 'Kicker', repeatable: false },
  { value: 'multikicker', label: 'Multikicker', repeatable: true },
  { value: 'buyback', label: 'Buyback', repeatable: false },
  { value: 'entwine', label: 'Entwine', repeatable: false },
  { value: 'replicate', label: 'Replicate', repeatable: true },
  { value: 'conspire', label: 'Conspire', repeatable: false },
];

const OPTIONAL_KEYWORDS: Record<
  OptionalCostKind,
  { repeatable: boolean; label: (costText: string) => string }
> = {
  kicker: { repeatable: false, label: (costText) => `Kicker ${costText}` },
  multikicker: { repeatable: true, label: (costText) => `Multikicker ${costText}` },
  buyback: { repeatable: false, label: (costText) => `Buyback ${costText}` },
  entwine: { repeatable: false, label: (costText) => `Entwine ${costText}` },
  replicate: { repeatable: true, label: (costText) => `Replicate ${costText}` },
  conspire: { repeatable: false, label: () => 'Conspire' },
};

const formatCostsLabel = (costs: CostEntry[]) => {
  if (!costs.length) return '';
  return buildActivationCosts(costs).map(formatActivationCostLabel).join(', ');
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
      return 'cost';
    })
    .join('+');
};

export const normalizeOptionalCostEntry = (entry: OptionalCostEntry): OptionalCostEntry => {
  const kind = entry.kind;
  const costs = Array.isArray(entry.costs) ? entry.costs : [];
  const meta = OPTIONAL_KEYWORDS[kind];
  const repeatable = entry.repeatable ?? meta.repeatable;
  const tag = entry.tag || (() => {
    const costTag = buildCostTag(costs);
    return costTag ? `${kind}:${costTag}` : kind;
  })();
  return { ...entry, kind, costs, repeatable, tag };
};

export const formatOptionalCostLabel = (entry: OptionalCostEntry) => {
  const normalized = normalizeOptionalCostEntry(entry);
  const costText = formatCostsLabel(normalized.costs);
  return OPTIONAL_KEYWORDS[normalized.kind].label(costText).trim();
};
