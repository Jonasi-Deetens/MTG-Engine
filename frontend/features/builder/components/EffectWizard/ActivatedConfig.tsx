import type { UnifiedEffect } from '@/lib/unifiedEffect';

interface ActivatedConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

const COST_TYPES = ['tap_self', 'mana', 'sacrifice', 'discard'];

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
        <select
          className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
          value={item.type}
          onChange={(e) => updateItem({ type: e.target.value })}
        >
          {COST_TYPES.map((type) => (
            <option key={type} value={type}>
              {type.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      {item.type === 'mana' && (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-[color:var(--theme-text-secondary)] uppercase tracking-wide">
              Mana Type
            </label>
            <input
              className="mt-1 w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-sm"
              placeholder="W, U, B, R, G, C"
              value={item.manaType ?? ''}
              onChange={(e) => updateItem({ manaType: e.target.value })}
            />
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
