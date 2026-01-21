'use client';

import { Effect } from '@/store/builderStore';
import {
  EFFECT_TYPE_OPTIONS,
  TARGET_OPTIONS,
  DURATION_OPTIONS,
} from '@/lib/effectTypes';

/**
 * CommonFields - Shared effect field components
 * 
 * Provides reusable field components for:
 * - Effect type selection
 * - Target selection
 * - Amount input
 * - Duration selection
 * - Mode selection
 */

interface CommonFieldsProps {
  effect: Effect;
  onUpdate: (field: string, value: any) => void;
  allowedEffectTypes?: string[];
  modeOptions?: Array<{ value: string; label: string }>;
}

export function EffectTypeField({
  effect,
  onUpdate,
  allowedEffectTypes,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate' | 'allowedEffectTypes'>) {
  const filteredEffectTypes = allowedEffectTypes
    ? EFFECT_TYPE_OPTIONS.filter((opt) => allowedEffectTypes.includes(opt.value))
    : EFFECT_TYPE_OPTIONS;

  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Type</label>
      <select
        value={effect.type || 'damage'}
        onChange={(e) => {
          const nextType = e.target.value;
          onUpdate('type', nextType);
          // Reset related fields based on new type
          if (nextType === 'counter_spell') {
            onUpdate('target', 'spell');
          }
          if (['replace_draw', 'replace_discard', 'replace_life_loss', 'lose_life'].includes(nextType)) {
            onUpdate('target', 'player');
          }
          if (nextType === 'cda_power_toughness') {
            onUpdate('cdaSource', 'controlled');
            onUpdate('cdaType', 'Permanent');
            onUpdate('cdaSet', 'both');
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
  );
}

export function ModeField({
  effect,
  onUpdate,
  modeOptions,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate' | 'modeOptions'>) {
  if (!modeOptions || modeOptions.length === 0) return null;

  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Mode</label>
      <select
        value={effect.modeId || ''}
        onChange={(e) => onUpdate('modeId', e.target.value || undefined)}
        className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
      >
        <option value="">No mode (always apply)</option>
        {modeOptions.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function AmountField({
  effect,
  onUpdate,
  label = 'Amount',
  min = 0,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate'> & { label?: string; min?: number }) {
  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">{label}</label>
      <input
        type="number"
        value={effect.amount || 0}
        onChange={(e) => onUpdate('amount', parseInt(e.target.value) || 0)}
        min={min}
        className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
      />
    </div>
  );
}

export function TargetField({
  effect,
  onUpdate,
  filterOptions,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate'> & { filterOptions?: (opts: typeof TARGET_OPTIONS) => typeof TARGET_OPTIONS }) {
  const options = filterOptions ? filterOptions(TARGET_OPTIONS) : TARGET_OPTIONS;

  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Target</label>
      <select
        value={effect.target || 'any'}
        onChange={(e) => onUpdate('target', e.target.value)}
        className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

export function DurationField({
  effect,
  onUpdate,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate'>) {
  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Duration</label>
      <select
        value={effect.duration || 'permanent'}
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
  );
}

export function MaxTargetsField({
  effect,
  onUpdate,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate'>) {
  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Max Targets</label>
      <input
        type="number"
        value={effect.maxTargets ?? ''}
        onChange={(e) => {
          const val = e.target.value ? parseInt(e.target.value) : undefined;
          onUpdate('maxTargets', val);
        }}
        min="1"
        placeholder="Unlimited"
        className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
      />
    </div>
  );
}

export function MinTargetsField({
  effect,
  onUpdate,
}: Pick<CommonFieldsProps, 'effect' | 'onUpdate'>) {
  return (
    <div>
      <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Min Targets</label>
      <input
        type="number"
        value={effect.minTargets ?? ''}
        onChange={(e) => {
          const val = e.target.value ? parseInt(e.target.value) : undefined;
          onUpdate('minTargets', val);
        }}
        min="0"
        placeholder="0"
        className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
      />
    </div>
  );
}

export function CheckboxField({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="rounded border-[color:var(--theme-input-border)]"
      />
      <span className="text-xs text-[color:var(--theme-text-secondary)]">{label}</span>
    </label>
  );
}
