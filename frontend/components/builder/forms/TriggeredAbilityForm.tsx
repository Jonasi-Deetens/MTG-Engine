'use client';

// frontend/components/builder/forms/TriggeredAbilityForm.tsx

import { useState, useEffect } from 'react';
import { useBuilderStore, TriggeredAbility, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';

interface TriggeredAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

const EVENT_OPTIONS = [
  { value: 'enters_battlefield', label: 'Enters the Battlefield' },
  { value: 'dies', label: 'Dies' },
  { value: 'becomes_target', label: 'Becomes the Target' },
  { value: 'attacks', label: 'Attacks' },
  { value: 'blocks', label: 'Blocks' },
  { value: 'deals_damage', label: 'Deals Damage' },
  { value: 'takes_damage', label: 'Takes Damage' },
];

const EFFECT_TYPE_OPTIONS = [
  { value: 'damage', label: 'Deal Damage' },
  { value: 'draw', label: 'Draw Cards' },
  { value: 'token', label: 'Create Token' },
  { value: 'counters', label: 'Add Counters' },
  { value: 'life', label: 'Gain Life' },
  { value: 'destroy', label: 'Destroy' },
  { value: 'exile', label: 'Exile' },
];

export function TriggeredAbilityForm({ abilityId, onSave, onCancel }: TriggeredAbilityFormProps) {
  const { triggeredAbilities, addTriggeredAbility, updateTriggeredAbility } = useBuilderStore();
  
  const existingAbility = abilityId ? triggeredAbilities.find((a) => a.id === abilityId) : null;
  
  const [event, setEvent] = useState(existingAbility?.event || 'enters_battlefield');
  const [condition, setCondition] = useState(existingAbility?.condition || '');
  const [effects, setEffects] = useState<Effect[]>(existingAbility?.effects || [{ type: 'damage', amount: 0 }]);

  const handleAddEffect = () => {
    setEffects([...effects, { type: 'damage', amount: 0 }]);
  };

  const handleRemoveEffect = (index: number) => {
    setEffects(effects.filter((_, i) => i !== index));
  };

  const handleUpdateEffect = (index: number, field: string, value: any) => {
    const updated = [...effects];
    updated[index] = { ...updated[index], [field]: value };
    setEffects(updated);
  };

  const handleSave = () => {
    const ability: TriggeredAbility = {
      id: abilityId || `triggered-${Date.now()}`,
      event,
      condition: condition || undefined,
      effects: effects.filter((e) => e.type && (e.amount !== undefined || e.type !== 'damage')),
    };

    if (abilityId) {
      updateTriggeredAbility(abilityId, ability);
    } else {
      addTriggeredAbility(ability);
    }
    onSave();
  };

  return (
    <div className="space-y-6">
      {/* Event Selection */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Trigger Event *
        </label>
        <select
          value={event}
          onChange={(e) => setEvent(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
        >
          {EVENT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Condition (Optional) */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Condition (Optional)
        </label>
        <input
          type="text"
          value={condition}
          onChange={(e) => setCondition(e.target.value)}
          placeholder="e.g., if you control an artifact"
          className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
        />
      </div>

      {/* Effects */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-slate-300">
            Effects *
          </label>
          <Button
            onClick={handleAddEffect}
            className="px-3 py-1 text-xs bg-slate-600 hover:bg-slate-500"
          >
            + Add Effect
          </Button>
        </div>
        <div className="space-y-3">
          {effects.map((effect, index) => (
            <div key={index} className="bg-slate-700/50 rounded p-3 border border-slate-600">
              <div className="flex items-start justify-between mb-2">
                <span className="text-xs text-slate-400">Effect {index + 1}</span>
                {effects.length > 1 && (
                  <button
                    onClick={() => handleRemoveEffect(index)}
                    className="text-xs text-red-400 hover:text-red-300"
                  >
                    Remove
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Type</label>
                  <select
                    value={effect.type || 'damage'}
                    onChange={(e) => handleUpdateEffect(index, 'type', e.target.value)}
                    className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                  >
                    {EFFECT_TYPE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
                {(effect.type === 'damage' || effect.type === 'draw' || effect.type === 'token' || effect.type === 'counters' || effect.type === 'life') && (
                  <div>
                    <label className="block text-xs text-slate-400 mb-1">Amount</label>
                    <input
                      type="number"
                      value={effect.amount || 0}
                      onChange={(e) => handleUpdateEffect(index, 'amount', parseInt(e.target.value) || 0)}
                      min="0"
                      className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                )}
                {effect.type === 'damage' && (
                  <div className="col-span-2">
                    <label className="block text-xs text-slate-400 mb-1">Target</label>
                    <select
                      value={effect.target || 'any'}
                      onChange={(e) => handleUpdateEffect(index, 'target', e.target.value)}
                      className="w-full px-2 py-1.5 bg-slate-800 text-white rounded border border-slate-600 text-sm focus:border-amber-500 focus:outline-none"
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
          ))}
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

