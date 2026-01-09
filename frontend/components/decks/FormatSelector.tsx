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
    <div className="space-y-2">
      <label className="block text-sm font-medium text-slate-700">
        Format
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full px-3 py-2 bg-white text-slate-900 rounded border border-amber-200/50 focus:border-amber-500 focus:outline-none disabled:opacity-50"
      >
        {FORMATS.map((format) => (
          <option key={format.value} value={format.value}>
            {format.label}
          </option>
        ))}
      </select>
      {FORMATS.find(f => f.value === value) && (
        <p className="text-xs text-slate-600">
          {FORMATS.find(f => f.value === value)?.description}
        </p>
      )}
    </div>
  );
}

