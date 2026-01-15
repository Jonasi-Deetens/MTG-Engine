'use client';

// frontend/components/builder/forms/EffectFields.tsx
// Reusable effect field components for all ability forms

import { Effect, useBuilderStore, ValidationError } from '@/store/builderStore';
import { 
  EFFECT_TYPE_OPTIONS, 
  TARGET_OPTIONS, 
  MANA_TYPE_OPTIONS, 
  UNTAP_TARGET_OPTIONS, 
  ATTACH_TARGET_OPTIONS, 
  CARD_TYPE_FILTERS, 
  SEARCH_ZONE_OPTIONS,
  COMPARE_AGAINST_ZONE_OPTIONS,
  DURATION_OPTIONS,
  CHOICE_TYPE_OPTIONS,
  PROTECTION_TYPE_OPTIONS,
  DISCARD_TYPE_OPTIONS,
  LOOK_AT_POSITION_OPTIONS,
  COLOR_OPTIONS,
  CDA_SOURCE_OPTIONS,
  CDA_TYPE_OPTIONS,
  CDA_ZONE_OPTIONS,
  CDA_SET_OPTIONS,
  CDA_TEMPLATE_OPTIONS,
  ZONE_OPTIONS
} from '@/lib/effectTypes';
import { useEffect, useState } from 'react';
import { abilities } from '@/lib/abilities';

interface EffectFieldsProps {
  effect: Effect;
  index: number;
  allEffects: Effect[];
  nodeId?: string;
  allowedEffectTypes?: string[];
  onUpdate: (field: string, value: any) => void;
}

