'use client';

interface ConspirePanelProps {
  enabled: boolean;
  options: Array<{ value: string; label: string }>;
  selections: string[];
  onToggle: (value: string) => void;
  error?: string | null;
}

export function ConspirePanel({
  enabled,
  options,
  selections,
  onToggle,
  error,
}: ConspirePanelProps) {
  if (!enabled) return null;
  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Conspire</div>
      <div className="text-xs text-[color:var(--theme-text-secondary)]">
        Tap two creatures you control that share a color with the spell.
      </div>
      {options.length === 0 && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">No eligible creatures.</div>
      )}
      {options.map((option) => {
        const selected = selections.includes(option.value);
        return (
          <label key={option.value} className="flex items-center gap-2 text-xs">
            <input
              type="checkbox"
              checked={selected}
              onChange={() => onToggle(option.value)}
              disabled={!selected && selections.length >= 2}
            />
            <span className="text-[color:var(--theme-text-secondary)]">{option.label}</span>
          </label>
        );
      })}
      {error && <div className="text-xs text-[color:var(--theme-status-error)]">{error}</div>}
    </div>
  );
}

