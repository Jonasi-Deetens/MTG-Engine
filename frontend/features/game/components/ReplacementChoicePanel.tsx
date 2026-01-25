'use client';

import { ReplacementConflictEntry } from '../hooks/useReplacementConflicts';
import { useEffect } from 'react';
import { BracketHeader } from '@/components/ui/play/NierUIElements';
import { StylizedButton } from '@/components/ui/play/StylizedButton';
import { StylizedNativeSelect } from '@/components/ui/play/StylizedNativeSelect';

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
    <div className="nier-panel space-y-3">
      <div className="flex items-center justify-between gap-3">
        <BracketHeader>Replacement Choice Needed</BracketHeader>
        {onNextHighlight && unresolved.length > 1 && (
          <StylizedButton type="button" variant="ghost" onClick={onNextHighlight}>
            Next unresolved
          </StylizedButton>
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
            <StylizedNativeSelect
              value={replacementChoices[entry.key] || ''}
              onChange={(e) => onSelectChoice(entry.key, e.target.value)}
            >
              <option value="">Auto (most recent)</option>
              {entry.options.map((effect) => (
                <option key={effect.effect_id} value={effect.effect_id}>
                  {effect.label || effect.replacement_zone || 'Replacement'}
                </option>
              ))}
            </StylizedNativeSelect>
          </div>
        ))}
      </div>
    </div>
  );
}

