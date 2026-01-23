'use client';

import { Effect } from '@/store/builderStore';
import { DISCARD_TYPE_OPTIONS } from '@/lib/effectTypes';
import { AmountField, TargetField, CheckboxField } from './CommonFields';

/**
 * DrawEffectFields - Fields for draw-related effects
 * 
 * Handles effect types:
 * - draw
 * - mill
 * - discard
 * - loot (draw then discard)
 */

interface DrawEffectFieldsProps {
  effect: Effect;
  onUpdate: (field: string, value: any) => void;
}

export function DrawEffectFields({ effect, onUpdate }: DrawEffectFieldsProps) {
  switch (effect.type) {
    case 'draw':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Cards to Draw" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent', 'each_player', 'each_opponent'].includes(o.value))}
          />
          <CheckboxField
            label="Optional (may draw)"
            checked={effect.optional ?? false}
            onChange={(checked) => onUpdate('optional', checked)}
          />
        </div>
      );

    case 'mill':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Cards to Mill" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent', 'each_player', 'each_opponent'].includes(o.value))}
          />
        </div>
      );

    case 'discard':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Cards to Discard" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent', 'each_player', 'each_opponent'].includes(o.value))}
          />
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Discard Type</label>
            <select
              value={effect.discardType || 'choice'}
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
        </div>
      );

    case 'loot':
      return (
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Draw Amount</label>
            <input
              type="number"
              value={effect.drawAmount || 1}
              onChange={(e) => onUpdate('drawAmount', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Discard Amount</label>
            <input
              type="number"
              value={effect.discardAmount || 1}
              onChange={(e) => onUpdate('discardAmount', parseInt(e.target.value) || 1)}
              min="1"
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent'].includes(o.value))}
          />
        </div>
      );

    default:
      return null;
  }
}

export function isDrawEffect(type: string): boolean {
  return ['draw', 'mill', 'discard', 'loot'].includes(type);
}
