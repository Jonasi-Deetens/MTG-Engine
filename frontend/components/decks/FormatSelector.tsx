'use client';

// frontend/components/decks/FormatSelector.tsx

interface FormatSelectorProps {
  value: string;
  onChange: (format: string) => void;
  disabled?: boolean;
}

const FORMATS = [
  { value: 'Commander', label: 'Commander', description: '100 cards + 1-2 commanders, singleton' },
  { value: 'Standard', label: 'Standard', description: '60+ cards, max 4 copies' },
  { value: 'Modern', label: 'Modern', description: '60+ cards, max 4 copies' },
  { value: 'Pauper', label: 'Pauper', description: '60+ cards, commons only' },
  { value: 'Legacy', label: 'Legacy', description: '60+ cards, max 4 copies' },
  { value: 'Vintage', label: 'Vintage', description: '60+ cards, max 4 copies' },
];

export function FormatSelector({ value, onChange, disabled = false }: FormatSelectorProps) {
  return (
    <div>
      <label className="block text-xs font-medium text-[color:var(--theme-text-secondary)] mb-1">
        Format
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none disabled:opacity-50"
      >
        {FORMATS.map((format) => (
          <option key={format.value} value={format.value}>
            {format.label}
          </option>
        ))}
      </select>
    </div>
  );
}

