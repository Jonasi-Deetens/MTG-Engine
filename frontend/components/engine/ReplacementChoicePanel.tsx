'use client';

import { Card } from '@/components/ui/Card';
import { EngineCardMap } from '@/lib/engine';

interface ReplacementConflictEntry {
  obj: any;
  key: string;
  fromLabel: string;
  toLabel: string;
  options: Array<Record<string, any>>;
}

interface ReplacementChoicePanelProps {
  conflicts: ReplacementConflictEntry[];
  replacementChoices: Record<string, string>;
  cardMap: EngineCardMap;
  onSelectChoice: (key: string, value: string) => void;
}

export function ReplacementChoicePanel({
  conflicts,
  replacementChoices,
  cardMap,
  onSelectChoice,
}: ReplacementChoicePanelProps) {
  const unresolved = conflicts.filter((entry) => !replacementChoices[entry.key]);
  if (unresolved.length === 0) return null;

  return (
    <Card variant="bordered" className="p-4 space-y-3">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
        Replacement Choice Needed
      </div>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">
        A zone change has multiple applicable replacements. Choose the one to apply before it happens.
      </div>
      <div className="space-y-2">
        {unresolved.map((entry) => (
          <div key={entry.key} className="flex flex-wrap items-center gap-2">
            <div className="text-xs text-[color:var(--theme-text-secondary)]">
              {cardMap[entry.obj.id]?.name || entry.obj.name || entry.obj.id}
              <span className="ml-1 text-[color:var(--theme-text-muted)]">
                ({entry.fromLabel} → {entry.toLabel})
              </span>
            </div>
            <select
              value={replacementChoices[entry.key] || ''}
              onChange={(e) => onSelectChoice(entry.key, e.target.value)}
              className="px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none text-xs"
            >
              <option value="">Auto (most recent)</option>
              {entry.options.map((effect) => (
                <option key={effect.effect_id} value={effect.effect_id}>
                  {effect.replacement_zone}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </Card>
  );
}

