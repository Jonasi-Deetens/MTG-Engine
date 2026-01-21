'use client';

import { Effect } from '@/store/builderStore';
import { AmountField, TargetField } from './CommonFields';

/**
 * LifeEffectFields - Fields for life-related effects
 * 
 * Handles effect types:
 * - gain_life
 * - lose_life
 * - set_life
 * - pay_life
 */

interface LifeEffectFieldsProps {
  effect: Effect;
  onUpdate: (field: string, value: any) => void;
}

export function LifeEffectFields({ effect, onUpdate }: LifeEffectFieldsProps) {
  switch (effect.type) {
    case 'gain_life':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Life to Gain" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent', 'each_player'].includes(o.value))}
          />
        </div>
      );

    case 'lose_life':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Life to Lose" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent', 'each_player', 'each_opponent'].includes(o.value))}
          />
        </div>
      );

    case 'set_life':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Set Life To" min={1} />
          <TargetField
            effect={effect}
            onUpdate={onUpdate}
            filterOptions={(opts) => opts.filter((o) => ['player', 'any_player', 'opponent'].includes(o.value))}
          />
        </div>
      );

    case 'pay_life':
      return (
        <div className="space-y-3">
          <AmountField effect={effect} onUpdate={onUpdate} label="Life to Pay" min={1} />
        </div>
      );

    default:
      return null;
  }
}

export function isLifeEffect(type: string): boolean {
  return ['gain_life', 'lose_life', 'set_life', 'pay_life'].includes(type);
}
