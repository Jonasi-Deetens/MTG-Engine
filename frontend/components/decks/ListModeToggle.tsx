'use client';

// frontend/components/decks/ListModeToggle.tsx

interface ListModeToggleProps {
  mode: 'standard' | 'custom';
  onChange: (mode: 'standard' | 'custom') => void;
}

export function ListModeToggle({ mode, onChange }: ListModeToggleProps) {
  return (
    <div className="flex items-center gap-2 p-1 bg-[color:var(--theme-bg-secondary)] rounded-lg">
      <button
        onClick={() => onChange('standard')}
        className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
          mode === 'standard'
            ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
            : 'text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]'
        }`}
      >
        Standard
      </button>
      <button
        onClick={() => onChange('custom')}
        className={`px-3 py-1.5 text-xs font-medium rounded transition-colors ${
          mode === 'custom'
            ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
            : 'text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]'
        }`}
      >
        Custom
      </button>
    </div>
  );
}

