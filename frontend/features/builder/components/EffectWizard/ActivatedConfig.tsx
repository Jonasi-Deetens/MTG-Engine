import type { UnifiedEffect } from '@/lib/unifiedEffect';
import { MANA_TYPE_OPTIONS } from '@/lib/effectTypes';
import { Select } from '@/components/ui/Select';

interface ActivatedConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

const COST_TYPES = [
  { value: 'tap_self', label: 'Tap This' },
  { value: 'mana', label: 'Mana' },
  { value: 'sacrifice', label: 'Sacrifice' },
  { value: 'discard', label: 'Discard' },
  { value: 'life', label: 'Pay Life' },
  { value: 'exile_graveyard', label: 'Exile From Graveyard' },
];

export function ActivatedConfig({ effect, onChange }: ActivatedConfigProps) {
  const cost = effect.cost ?? { items: [{ type: 'tap_self' }] };
  const [item] = cost.items;

  const updateItem = (updates: Record<string, unknown>) => {
    const updated = { ...item, ...updates };
    onChange({ ...effect, cost: { ...cost, items: [updated] } });
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
          Cost Type
        </label>
        <Select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={item.type}
          onChange={(e) => updateItem({ type: e.target.value })}
        >
          {COST_TYPES.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </Select>
      </div>

      {item.type === 'mana' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Mana Type
            </label>
            <Select
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              value={item.manaType ?? 'C'}
              onChange={(e) => updateItem({ manaType: e.target.value })}
            >
              {MANA_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Amount
            </label>
            <input
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              type="number"
              value={item.amount ?? 1}
              onChange={(e) => updateItem({ amount: Number(e.target.value) })}
            />
          </div>
        </div>
      )}
    </div>
  );
}
