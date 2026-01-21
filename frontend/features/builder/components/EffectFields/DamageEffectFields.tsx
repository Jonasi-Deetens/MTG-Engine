'use client';

import { Effect } from '@/store/builderStore';
import { TARGET_OPTIONS } from '@/lib/effectTypes';
import { AmountField, TargetField, MaxTargetsField, CheckboxField } from './CommonFields';

/**
 * DamageEffectFields - Fields for damage-related effects
 * 
 * Handles effect types:
 * - damage
 * - damage_all
 * - prevent_damage
 */

interface DamageEffectFieldsProps {
  effect: Effect;
  onUpdate: (field: string, value: any) => void;
}

export function DamageEffectFields({ effect, onUpdate }: DamageEffectFieldsProps) {
  switch (effect.type) {
    case 'damage':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Damage Amount" />
          <TargetField effect={effect} onUpdate={onUpdate} />
          <MaxTargetsField effect={effect} onUpdate={onUpdate} />
          <CheckboxField
            label="Can target players"
            checked={effect.canTargetPlayers ?? true}
            onChange={(checked) => onUpdate('canTargetPlayers', checked)}
          />
          <CheckboxField
            label="Combat damage only"
            checked={effect.combatDamageOnly ?? false}
            onChange={(checked) => onUpdate('combatDamageOnly', checked)}
          />
        </div>
      );

    case 'damage_all':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Damage to Each" />
          <div>
            <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Damage To</label>
            <select
              value={effect.damageTo || 'creatures'}
              onChange={(e) => onUpdate('damageTo', e.target.value)}
              className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              <option value="creatures">All Creatures</option>
              <option value="players">All Players</option>
              <option value="opponent_creatures">Opponent Creatures</option>
              <option value="your_creatures">Your Creatures</option>
              <option value="everything">Everything (creatures + players)</option>
            </select>
          </div>
        </div>
      );

    case 'prevent_damage':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Prevent Amount" />
          <TargetField effect={effect} onUpdate={onUpdate} />
          <CheckboxField
            label="Prevent all damage"
            checked={effect.preventAll ?? false}
            onChange={(checked) => onUpdate('preventAll', checked)}
          />
          <CheckboxField
            label="Combat damage only"
            checked={effect.combatDamageOnly ?? false}
            onChange={(checked) => onUpdate('combatDamageOnly', checked)}
          />
        </div>
      );

    default:
      return null;
  }
}

export function isDamageEffect(type: string): boolean {
  return ['damage', 'damage_all', 'prevent_damage'].includes(type);
}
