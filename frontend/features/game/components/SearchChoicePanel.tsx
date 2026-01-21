'use client';

import { EngineCardMap } from '@/lib/engine';

type SearchChoiceEntry = {
  id: string;
  label: string;
  zone: string;
  candidates: Array<{ id: string; label: string }>;
  selectedIds: string[];
  maxSelections?: number | null;
  onChange: (ids: string[]) => void;
};

interface SearchChoicePanelProps {
  entries: SearchChoiceEntry[];
  cardMap: EngineCardMap;
}

export function SearchChoicePanel({ entries, cardMap }: SearchChoicePanelProps) {
  if (!entries.length) return null;

  return (
    <div className="space-y-3">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Search Choices</div>
      {entries.map((entry) => {
        const countLabel =
          entry.maxSelections && entry.maxSelections > 0
            ? `${entry.selectedIds.length}/${entry.maxSelections} selected`
            : `${entry.selectedIds.length} selected`;
        return (
          <div key={entry.id} className="space-y-2 rounded border border-[color:var(--theme-input-border)] p-2">
            <div className="text-xs text-[color:var(--theme-text-secondary)]">{entry.label}</div>
            <div className="text-xs text-[color:var(--theme-text-muted)]">Zone: {entry.zone}</div>
            <div className="text-xs text-[color:var(--theme-text-secondary)]">{countLabel}</div>
            <div className="space-y-1 max-h-40 overflow-auto pr-1">
              {entry.candidates.length === 0 && (
                <div className="text-xs text-[color:var(--theme-text-secondary)]">No cards available</div>
              )}
              {entry.candidates.map((candidate) => {
                const label = cardMap[candidate.id]?.name || candidate.label;
                const checked = entry.selectedIds.includes(candidate.id);
                const disabled =
                  !!entry.maxSelections &&
                  entry.maxSelections > 0 &&
                  !checked &&
                  entry.selectedIds.length >= entry.maxSelections;
                return (
                  <label key={`${entry.id}-${candidate.id}`} className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => {
                        if (checked) {
                          entry.onChange(entry.selectedIds.filter((id) => id !== candidate.id));
                          return;
                        }
                        entry.onChange([...entry.selectedIds, candidate.id]);
                      }}
                      disabled={disabled}
                    />
                    <span className="text-[color:var(--theme-text-secondary)]">{label}</span>
                  </label>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

