'use client';

import { Effect } from '@/store/builderStore';
import { MANA_TYPE_OPTIONS } from '@/lib/effectTypes';
import { AmountField, TargetField } from './CommonFields';

/**
 * ManaEffectFields - Fields for mana-related effects
 * 
 * Handles effect types:
 * - add_mana
 * - ritual (temporary mana)
 */

interface ManaEffectFieldsProps {
  effect: Effect;
  onUpdate: (field: string, value: any) => void;
}

export function ManaEffectFields({ effect, onUpdate }: ManaEffectFieldsProps) {
  switch (effect.type) {
    case 'add_mana':
    case 'ritual':
      return (
        <div className="space-y-3">
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
          <AmountField effect={effect} onUpdate={onUpdate} label="Mana Amount" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player'].includes(o.value))}
          />
        </div>
      );

    default:
      return null;
  }
}

export function isManaEffect(type: string): boolean {
  return ['add_mana', 'ritual'].includes(type);
}
