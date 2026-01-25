'use client';

import { Button } from '@/components/ui/Button';
import type { CostEntry } from '@/lib/activationCosts';
import type { OptionalCostEntry, OptionalCostKind } from '@/lib/optionalCosts';
import { OPTIONAL_COST_KIND_OPTIONS } from '@/lib/optionalCosts';
import { CostListEditor } from '@/features/builder/components/CostListEditor';

interface OptionalCostListEditorProps {
  value: OptionalCostEntry[];
  onChange: (value: OptionalCostEntry[]) => void;
}

const buildDefaultOptionalCost = (kind: OptionalCostKind): OptionalCostEntry => ({
  kind,
  costs: [],
  repeatable: OPTIONAL_COST_KIND_OPTIONS.find((entry) => entry.value === kind)?.repeatable ?? false,
});

export function OptionalCostListEditor({ value, onChange }: OptionalCostListEditorProps) {
  const updateEntry = (index: number, next: OptionalCostEntry) => {
    const updated = [...value];
    updated[index] = next;
    onChange(updated);
  };

  const handleRemove = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const handleKindChange = (index: number, kind: OptionalCostKind) => {
    const current = value[index];
    updateEntry(index, {
      ...current,
      kind,
      repeatable: OPTIONAL_COST_KIND_OPTIONS.find((entry) => entry.value === kind)?.repeatable ?? false,
    });
  };

  return (
    <div className="space-y-3">
      {value.map((entry, index) => (
        <div key={`optional-cost-${index}`} className="space-y-2 rounded border border-[color:var(--theme-border-default)] p-3">
          <div className="flex items-center gap-2">
            <select
              value={entry.kind}
              onChange={(e) => handleKindChange(index, e.target.value as OptionalCostKind)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {OPTIONAL_COST_KIND_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <Button variant="ghost" onClick={() => handleRemove(index)} className="text-xs">
              Remove
            </Button>
          </div>
          <div className="text-xs text-[color:var(--theme-text-muted)]">
            Repeatable: {entry.repeatable ? 'Yes' : 'No'}
          </div>
          <CostListEditor
            label="Costs"
            value={Array.isArray(entry.costs) ? (entry.costs as CostEntry[]) : []}
            onChange={(nextCosts) => updateEntry(index, { ...entry, costs: nextCosts })}
          />
        </div>
      ))}
      <Button
        variant="outline"
        onClick={() => onChange([...value, buildDefaultOptionalCost('kicker')])}
        className="text-xs"
      >
        Add Optional Cost
      </Button>
    </div>
  );
}
