'use client';

import { CARD_TYPE_FILTERS, CHOICE_TYPE_OPTIONS, COLOR_OPTIONS } from '@/lib/effectTypes';
import { EnterChoiceConfig } from '@/lib/enterChoices';

interface EnterChoicesPanelProps {
  configs: EnterChoiceConfig[];
  values: Record<string, string>;
  errors: string[];
  targetOptions: Array<{ value: string; label: string }>;
  onChange: (choiceType: string, value: string) => void;
}

export function EnterChoicesPanel({
  configs,
  values,
  errors,
  targetOptions,
  onChange,
}: EnterChoicesPanelProps) {
  if (configs.length === 0) return null;
  const labels = new Map(CHOICE_TYPE_OPTIONS.map((opt) => [opt.value, opt.label]));

  return (
    <div className="space-y-2">
      <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">As Enters Choices</div>
      {configs.map((config) => {
        const label = labels.get(config.choiceType) ?? config.choiceType;
        const value = values[config.choiceType] ?? '';
        if (config.choiceValue) {
          return (
            <div key={`enter-choice-${config.choiceType}`} className="text-xs text-[color:var(--theme-text-secondary)]">
              {label}: {config.choiceValue}
            </div>
          );
        }
        if (config.choiceType === 'color') {
          return (
            <label key={`enter-choice-${config.choiceType}`} className="flex items-center gap-2 text-xs">
              <span className="text-[color:var(--theme-text-secondary)]">{label}</span>
              <select
                value={value || 'W'}
                onChange={(e) => onChange(config.choiceType, e.target.value)}
                className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                {COLOR_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          );
        }
        if (config.choiceType === 'card_type') {
          return (
            <label key={`enter-choice-${config.choiceType}`} className="flex items-center gap-2 text-xs">
              <span className="text-[color:var(--theme-text-secondary)]">{label}</span>
              <select
                value={value || 'creature'}
                onChange={(e) => onChange(config.choiceType, e.target.value)}
                className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                {CARD_TYPE_FILTERS.filter((opt) => opt.value !== 'any').map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          );
        }
        if (config.choiceType === 'target') {
          return (
            <label key={`enter-choice-${config.choiceType}`} className="flex items-center gap-2 text-xs">
              <span className="text-[color:var(--theme-text-secondary)]">{label}</span>
              <select
                value={value}
                onChange={(e) => onChange(config.choiceType, e.target.value)}
                className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                <option value="">Select target</option>
                {targetOptions.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </label>
          );
        }
        return (
          <label key={`enter-choice-${config.choiceType}`} className="flex items-center gap-2 text-xs">
            <span className="text-[color:var(--theme-text-secondary)]">{label}</span>
            <input
              value={value}
              onChange={(e) => onChange(config.choiceType, e.target.value)}
              placeholder="Enter choice"
              className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </label>
        );
      })}
      {errors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">{errors.join(' ')}</div>
      )}
    </div>
  );
}

