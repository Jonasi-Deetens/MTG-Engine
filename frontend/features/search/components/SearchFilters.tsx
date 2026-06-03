// frontend/components/search/SearchFilters.tsx

import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
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
      <div className="flex flex-wrap items-center gap-2">
        <Button
          onClick={onToggleFilters}
          variant="outline"
          size="sm"
          className="font-mono text-xs tracking-[0.2em] uppercase"
        >
          {showFilters ? 'Hide' : 'Show'} Filters
        </Button>
        {hasActiveFilters && (
          <Button
            onClick={onClearFilters}
            variant="outline"
            size="sm"
            className="font-mono text-xs tracking-[0.2em] uppercase"
          >
            Clear Filters
          </Button>
        )}
      </div>

      {showFilters && (
        <div className="bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-none p-4 space-y-4">
          <div className="pb-4 border-b border-[color:var(--theme-card-border)]">
            <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
              Colors
            </label>
            <div className="flex flex-wrap gap-2">
              {COLORS.map(color => (
                <button
                  key={color}
                  onClick={() => onToggleColor(color)}
                  className={`px-3 py-1 rounded-none text-xs font-mono tracking-[0.2em] uppercase transition-colors cursor-pointer ${
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
              <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
                Card Types
              </label>
              <div className="flex flex-wrap gap-2">
                {CARD_TYPE_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => onToggleType(option.value)}
                    className={`px-3 py-1 rounded-none text-xs font-mono tracking-[0.2em] uppercase transition-colors cursor-pointer ${
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
              <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
                Set Code
              </label>
              <Input
                type="text"
                placeholder="e.g., M21, CMR"
                value={setFilter}
                onChange={(e) => onSetFilterChange(e.target.value.toUpperCase())}
                className="text-xs font-mono uppercase tracking-[0.12em]"
              />
            </div>

            <div>
              <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
                Rarity
              </label>
              <Select
                value={rarityFilter}
                onChange={(e) => onRarityFilterChange(e.target.value)}
                className="w-full"
              >
                {RARITY_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
                Language
              </label>
              <Select
                value={languageFilter}
                onChange={(e) => onLanguageFilterChange(e.target.value)}
                className="w-full"
              >
                {LANGUAGE_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </Select>
            </div>

            <div>
              <label className="block text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-muted)] mb-2">
                Keyword
              </label>
              <Input
                type="text"
                placeholder="e.g., Flying, Trample"
                value={keywordFilter}
                onChange={(e) => onKeywordFilterChange(e.target.value)}
                className="text-xs font-mono uppercase tracking-[0.12em]"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

