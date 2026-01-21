'use client';

import { buildActivationCosts, formatActivationCostLabel } from '@/lib/activationCosts';

interface SpliceOption {
  cardId: string;
  label: string;
  costs: Array<{ type: string; [key: string]: any }>;
}

interface SplicePanelProps {
  options: SpliceOption[];
  selections: string[];
  onToggle: (cardId: string) => void;
}

export function SplicePanel({ options, selections, onToggle }: SplicePanelProps) {
  if (options.length === 0) return null;
  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Splice</div>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">
        Choose cards with splice in hand. Their effects will be added to the spell.
      </div>
      {options.map((option) => {
        const selected = selections.includes(option.cardId);
        const costLabel = buildActivationCosts(option.costs as any).map(formatActivationCostLabel).join(', ');
        return (
          <label key={option.cardId} className="flex items-center gap-2 text-xs">
            <input type="checkbox" checked={selected} onChange={() => onToggle(option.cardId)} />
            <span className="text-[color:var(--theme-text-secondary)]">
              {option.label} — {costLabel}
            </span>
          </label>
        );
      })}
    </div>
  );
}

