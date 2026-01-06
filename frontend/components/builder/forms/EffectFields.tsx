'use client';

// frontend/components/builder/forms/EffectFields.tsx
// Reusable effect field components for all ability forms

import { Effect } from '@/store/builderStore';
import { 
  EFFECT_TYPE_OPTIONS, 
  TARGET_OPTIONS, 
  MANA_TYPE_OPTIONS, 
  UNTAP_TARGET_OPTIONS, 
  ATTACH_TARGET_OPTIONS, 
  CARD_TYPE_FILTERS, 
  SEARCH_ZONE_OPTIONS,
  COMPARE_AGAINST_ZONE_OPTIONS
} from '@/lib/effectTypes';

interface EffectFieldsProps {
  effect: Effect;
  index: number;
  allEffects: Effect[];
  onUpdate: (field: string, value: any) => void;
}

export function EffectFields({ effect, index, allEffects, onUpdate }: EffectFieldsProps) {
  const selectedEffectType = EFFECT_TYPE_OPTIONS.find((opt) => opt.value === effect.type);

  return (
    <div className="space-y-3">
      {/* Effect Type */}
      <div>
        <label className="block text-xs text-slate-400 mb-1">Type</label>
        <select
          value={effect.type || 'damage'}
          onChange={(e) => onUpdate('type', e.target.value)}
          className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
        >
          {EFFECT_TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Amount */}
      {selectedEffectType?.requiresAmount && (
        <div>
          <label className="block text-xs text-slate-400 mb-1">Amount</label>
          <input
            type="number"
            value={effect.amount || 0}
            onChange={(e) => onUpdate('amount', parseInt(e.target.value) || 0)}
            min="0"
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          />
        </div>
      )}

      {/* Mana Type */}
      {selectedEffectType?.requiresManaType && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Mana Type</label>
            <select
              value={effect.manaType || 'C'}
              onChange={(e) => onUpdate('manaType', e.target.value)}
              className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
            >
              {MANA_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Amount</label>
            <input
              type="number"
              value={effect.amount || 1}
              onChange={(e) => onUpdate('amount', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Target */}
      {selectedEffectType?.requiresTarget && (
        <div>
          <label className="block text-xs text-slate-400 mb-1">Target</label>
          <select
            value={effect.target || 'any'}
            onChange={(e) => onUpdate('target', e.target.value)}
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          >
            {TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Untap Target */}
      {selectedEffectType?.requiresUntapTarget && (
        <div>
          <label className="block text-xs text-slate-400 mb-1">Target</label>
          <select
            value={effect.untapTarget || 'self'}
            onChange={(e) => onUpdate('untapTarget', e.target.value)}
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          >
            {UNTAP_TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Zone (for search) */}
      {selectedEffectType?.requiresZone && (
        <div>
          <label className="block text-xs text-slate-400 mb-1">Zone</label>
          <select
            value={effect.zone || 'library'}
            onChange={(e) => onUpdate('zone', e.target.value)}
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          >
            {SEARCH_ZONE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Search Filters */}
      {selectedEffectType?.requiresSearchFilters && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Card Type</label>
            <select
              value={effect.cardType || 'any'}
              onChange={(e) => onUpdate('cardType', e.target.value)}
              className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
            >
              {CARD_TYPE_FILTERS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Mana Value Comparison</label>
            <div className="space-y-2">
              <select
                value={effect.manaValueComparison || '<='}
                onChange={(e) => onUpdate('manaValueComparison', e.target.value)}
                className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
              >
                <option value="<=">≤ (Less than or equal)</option>
                <option value="<">&lt; (Less than)</option>
                <option value=">=">≥ (Greater than or equal)</option>
                <option value=">">&gt; (Greater than)</option>
                <option value="==">= (Equal)</option>
              </select>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Compare Against</label>
                <select
                  value={effect.manaValueComparisonSource || 'fixed_value'}
                  onChange={(e) => {
                    const newValue = e.target.value;
                    onUpdate('manaValueComparisonSource', newValue);
                    // Clear value when switching to a source-based comparison
                    if (newValue !== 'fixed_value') {
                      onUpdate('manaValueComparisonValue', undefined);
                    }
                  }}
                  className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                >
                  <option value="fixed_value">Fixed Value</option>
                  <option value="triggering_source">Triggering Source</option>
                  <option value="triggering_aura">The Triggering Aura</option>
                  <option value="triggering_spell">The Triggering Spell</option>
                </select>
              </div>
              {(!effect.manaValueComparisonSource || effect.manaValueComparisonSource === 'fixed_value') && (
                <input
                  type="number"
                  value={effect.manaValueComparisonValue || ''}
                  onChange={(e) => onUpdate('manaValueComparisonValue', e.target.value ? parseInt(e.target.value) : undefined)}
                  placeholder="Value"
                  min="0"
                  className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                />
              )}
              {effect.manaValueComparisonSource && effect.manaValueComparisonSource !== 'fixed_value' && (
                <p className="text-xs text-slate-500">Will compare against the {effect.manaValueComparisonSource.replace(/_/g, ' ')}'s mana value</p>
              )}
            </div>
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={
                  typeof effect.differentName === 'object' 
                    ? effect.differentName.enabled 
                    : effect.differentName || false
                }
                onChange={(e) => {
                  const enabled = e.target.checked;
                  if (enabled) {
                    // Initialize as object with defaults
                    onUpdate('differentName', {
                      enabled: true,
                      compareAgainstType: 'any',
                      compareAgainstZone: 'controlled',
                    });
                  } else {
                    // Disable by setting to false
                    onUpdate('differentName', false);
                  }
                }}
                className="w-4 h-4 rounded border-slate-600 bg-slate-800 text-amber-600 focus:ring-amber-500"
              />
              <span className="text-xs text-slate-400">Different name check</span>
            </label>
            {((typeof effect.differentName === 'object' && effect.differentName.enabled) || effect.differentName === true) && (
              <div className="pl-6 space-y-2 border-l-2 border-slate-700">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Compare Against Type <span className="text-slate-500">(optional)</span>
                  </label>
                  <select
                    value={
                      typeof effect.differentName === 'object' 
                        ? (effect.differentName.compareAgainstType || 'any')
                        : 'any'
                    }
                    onChange={(e) => {
                      const current = typeof effect.differentName === 'object' ? effect.differentName : { enabled: true, compareAgainstZone: 'controlled' };
                      onUpdate('differentName', {
                        ...current,
                        compareAgainstType: e.target.value === 'any' ? undefined : e.target.value,
                      });
                    }}
                    className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                  >
                    {CARD_TYPE_FILTERS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-slate-500 mt-1">
                    Leave as "Any" to compare against all cards, or select a specific type (e.g., "Aura" for Light-Paws)
                  </p>
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-1">
                    Compare Against Zone
                  </label>
                  <select
                    value={
                      typeof effect.differentName === 'object' 
                        ? (effect.differentName.compareAgainstZone || 'controlled')
                        : 'controlled'
                    }
                    onChange={(e) => {
                      const current = typeof effect.differentName === 'object' ? effect.differentName : { enabled: true, compareAgainstType: undefined };
                      onUpdate('differentName', {
                        ...current,
                        compareAgainstZone: e.target.value,
                      });
                    }}
                    className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                  >
                    {COMPARE_AGAINST_ZONE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Attach Target */}
      {selectedEffectType?.requiresAttachTarget && (
        <div>
          <label className="block text-xs text-slate-400 mb-1">Attach To</label>
          <select
            value={effect.attachTo || 'self'}
            onChange={(e) => onUpdate('attachTo', e.target.value)}
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          >
            {ATTACH_TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Effect Linking - Show for effects that can reference previous effects */}
      {index > 0 && (
        <div className="mt-3 pt-3 border-t border-slate-600">
          <label className="block text-xs text-slate-400 mb-1">
            Reference Previous Effect <span className="text-slate-500">(optional)</span>
          </label>
          <select
            value={effect.fromEffect !== undefined ? effect.fromEffect.toString() : ''}
            onChange={(e) => {
              const value = e.target.value === '' ? undefined : parseInt(e.target.value);
              onUpdate('fromEffect', value);
            }}
            className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
          >
            <option value="">None (use target/other fields)</option>
            {allEffects.slice(0, index).map((prevEffect, prevIndex) => {
              const prevEffectType = EFFECT_TYPE_OPTIONS.find(opt => opt.value === prevEffect.type);
              const prevLabel = prevEffectType?.label || prevEffect.type;
              return (
                <option key={prevIndex} value={prevIndex.toString()}>
                  Effect {prevIndex + 1}: {prevLabel}
                </option>
              );
            })}
          </select>
          {effect.fromEffect !== undefined && (
            <p className="text-xs text-amber-400 mt-1">
              ✓ Will use the result from effect {effect.fromEffect + 1}
            </p>
          )}
          <p className="text-xs text-slate-500 mt-1">
            Use this to chain effects together (e.g., search → put onto battlefield → attach)
          </p>
        </div>
      )}
    </div>
  );
}

