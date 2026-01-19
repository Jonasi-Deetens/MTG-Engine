'use client';

import { Card } from '@/components/ui/Card';
import { ReplacementConflictEntry } from '@/hooks/useReplacementConflicts';
import { useEffect } from 'react';

interface ReplacementChoicePanelProps {
  conflicts: ReplacementConflictEntry[];
  replacementChoices: Record<string, string>;
  onSelectChoice: (key: string, value: string) => void;
  highlightKey?: string | null;
  onNextHighlight?: () => void;
}

export function ReplacementChoicePanel({
  conflicts,
  replacementChoices,
  onSelectChoice,
  highlightKey,
  onNextHighlight,
}: ReplacementChoicePanelProps) {
  const unresolved = conflicts.filter((entry) => !replacementChoices[entry.key]);
  if (unresolved.length === 0) return null;

  useEffect(() => {
    if (!highlightKey) return;
    const el = document.getElementById(`replacement-conflict-${highlightKey}`);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, [highlightKey]);

  return (
    <Card variant="bordered" className="p-4 space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
          Replacement Choice Needed
        </div>
        {onNextHighlight && unresolved.length > 1 && (
          <button
            type="button"
            onClick={onNextHighlight}
            className="text-xs text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]"
          >
            Next unresolved
          </button>
        )}
      </div>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">
        Multiple replacement or prevention effects apply. Choose the one to apply first.
      </div>
      <div className="space-y-2">
        {unresolved.map((entry) => (
          <div
            key={entry.key}
            id={`replacement-conflict-${entry.key}`}
            className={`flex flex-wrap items-center gap-2 rounded ${
              highlightKey === entry.key ? 'ring-1 ring-[color:var(--theme-border-focus)]' : ''
            }`}
          >
            <div className="text-xs text-[color:var(--theme-text-secondary)]">
              {entry.label}
            </div>
            <select
              value={replacementChoices[entry.key] || ''}
              onChange={(e) => onSelectChoice(entry.key, e.target.value)}
              className="px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none text-xs"
            >
              <option value="">Auto (most recent)</option>
              {entry.options.map((effect) => (
                <option key={effect.effect_id} value={effect.effect_id}>
                  {effect.label || effect.replacement_zone || 'Replacement'}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </Card>
  );
}

