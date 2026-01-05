'use client';

// frontend/components/builder/forms/ContinuousAbilityForm.tsx

import { useState } from 'react';
import { useBuilderStore, ContinuousAbility } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';

interface ContinuousAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

const APPLIES_TO_OPTIONS = [
  { value: 'self', label: 'This Permanent' },
  { value: 'creatures_you_control', label: 'Creatures You Control' },
  { value: 'enchanted_creature', label: 'Enchanted Creature' },
  { value: 'equipped_creature', label: 'Equipped Creature' },
  { value: 'all_creatures', label: 'All Creatures' },
  { value: 'all_permanents', label: 'All Permanents' },
];

export function ContinuousAbilityForm({ abilityId, onSave, onCancel }: ContinuousAbilityFormProps) {
  const { continuousAbilities, addContinuousAbility, updateContinuousAbility } = useBuilderStore();
  
  const existingAbility = abilityId ? continuousAbilities.find((a) => a.id === abilityId) : null;
  
  const [appliesTo, setAppliesTo] = useState(existingAbility?.appliesTo || 'self');
  const [effect, setEffect] = useState(existingAbility?.effect || '');

  const handleSave = () => {
    const ability: ContinuousAbility = {
      id: abilityId || `continuous-${Date.now()}`,
      appliesTo,
      effect,
    };

    if (abilityId) {
      updateContinuousAbility(abilityId, ability);
    } else {
      addContinuousAbility(ability);
    }
    onSave();
  };

  return (
    <div className="space-y-6">
      {/* Applies To */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Applies To *
        </label>
        <select
          value={appliesTo}
          onChange={(e) => setAppliesTo(e.target.value)}
          className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
        >
          {APPLIES_TO_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Effect */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-2">
          Effect Description *
        </label>
        <textarea
          value={effect}
          onChange={(e) => setEffect(e.target.value)}
          placeholder="e.g., gets +1/+1, has flying, can't be blocked"
          rows={4}
          className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none resize-none"
        />
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