export function EffectFields({ effect, index, allEffects, nodeId, allowedEffectTypes, onUpdate }: EffectFieldsProps) {
  const filteredEffectTypes = allowedEffectTypes
    ? EFFECT_TYPE_OPTIONS.filter((opt) => allowedEffectTypes.includes(opt.value))
    : EFFECT_TYPE_OPTIONS;
  const selectedEffectType = filteredEffectTypes.find((opt) => opt.value === effect.type);
  const shouldShowMaxTargets = !!(
    selectedEffectType?.requiresTarget ||
    selectedEffectType?.requiresUntapTarget ||
    selectedEffectType?.requiresTwoTargets
  );
  const { validationErrors } = useBuilderStore();
  const [keywords, setKeywords] = useState<Array<{ value: string; label: string }>>([]);

  const parseList = (value: string) =>
    value
      .split(',')
      .map((token) => token.trim())
      .filter(Boolean);

  const normalizeTypeList = (value: string) =>
    parseList(value).map((token) => token.charAt(0).toUpperCase() + token.slice(1).toLowerCase());

  const normalizeColorList = (value: string) =>
    parseList(value).map((token) => token.toUpperCase());

  const getNodeErrors = (errors: ValidationError[], id?: string) =>
    id ? errors.filter((error) => error.nodeId === id) : [];

  const nodeErrors = getNodeErrors(validationErrors, nodeId);

  const getFieldErrors = (keyword: string) =>
    nodeErrors.filter((error) => error.message.toLowerCase().includes(keyword));

  const getCdaTemplateValue = (current: Effect) => {
    const match = CDA_TEMPLATE_OPTIONS.find((opt) =>
      Object.entries(opt.config).every(([field, value]) => current[field] === value)
    );
    return match?.value || 'custom';
  };

  // Fetch keywords for gain_keyword effect
  useEffect(() => {
    if (selectedEffectType?.requiresKeyword) {
      abilities.listKeywords().then((response) => {
        setKeywords(response.keywords.map(k => ({ value: k.name, label: k.name })));
      }).catch(() => {
        setKeywords([]);
      });
    }
  }, [selectedEffectType?.requiresKeyword]);

  useEffect(() => {
    if (!allowedEffectTypes || allowedEffectTypes.length === 0) return;
    if (allowedEffectTypes.includes(effect.type)) return;
    onUpdate('type', allowedEffectTypes[0]);
  }, [allowedEffectTypes, effect.type, onUpdate]);

  return (
    <div className="space-y-3">
      {/* Effect Type */}
      <div>
        <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Type</label>
        <select
          value={effect.type || 'damage'}
          onChange={(e) => {
            const nextType = e.target.value;
            onUpdate('type', nextType);
            if (nextType === 'counter_spell') {
              onUpdate('target', 'spell');
            }
            if (nextType === 'cda_power_toughness') {
              onUpdate('cdaSource', 'controlled');
              onUpdate('cdaType', 'Permanent');
              onUpdate('cdaSet', 'both');
            }
            const nextEffectType = EFFECT_TYPE_OPTIONS.find((opt) => opt.value === nextType);
            const supportsMaxTargets = !!(
              nextEffectType?.requiresTarget ||
              nextEffectType?.requiresUntapTarget ||
              nextEffectType?.requiresTwoTargets
            );
            if (!supportsMaxTargets) {
              onUpdate('maxTargets', undefined);
            }
          }}
          className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
        >
          {filteredEffectTypes.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Amount */}
      {selectedEffectType?.requiresAmount && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Amount</label>
          <input
            type="number"
            value={effect.amount || 0}
            onChange={(e) => onUpdate('amount', parseInt(e.target.value) || 0)}
            min="0"
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      )}

      {/* Mana Type */}
      {selectedEffectType?.requiresManaType && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Mana Type</label>
            <select
              value={effect.manaType || 'C'}
              onChange={(e) => onUpdate('manaType', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {MANA_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Amount</label>
            <input
              type="number"
              value={effect.amount || 1}
              onChange={(e) => onUpdate('amount', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Target */}
      {selectedEffectType?.requiresTarget && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Target</label>
          <select
            value={effect.target || 'any'}
            onChange={(e) => onUpdate('target', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {(effect.type === 'counter_spell'
              ? TARGET_OPTIONS.filter((opt) => opt.value === 'spell')
              : TARGET_OPTIONS
            ).map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {selectedEffectType?.requiresTypeList && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Types (comma-separated)</label>
          <input
            type="text"
            value={Array.isArray(effect.types) ? effect.types.join(', ') : ''}
            onChange={(e) => onUpdate('types', normalizeTypeList(e.target.value))}
            placeholder="Creature, Artifact"
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
          {getFieldErrors('type').map((error, idx) => (
            <div key={`type-error-${idx}`} className="text-xs text-[color:var(--theme-status-error)]">
              {error.message}
            </div>
          ))}
        </div>
      )}

      {selectedEffectType?.requiresTypeName && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Type</label>
          <select
            value={effect.typeName || 'creature'}
            onChange={(e) => onUpdate('typeName', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {CARD_TYPE_FILTERS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {getFieldErrors('type').map((error, idx) => (
            <div key={`type-name-error-${idx}`} className="text-xs text-[color:var(--theme-status-error)]">
              {error.message}
            </div>
          ))}
        </div>
      )}

      {selectedEffectType?.requiresColorList && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Colors (comma-separated)</label>
          <input
            type="text"
            value={Array.isArray(effect.colors) ? effect.colors.join(', ') : ''}
            onChange={(e) => onUpdate('colors', normalizeColorList(e.target.value))}
            placeholder="W, U"
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
          {getFieldErrors('color').map((error, idx) => (
            <div key={`color-error-${idx}`} className="text-xs text-[color:var(--theme-status-error)]">
              {error.message}
            </div>
          ))}
        </div>
      )}

      {selectedEffectType?.requiresColor && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Color</label>
          <select
            value={effect.color || 'W'}
            onChange={(e) => onUpdate('color', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {COLOR_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {getFieldErrors('color').map((error, idx) => (
            <div key={`color-name-error-${idx}`} className="text-xs text-[color:var(--theme-status-error)]">
              {error.message}
            </div>
          ))}
        </div>
      )}

      {selectedEffectType?.requiresCdaSource && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Template</label>
            <select
              value={getCdaTemplateValue(effect)}
              onChange={(e) => {
                const selected = CDA_TEMPLATE_OPTIONS.find((opt) => opt.value === e.target.value);
                if (!selected) return;
                Object.entries(selected.config).forEach(([field, value]) => onUpdate(field, value));
              }}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              <option value="custom">Custom</option>
              {CDA_TEMPLATE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">CDA Source</label>
            <select
              value={effect.cdaSource || 'controlled'}
              onChange={(e) => {
                const nextSource = e.target.value;
                onUpdate('cdaSource', nextSource);
                if (nextSource === 'controlled' && !effect.cdaType) {
                  onUpdate('cdaType', 'Permanent');
                }
                if (nextSource === 'zone' && !effect.cdaZone) {
                  onUpdate('cdaZone', 'hand');
                }
              }}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {CDA_SOURCE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          {effect.cdaSource === 'controlled' && (
            <div>
              <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Count Type</label>
              <select
                value={effect.cdaType || 'Permanent'}
                onChange={(e) => onUpdate('cdaType', e.target.value)}
                className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                {CDA_TYPE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          )}
          {effect.cdaSource === 'zone' && (
            <div>
              <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Zone</label>
              <select
                value={effect.cdaZone || 'hand'}
                onChange={(e) => onUpdate('cdaZone', e.target.value)}
                className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                {CDA_ZONE_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Sets</label>
            <select
              value={effect.cdaSet || 'both'}
              onChange={(e) => onUpdate('cdaSet', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {CDA_SET_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {selectedEffectType?.requiresReplacementZone && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">From Zone</label>
            <select
              value={effect.fromZone || 'battlefield'}
              onChange={(e) => onUpdate('fromZone', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">To Zone</label>
            <select
              value={effect.toZone || 'graveyard'}
              onChange={(e) => onUpdate('toZone', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Replacement Zone</label>
            <select
              value={effect.replacementZone || 'exile'}
              onChange={(e) => onUpdate('replacementZone', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {selectedEffectType?.requiresUses && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">
            Uses <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
          </label>
          <input
            type="number"
            value={effect.uses || ''}
            onChange={(e) => {
              const value = e.target.value ? parseInt(e.target.value, 10) : undefined;
              onUpdate('uses', value);
            }}
            min="1"
            placeholder="Unlimited"
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      )}

      {shouldShowMaxTargets && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">
            Max Targets <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
          </label>
          <input
            type="number"
            value={effect.maxTargets || ''}
            onChange={(e) => {
              const value = e.target.value ? parseInt(e.target.value, 10) : undefined;
              onUpdate('maxTargets', value);
            }}
            min="1"
            placeholder="Leave blank for unlimited"
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
          {effect.maxTargets !== undefined &&
            (!Number.isFinite(effect.maxTargets) || effect.maxTargets < 1) && (
              <div className="text-xs text-[color:var(--theme-status-error)]">Must be at least 1.</div>
            )}
          {typeof effect.maxTargets === 'number' && effect.maxTargets > 10 && (
            <div className="text-xs text-[color:var(--theme-text-muted)]">
              Large target counts can be hard to resolve in play.
            </div>
          )}
        </div>
      )}

      {/* Untap Target */}
      {selectedEffectType?.requiresUntapTarget && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Target</label>
          <select
            value={effect.untapTarget || 'self'}
            onChange={(e) => onUpdate('untapTarget', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Zone</label>
          <select
            value={effect.zone || 'library'}
            onChange={(e) => onUpdate('zone', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Card Type</label>
            <select
              value={effect.cardType || 'any'}
              onChange={(e) => onUpdate('cardType', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {CARD_TYPE_FILTERS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Mana Value Comparison</label>
            <div className="space-y-2">
              <select
                value={effect.manaValueComparison || '<='}
                onChange={(e) => onUpdate('manaValueComparison', e.target.value)}
                className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
              >
                <option value="<=">≤ (Less than or equal)</option>
                <option value="<">&lt; (Less than)</option>
                <option value=">=">≥ (Greater than or equal)</option>
                <option value=">">&gt; (Greater than)</option>
                <option value="==">= (Equal)</option>
              </select>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Compare Against</label>
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
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              )}
              {effect.manaValueComparisonSource && effect.manaValueComparisonSource !== 'fixed_value' && (
                <p className="text-xs text-[color:var(--theme-text-muted)]">Will compare against the {effect.manaValueComparisonSource.replace(/_/g, ' ')}'s mana value</p>
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
                className="w-4 h-4 rounded border-[color:var(--theme-input-border)] bg-[color:var(--theme-input-bg)] text-[color:var(--theme-accent-primary)] focus:ring-[color:var(--theme-border-focus)]"
              />
              <span className="text-xs text-[color:var(--theme-text-secondary)]">Different name check</span>
            </label>
            {((typeof effect.differentName === 'object' && effect.differentName.enabled) || effect.differentName === true) && (
              <div className="pl-6 space-y-2 border-l-2 border-[color:var(--theme-border-default)]">
                <div>
                  <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">
                    Compare Against Type <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
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
                    className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  >
                    {CARD_TYPE_FILTERS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-[color:var(--theme-text-muted)] mt-1">
                    Leave as "Any" to compare against all cards, or select a specific type (e.g., "Aura" for Light-Paws)
                  </p>
                </div>
                <div>
                  <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">
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
                    className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Attach To</label>
          <select
            value={effect.attachTo || 'self'}
            onChange={(e) => onUpdate('attachTo', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {ATTACH_TARGET_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Duration */}
      {selectedEffectType?.requiresDuration && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Duration</label>
          <select
            value={effect.duration || 'until_end_of_turn'}
            onChange={(e) => onUpdate('duration', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {DURATION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Choice Type */}
      {selectedEffectType?.requiresChoice && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Player Choice</label>
          <select
            value={effect.choice || 'color'}
            onChange={(e) => onUpdate('choice', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {CHOICE_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <p className="text-xs text-[color:var(--theme-text-muted)] mt-1">
            Player will choose this at runtime
          </p>
        </div>
      )}

      {/* Protection Type */}
      {selectedEffectType?.requiresProtectionType && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Protection From</label>
          <select
            value={effect.protectionType || 'white'}
            onChange={(e) => {
              onUpdate('protectionType', e.target.value);
              // If chosen_color, enable choice
              if (e.target.value === 'chosen_color') {
                onUpdate('choice', 'color');
              } else {
                onUpdate('choice', undefined);
              }
            }}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {PROTECTION_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Keyword (for gain_keyword) */}
      {selectedEffectType?.requiresKeyword && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Keyword</label>
          <select
            value={effect.keyword || ''}
            onChange={(e) => onUpdate('keyword', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            <option value="">Select a keyword</option>
            {keywords.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Power/Toughness Change */}
      {selectedEffectType?.requiresPowerToughness && (
        <div className="space-y-2">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Power Change</label>
            <input
              type="number"
              value={effect.powerChange || 0}
              onChange={(e) => onUpdate('powerChange', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Toughness Change</label>
            <input
              type="number"
              value={effect.toughnessChange || 0}
              onChange={(e) => onUpdate('toughnessChange', parseInt(e.target.value) || 0)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
        </div>
      )}

      {/* Two Targets (for fight, redirect damage) */}
      {selectedEffectType?.requiresTwoTargets && (
        <div className="space-y-2">
          {effect.type === 'fight' && (
            <>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Your Creature</label>
                <select
                  value={effect.yourCreature || 'creature'}
                  onChange={(e) => onUpdate('yourCreature', e.target.value)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  {TARGET_OPTIONS.filter(opt => opt.value === 'creature' || opt.value === 'self').map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Opponent's Creature</label>
                <select
                  value={effect.opponentCreature || 'creature'}
                  onChange={(e) => onUpdate('opponentCreature', e.target.value)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  {TARGET_OPTIONS.filter(opt => opt.value === 'creature').map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
          {effect.type === 'redirect_damage' && (
            <>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Source Target (would receive damage)</label>
                <select
                  value={effect.sourceTarget || 'creature'}
                  onChange={(e) => onUpdate('sourceTarget', e.target.value)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  {TARGET_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Redirect Target (receives damage instead)</label>
                <select
                  value={effect.redirectTarget || 'creature'}
                  onChange={(e) => onUpdate('redirectTarget', e.target.value)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  {TARGET_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>
      )}

      {/* Discard Type */}
      {selectedEffectType?.requiresDiscardType && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Discard Type</label>
          <select
            value={effect.discardType || 'chosen'}
            onChange={(e) => onUpdate('discardType', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {DISCARD_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Position (for look_at) */}
      {selectedEffectType?.requiresPosition && (
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Position</label>
          <select
            value={effect.position || 'top'}
            onChange={(e) => onUpdate('position', e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            {LOOK_AT_POSITION_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Return Under Owner (for flicker) */}
      {effect.type === 'flicker' && (
        <div>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={effect.returnUnderOwner || false}
              onChange={(e) => onUpdate('returnUnderOwner', e.target.checked)}
              className="w-4 h-4 rounded border-[color:var(--theme-input-border)] bg-[color:var(--theme-input-bg)] text-[color:var(--theme-accent-primary)] focus:ring-[color:var(--theme-border-focus)]"
            />
            <span className="text-xs text-[color:var(--theme-text-secondary)]">Return under owner's control</span>
          </label>
        </div>
      )}

      {/* Effect Linking - Show for effects that can reference previous effects */}
      {index > 0 && (
        <div className="mt-3 pt-3 border-t border-[color:var(--theme-border-default)]">
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">
            Reference Previous Effect <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
          </label>
          <select
            value={effect.fromEffect !== undefined ? effect.fromEffect.toString() : ''}
            onChange={(e) => {
              const value = e.target.value === '' ? undefined : parseInt(e.target.value);
              onUpdate('fromEffect', value);
            }}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
            <p className="text-xs text-[color:var(--theme-accent-primary)] mt-1">
              ✓ Will use the result from effect {effect.fromEffect + 1}
            </p>
          )}
          <p className="text-xs text-[color:var(--theme-text-muted)] mt-1">
            Use this to chain effects together (e.g., search → put onto battlefield → attach)
          </p>
        </div>
      )}
    </div>
  );
}

