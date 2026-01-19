'use client';

import { OptionalCastCostOption } from '@/lib/graphCosts';

interface OptionalCostPanelProps {
  options: OptionalCastCostOption[];
  selections: Record<string, number>;
  errors: string[];
  onToggle: (tag: string) => void;
  onChangeCount: (tag: string, count: number) => void;
}

export function OptionalCostPanel({
  options,
  selections,
  errors,
  onToggle,
  onChangeCount,
}: OptionalCostPanelProps) {
  if (options.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Optional Costs</div>
      {options.map((option) => {
        const count = selections[option.tag] ?? 0;
        const isSelected = count > 0;
        return (
          <div key={option.tag} className="flex items-center gap-3 text-xs">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggle(option.tag)}
              />
              <span className="text-[color:var(--theme-text-secondary)]">{option.label}</span>
            </label>
            {option.repeatable && (
              <label className="flex items-center gap-2">
                <span className="text-[color:var(--theme-text-secondary)]">Times</span>
                <input
                  type="number"
                  min={isSelected ? 1 : 0}
                  value={count}
                  onChange={(e) => onChangeCount(option.tag, parseInt(e.target.value, 10) || 0)}
                  className="w-16 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  disabled={!isSelected}
                />
              </label>
            )}
          </div>
        );
      })}
      {errors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">{errors.join(' ')}</div>
      )}
    </div>
  );
}

