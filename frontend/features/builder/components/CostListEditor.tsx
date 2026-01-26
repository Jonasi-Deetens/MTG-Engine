'use client';

import { CostEntry } from '@/lib/activationCosts';
import { ManaCostData } from '@/lib/wardCosts';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';

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
  if (type === 'mana') {
    return {
      type,
      cost: {
        generic: 1,
        colored: { W: 0, U: 0, B: 0, R: 0, G: 0 },
        hybrids: [],
        two_brids: [],
        phyrexian: [],
        colorless: 0,
        x: 0,
      },
    };
  }
  if (type === 'life') return { type, amount: 1 };
  if (type === 'discard') return { type, amount: 1 };
  if (type === 'sacrifice') return { type };
  if (type === 'tap') return { type };
  if (type === 'exile_graveyard') return { type, amount: 1, other: false };
  return { type };
};

const COLOR_OPTIONS = ['W', 'U', 'B', 'R', 'G'];

const normalizeManaCost = (cost: ManaCostData): ManaCostData => ({
  generic: Number(cost.generic || 0),
  colored: {
    W: Number(cost.colored?.W || 0),
    U: Number(cost.colored?.U || 0),
    B: Number(cost.colored?.B || 0),
    R: Number(cost.colored?.R || 0),
    G: Number(cost.colored?.G || 0),
  },
  hybrids: Array.isArray(cost.hybrids) ? cost.hybrids : [],
  two_brids: Array.isArray(cost.two_brids) ? cost.two_brids : [],
  phyrexian: Array.isArray(cost.phyrexian) ? cost.phyrexian : [],
  colorless: Number(cost.colorless || 0),
  x: Number(cost.x || 0),
});

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
            <Select
              value={cost.type}
              onChange={(e) => handleTypeChange(index, e.target.value as CostEntry['type'])}
              className="w-full"
            >
              {COST_TYPES.map((entry) => (
                <option key={entry.value} value={entry.value}>
                  {entry.label}
                </option>
              ))}
            </Select>
            <Button variant="ghost" onClick={() => handleRemove(index)} className="text-xs">
              Remove
            </Button>
          </div>

          {cost.type === 'mana' && (
            <div className="space-y-2">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                <label className="text-xs text-[color:var(--theme-text-secondary)]">
                  Generic
                  <input
                    type="number"
                    min={0}
                    value={normalizeManaCost(cost.cost).generic}
                    onChange={(e) =>
                      updateCost(index, {
                        ...cost,
                        cost: { ...normalizeManaCost(cost.cost), generic: Math.max(0, Number(e.target.value) || 0) },
                      })
                    }
                    className="mt-1 w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                </label>
                <label className="text-xs text-[color:var(--theme-text-secondary)]">
                  Colorless
                  <input
                    type="number"
                    min={0}
                    value={normalizeManaCost(cost.cost).colorless}
                    onChange={(e) =>
                      updateCost(index, {
                        ...cost,
                        cost: { ...normalizeManaCost(cost.cost), colorless: Math.max(0, Number(e.target.value) || 0) },
                      })
                    }
                    className="mt-1 w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                </label>
                <label className="text-xs text-[color:var(--theme-text-secondary)]">
                  X
                  <input
                    type="number"
                    min={0}
                    value={normalizeManaCost(cost.cost).x}
                    onChange={(e) =>
                      updateCost(index, {
                        ...cost,
                        cost: { ...normalizeManaCost(cost.cost), x: Math.max(0, Number(e.target.value) || 0) },
                      })
                    }
                    className="mt-1 w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                </label>
              </div>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
                {COLOR_OPTIONS.map((color) => (
                  <label key={`color-${color}`} className="text-xs text-[color:var(--theme-text-secondary)]">
                    {color}
                    <input
                      type="number"
                      min={0}
                      value={normalizeManaCost(cost.cost).colored[color] ?? 0}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        updateCost(index, {
                          ...cost,
                          cost: {
                            ...normalized,
                            colored: {
                              ...normalized.colored,
                              [color]: Math.max(0, Number(e.target.value) || 0),
                            },
                          },
                        });
                      }}
                      className="mt-1 w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                    />
                  </label>
                ))}
              </div>
              <div className="space-y-1 text-xs text-[color:var(--theme-text-secondary)]">
                <div>Hybrid symbols</div>
                {normalizeManaCost(cost.cost).hybrids.map(([colorA, colorB], hybridIndex) => (
                  <div key={`hybrid-${hybridIndex}`} className="flex items-center gap-2">
                    <Select
                      value={colorA}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        const hybrids = [...normalized.hybrids];
                        hybrids[hybridIndex] = [e.target.value, hybrids[hybridIndex][1]];
                        updateCost(index, { ...cost, cost: { ...normalized, hybrids } });
                      }}
                      className="flex-1"
                    >
                      {COLOR_OPTIONS.map((color) => (
                        <option key={`hybrid-a-${color}`} value={color}>
                          {color}
                        </option>
                      ))}
                    </Select>
                    <Select
                      value={colorB}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        const hybrids = [...normalized.hybrids];
                        hybrids[hybridIndex] = [hybrids[hybridIndex][0], e.target.value];
                        updateCost(index, { ...cost, cost: { ...normalized, hybrids } });
                      }}
                      className="flex-1"
                    >
                      {COLOR_OPTIONS.map((color) => (
                        <option key={`hybrid-b-${color}`} value={color}>
                          {color}
                        </option>
                      ))}
                    </Select>
                    <Button
                      variant="ghost"
                      onClick={() => {
                        const normalized = normalizeManaCost(cost.cost);
                        const hybrids = normalized.hybrids.filter((_, idx) => idx !== hybridIndex);
                        updateCost(index, { ...cost, cost: { ...normalized, hybrids } });
                      }}
                      className="text-xs"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() => {
                    const normalized = normalizeManaCost(cost.cost);
                    updateCost(index, {
                      ...cost,
                      cost: { ...normalized, hybrids: [...normalized.hybrids, ['W', 'U']] },
                    });
                  }}
                  className="text-xs"
                >
                  Add hybrid
                </Button>
              </div>
              <div className="space-y-1 text-xs text-[color:var(--theme-text-secondary)]">
                <div>Two-brid symbols</div>
                {normalizeManaCost(cost.cost).two_brids.map(([genericValue, color], twoBridIndex) => (
                  <div key={`two-brid-${twoBridIndex}`} className="flex items-center gap-2">
                    <input
                      type="number"
                      min={0}
                      value={genericValue}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        const two_brids = [...normalized.two_brids];
                        two_brids[twoBridIndex] = [Math.max(0, Number(e.target.value) || 0), two_brids[twoBridIndex][1]];
                        updateCost(index, { ...cost, cost: { ...normalized, two_brids } });
                      }}
                      className="w-20 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)]"
                    />
                    <Select
                      value={color}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        const two_brids = [...normalized.two_brids];
                        two_brids[twoBridIndex] = [two_brids[twoBridIndex][0], e.target.value];
                        updateCost(index, { ...cost, cost: { ...normalized, two_brids } });
                      }}
                      className="flex-1"
                    >
                      {COLOR_OPTIONS.map((colorOption) => (
                        <option key={`two-brid-${colorOption}`} value={colorOption}>
                          {colorOption}
                        </option>
                      ))}
                    </Select>
                    <Button
                      variant="ghost"
                      onClick={() => {
                        const normalized = normalizeManaCost(cost.cost);
                        const two_brids = normalized.two_brids.filter((_, idx) => idx !== twoBridIndex);
                        updateCost(index, { ...cost, cost: { ...normalized, two_brids } });
                      }}
                      className="text-xs"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() => {
                    const normalized = normalizeManaCost(cost.cost);
                    updateCost(index, {
                      ...cost,
                      cost: { ...normalized, two_brids: [...normalized.two_brids, [2, 'W']] },
                    });
                  }}
                  className="text-xs"
                >
                  Add two-brid
                </Button>
              </div>
              <div className="space-y-1 text-xs text-[color:var(--theme-text-secondary)]">
                <div>Phyrexian symbols</div>
                {normalizeManaCost(cost.cost).phyrexian.map((color, phyIndex) => (
                  <div key={`phyrexian-${phyIndex}`} className="flex items-center gap-2">
                    <Select
                      value={color}
                      onChange={(e) => {
                        const normalized = normalizeManaCost(cost.cost);
                        const phyrexian = [...normalized.phyrexian];
                        phyrexian[phyIndex] = e.target.value;
                        updateCost(index, { ...cost, cost: { ...normalized, phyrexian } });
                      }}
                      className="flex-1"
                    >
                      {COLOR_OPTIONS.map((colorOption) => (
                        <option key={`phyrexian-${colorOption}`} value={colorOption}>
                          {colorOption}
                        </option>
                      ))}
                    </Select>
                    <Button
                      variant="ghost"
                      onClick={() => {
                        const normalized = normalizeManaCost(cost.cost);
                        const phyrexian = normalized.phyrexian.filter((_, idx) => idx !== phyIndex);
                        updateCost(index, { ...cost, cost: { ...normalized, phyrexian } });
                      }}
                      className="text-xs"
                    >
                      Remove
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  onClick={() => {
                    const normalized = normalizeManaCost(cost.cost);
                    updateCost(index, {
                      ...cost,
                      cost: { ...normalized, phyrexian: [...normalized.phyrexian, 'W'] },
                    });
                  }}
                  className="text-xs"
                >
                  Add phyrexian
                </Button>
              </div>
            </div>
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
              <Select
                value={cost.card_type ?? ''}
                onChange={(e) => updateCost(index, { ...cost, card_type: e.target.value || undefined })}
                className="w-full"
              >
                <option value="">Any Permanent</option>
                <option value="creature">Creature</option>
                <option value="artifact">Artifact</option>
                <option value="enchantment">Enchantment</option>
                <option value="land">Land</option>
                <option value="planeswalker">Planeswalker</option>
              </Select>
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

