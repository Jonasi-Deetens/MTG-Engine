'use client';

import { CostEntry } from '@/lib/activationCosts';
import { Button } from '@/components/ui/Button';

const COST_TYPES: Array<{ value: CostEntry['type']; label: string }> = [
  { value: 'mana', label: 'Mana' },
  { value: 'tap_self', label: 'Tap this' },
  { value: 'life', label: 'Pay life' },
  { value: 'discard', label: 'Discard cards' },
  { value: 'sacrifice', label: 'Sacrifice permanent' },
  { value: 'sacrifice_self', label: 'Sacrifice this' },
  { value: 'tap', label: 'Tap permanent' },
  { value: 'exile_graveyard', label: 'Exile from graveyard' },
];

const buildDefaultCost = (type: CostEntry['type']): CostEntry => {
  if (type === 'mana') return { type, cost: '{1}' };
  if (type === 'life') return { type, amount: 1 };
  if (type === 'discard') return { type, amount: 1 };
  if (type === 'sacrifice') return { type };
  if (type === 'tap') return { type };
  if (type === 'exile_graveyard') return { type, amount: 1, other: false };
  return { type };
};

interface CostListEditorProps {
  label?: string;
  value: CostEntry[];
  onChange: (value: CostEntry[]) => void;
}

export function CostListEditor({ label = 'Costs', value, onChange }: CostListEditorProps) {
  const updateCost = (index: number, next: CostEntry) => {
    const updated = [...value];
    updated[index] = next;
    onChange(updated);
  };

  const handleTypeChange = (index: number, type: CostEntry['type']) => {
    updateCost(index, buildDefaultCost(type));
  };

  const handleRemove = (index: number) => {
    const updated = value.filter((_, i) => i !== index);
    onChange(updated);
  };

  return (
    <div className="space-y-3">
      <div className="text-sm font-medium text-[color:var(--theme-text-secondary)]">{label}</div>
      {value.map((cost, index) => (
        <div key={`cost-${index}`} className="grid grid-cols-1 gap-2 rounded border border-[color:var(--theme-border-default)] p-3">
          <div className="flex items-center gap-2">
            <select
              value={cost.type}
              onChange={(e) => handleTypeChange(index, e.target.value as CostEntry['type'])}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {COST_TYPES.map((entry) => (
                <option key={entry.value} value={entry.value}>
                  {entry.label}
                </option>
              ))}
            </select>
            <Button variant="ghost" onClick={() => handleRemove(index)} className="text-xs">
              Remove
            </Button>
          </div>

          {cost.type === 'mana' && (
            <input
              type="text"
              value={cost.cost}
              onChange={(e) => updateCost(index, { ...cost, cost: e.target.value })}
              placeholder="{1}{R}"
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          )}
          {(cost.type === 'life' || cost.type === 'discard' || cost.type === 'exile_graveyard') && (
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={1}
                value={cost.amount}
                onChange={(e) => updateCost(index, { ...cost, amount: Math.max(1, Number(e.target.value) || 1) })}
                className="w-24 px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
              {cost.type === 'exile_graveyard' && (
                <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                  <input
                    type="checkbox"
                    checked={!!cost.other}
                    onChange={(e) => updateCost(index, { ...cost, other: e.target.checked })}
                  />
                  Must be other cards
                </label>
              )}
            </div>
          )}
          {(cost.type === 'sacrifice' || cost.type === 'tap') && (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={cost.card_type ?? ''}
                onChange={(e) => updateCost(index, { ...cost, card_type: e.target.value || undefined })}
                placeholder="Creature, Artifact, etc."
                className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              />
              <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                <input
                  type="checkbox"
                  checked={!!cost.nonland}
                  onChange={(e) => updateCost(index, { ...cost, nonland: e.target.checked })}
                />
                Nonland
              </label>
            </div>
          )}
        </div>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange([...value, buildDefaultCost('mana')])}
        className="text-xs"
      >
        Add Cost
      </Button>
    </div>
  );
}

