// frontend/components/search/SearchFilters.tsx

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { COLORS, COLOR_NAMES, RARITY_OPTIONS, LANGUAGE_OPTIONS, CARD_TYPE_OPTIONS } from '@/lib/constants/search';

interface SearchFiltersProps {
  selectedColors: string[];
  typeFilters: string[];
  setFilter: string;
  rarityFilter: string;
  languageFilter: string;
  keywordFilter: string;
  showFilters: boolean;
  hasActiveFilters: boolean;
  onToggleFilters: () => void;
  onToggleColor: (color: string) => void;
  onToggleType: (value: string) => void;
  onSetFilterChange: (value: string) => void;
  onRarityFilterChange: (value: string) => void;
  onLanguageFilterChange: (value: string) => void;
  onKeywordFilterChange: (value: string) => void;
  onClearFilters: () => void;
  isBrowseMode: boolean;
}

export function SearchFilters({
  selectedColors,
  typeFilters,
  setFilter,
  rarityFilter,
  languageFilter,
  keywordFilter,
  showFilters,
  hasActiveFilters,
  onToggleFilters,
  onToggleColor,
  onToggleType,
  onSetFilterChange,
  onRarityFilterChange,
  onLanguageFilterChange,
  onKeywordFilterChange,
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

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Card Types
              </label>
              <div className="flex flex-wrap gap-2">
                {CARD_TYPE_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => onToggleType(option.value)}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors cursor-pointer ${
                      typeFilters.includes(option.value)
                        ? 'bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)]'
                        : 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)] border border-[color:var(--theme-card-border)]'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
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
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Rarity
              </label>
              <select
                value={rarityFilter}
                onChange={(e) => onRarityFilterChange(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-[color:var(--theme-card-border)] bg-[color:var(--theme-card-bg)] text-[color:var(--theme-text-primary)] focus:outline-none focus:ring-2 focus:ring-[color:var(--theme-accent-primary)]"
              >
                {RARITY_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Language
              </label>
              <select
                value={languageFilter}
                onChange={(e) => onLanguageFilterChange(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-[color:var(--theme-card-border)] bg-[color:var(--theme-card-bg)] text-[color:var(--theme-text-primary)] focus:outline-none focus:ring-2 focus:ring-[color:var(--theme-accent-primary)]"
              >
                {LANGUAGE_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
                Keyword
              </label>
              <Input
                type="text"
                placeholder="e.g., Flying, Trample"
                value={keywordFilter}
                onChange={(e) => onKeywordFilterChange(e.target.value)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

