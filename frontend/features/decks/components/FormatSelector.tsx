'use client';

// frontend/components/decks/FormatSelector.tsx

import { Select } from '@/components/ui/Select';

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
      <Select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        className="w-full"
      >
        {FORMATS.map((format) => (
          <option key={format.value} value={format.value}>
            {format.label}
          </option>
        ))}
      </Select>
    </div>
  );
}

