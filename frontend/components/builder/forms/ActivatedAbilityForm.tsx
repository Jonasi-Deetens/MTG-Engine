'use client';

// frontend/components/builder/forms/ActivatedAbilityForm.tsx

import { useState } from 'react';
import { useBuilderStore, ActivatedAbility, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';

interface ActivatedAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

const EFFECT_TYPE_OPTIONS = [
  { value: 'damage', label: 'Deal Damage' },
  { value: 'draw', label: 'Draw Cards' },
  { value: 'token', label: 'Create Token' },
  { value: 'counters', label: 'Add Counters' },
  { value: 'life', label: 'Gain Life' },
  { value: 'destroy', label: 'Destroy' },
  { value: 'exile', label: 'Exile' },
];

export function ActivatedAbilityForm({ abilityId, onSave, onCancel }: ActivatedAbilityFormProps) {
  const { activatedAbilities, addActivatedAbility, updateActivatedAbility } = useBuilderStore();
  
  const existingAbility = abilityId ? activatedAbilities.find((a) => a.id === abilityId) : null;
  
  const [cost, setCost] = useState(existingAbility?.cost || '{T}');
  const [effectType, setEffectType] = useState(existingAbility?.effect.type || 'damage');
  const [effectAmount, setEffectAmount] = useState(existingAbility?.effect.amount || 0);
  const [effectTarget, setEffectTarget] = useState(existingAbility?.effect.target || 'any');

  const handleSave = () => {
    const effect: Effect = {
      type: effectType,
      amount: effectAmount,
      target: effectTarget,
    };

    const ability: ActivatedAbility = {
      id: abilityId || `activated-${Date.now()}`,
      cost,
      effect,
    };

    if (abilityId) {
      updateActivatedAbility(abilityId, ability);
    } else {
      addActivatedAbility(ability);
    }
    onSave();
  };

  return (
    <div className="space-y-6">
      {/* Cost */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Activation Cost *
        </label>
        <input
          type="text"
          value={cost}
          onChange={(e) => setCost(e.target.value)}
          placeholder="e.g., {T}, {1}{R}, Sacrifice a creature"
          className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
        />
        <p className="text-xs text-slate-400 mt-1">
          Use mana symbols like {'{T}'}, {'{1}{R}'}, or describe other costs
        </p>
      </div>

      {/* Effect */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Effect *
        </label>
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Effect Type</label>
            <select
              value={effectType}
              onChange={(e) => setEffectType(e.target.value)}
              className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
            >
              {EFFECT_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          
          {(effectType === 'damage' || effectType === 'draw' || effectType === 'token' || effectType === 'counters' || effectType === 'life') && (
            <div>
              <label className="block text-xs text-slate-400 mb-1">Amount</label>
              <input
                type="number"
                value={effectAmount}
                onChange={(e) => setEffectAmount(parseInt(e.target.value) || 0)}
                min="0"
                className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
              />
            </div>
          )}
          
          {effectType === 'damage' && (
            <div>
              <label className="block text-xs text-slate-400 mb-1">Target</label>
              <select
                value={effectTarget}
                onChange={(e) => setEffectTarget(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
              >
                <option value="any">Any Target</option>
                <option value="creature">Target Creature</option>
                <option value="player">Target Player</option>
                <option value="planeswalker">Target Planeswalker</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-slate-700">
        <Button
          onClick={handleSave}
          className="flex-1 bg-amber-600 hover:bg-amber-700"
        >
          Save
        </Button>
        <Button
          onClick={onCancel}
          className="flex-1 bg-slate-600 hover:bg-slate-500"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}

