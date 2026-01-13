// frontend/components/search/SearchFilters.tsx

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { COLORS, COLOR_NAMES } from '@/lib/constants/search';

interface SearchFiltersProps {
  selectedColors: string[];
  typeFilter: string;
  setFilter: string;
  showFilters: boolean;
  hasActiveFilters: boolean;
  onToggleFilters: () => void;
  onToggleColor: (color: string) => void;
  onTypeFilterChange: (value: string) => void;
  onSetFilterChange: (value: string) => void;
  onClearFilters: () => void;
  isBrowseMode: boolean;
}

export function SearchFilters({
  selectedColors,
  typeFilter,
  setFilter,
  showFilters,
  hasActiveFilters,
  onToggleFilters,
  onToggleColor,
  onTypeFilterChange,
  onSetFilterChange,
  onClearFilters,
  isBrowseMode,
}: SearchFiltersProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Button
          onClick={onToggleFilters}
          variant="outline"
          size="sm"
        >
          {showFilters ? 'Hide' : 'Show'} Filters
        </Button>
        {hasActiveFilters && (
          <Button
            onClick={onClearFilters}
            variant="outline"
            size="sm"
          >
            Clear Filters
          </Button>
        )}
      </div>

      {showFilters && (
        <div className="bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              Colors
            </label>
            <div className="flex flex-wrap gap-2">
              {COLORS.map(color => (
                <button
                  key={color}
                  onClick={() => onToggleColor(color)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors cursor-pointer ${
                    selectedColors.includes(color)
                      ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                      : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
                  }`}
                >
                  {COLOR_NAMES[color]}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              Type (contains)
            </label>
            <Input
              type="text"
              placeholder="e.g., Creature, Instant, Artifact"
              value={typeFilter}
              onChange={(e) => onTypeFilterChange(e.target.value)}
              className="max-w-xs"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              Set Code
            </label>
            <Input
              type="text"
              placeholder="e.g., M21, CMR"
              value={setFilter}
              onChange={(e) => onSetFilterChange(e.target.value.toUpperCase())}
              className="max-w-xs"
            />
          </div>
        </div>
      )}
    </div>
  );
}

