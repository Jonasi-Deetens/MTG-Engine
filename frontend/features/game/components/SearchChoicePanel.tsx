'use client';

import { useEffect } from 'react';
import { EngineCardMap } from '@/lib/engine';

type SearchChoiceEntry = {
  id: string;
  label: string;
  zone: string;
  candidates: Array<{ id: string; label: string }>;
  selectedIds: string[];
  maxSelections?: number | null;
  orderRequired?: boolean;
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
      {entries.map((entry) => (
        <SearchChoiceEntryView key={entry.id} entry={entry} cardMap={cardMap} />
      ))}
    </div>
  );
}

function SearchChoiceEntryView({ entry, cardMap }: { entry: SearchChoiceEntry; cardMap: EngineCardMap }) {
  const orderedIds = entry.selectedIds.length
    ? entry.selectedIds
    : entry.candidates.map((candidate) => candidate.id);

  useEffect(() => {
    if (entry.orderRequired && entry.selectedIds.length === 0 && orderedIds.length > 0) {
      entry.onChange(orderedIds);
    }
  }, [entry, orderedIds]);

  const countLabel =
    entry.maxSelections && entry.maxSelections > 0
      ? `${entry.selectedIds.length}/${entry.maxSelections} selected`
      : `${entry.selectedIds.length} selected`;

  const moveItem = (index: number, direction: -1 | 1) => {
    const next = [...orderedIds];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= next.length) return;
    const [item] = next.splice(index, 1);
    next.splice(targetIndex, 0, item);
    entry.onChange(next);
  };

  return (
    <div className="space-y-2 rounded border border-[color:var(--theme-input-border)] p-2">
      <div className="text-xs text-[color:var(--theme-text-secondary)]">{entry.label}</div>
      <div className="text-xs text-[color:var(--theme-text-muted)]">Zone: {entry.zone}</div>
      {!entry.orderRequired && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">{countLabel}</div>
      )}
      <div className="space-y-1 max-h-40 overflow-auto pr-1">
        {entry.candidates.length === 0 && (
          <div className="text-xs text-[color:var(--theme-text-secondary)]">No cards available</div>
        )}
        {entry.orderRequired
          ? orderedIds.map((cardId, index) => {
              const label =
                cardMap[cardId]?.name || entry.candidates.find((c) => c.id === cardId)?.label || cardId;
              return (
                <div key={`${entry.id}-${cardId}`} className="flex items-center gap-2 text-sm">
                  <span className="text-[color:var(--theme-text-secondary)] flex-1">{label}</span>
                  <button
                    type="button"
                    className="px-2 py-1 text-xs rounded border border-[color:var(--theme-input-border)]"
                    onClick={() => moveItem(index, -1)}
                    disabled={index === 0}
                  >
                    Up
                  </button>
                  <button
                    type="button"
                    className="px-2 py-1 text-xs rounded border border-[color:var(--theme-input-border)]"
                    onClick={() => moveItem(index, 1)}
                    disabled={index === orderedIds.length - 1}
                  >
                    Down
                  </button>
                </div>
              );
            })
          : entry.candidates.map((candidate) => {
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
}

