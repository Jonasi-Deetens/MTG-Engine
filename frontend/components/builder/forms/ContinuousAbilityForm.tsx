'use client';

// frontend/components/builder/forms/ContinuousAbilityForm.tsx

import { useState } from 'react';
import { useBuilderStore, ContinuousAbility, ValidationError, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { EffectFields } from './EffectFields';

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
  const { continuousAbilities, addContinuousAbility, updateContinuousAbility, validationErrors } = useBuilderStore();
  
  const existingAbility = abilityId ? continuousAbilities.find((a) => a.id === abilityId) : null;
  const nodeId = abilityId || existingAbility?.id;
  const nodeErrors = nodeId
    ? validationErrors.filter((error: ValidationError) => error.nodeId === `continuous-${nodeId}`)
    : [];
  
  const [appliesTo, setAppliesTo] = useState(existingAbility?.appliesTo || 'self');
  const [effect, setEffect] = useState(existingAbility?.effect || '');
  const [useStructured, setUseStructured] = useState(!!existingAbility?.effectData);
  const [effectData, setEffectData] = useState<Effect>(
    existingAbility?.effectData || {
      type: 'set_types',
      target: 'permanent',
      types: ['Creature'],
      duration: 'permanent',
    }
  );
  const allowedEffectTypes = [
    'set_types',
    'add_type',
    'remove_type',
    'set_colors',
    'add_color',
    'remove_color',
    'gain_keyword',
    'change_power_toughness',
    'change_control',
    'cda_power_toughness',
  ];

  const handleSave = () => {
    const ability: ContinuousAbility = {
      id: abilityId || `continuous-${Date.now()}`,
      appliesTo,
      effect,
      effectData: useStructured ? effectData : undefined,
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
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
          Applies To *
        </label>
        <select
          value={appliesTo}
          onChange={(e) => setAppliesTo(e.target.value)}
          className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
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
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
          Effect Description *
        </label>
        <label className="flex items-center gap-2 mb-2">
          <input
            type="checkbox"
            checked={useStructured}
            onChange={(e) => setUseStructured(e.target.checked)}
            className="w-4 h-4 rounded border-[color:var(--theme-input-border)] bg-[color:var(--theme-input-bg)] text-[color:var(--theme-accent-primary)] focus:ring-[color:var(--theme-border-focus)]"
          />
          <span className="text-xs text-[color:var(--theme-text-secondary)]">Use structured effect</span>
        </label>
        {useStructured ? (
          <EffectFields
            effect={effectData}
            index={0}
            allEffects={[effectData]}
            nodeId={nodeId ? `continuous-${nodeId}` : undefined}
            allowedEffectTypes={allowedEffectTypes}
            onUpdate={(field, value) => setEffectData((prev) => ({ ...prev, [field]: value }))}
          />
        ) : (
          <textarea
            value={effect}
            onChange={(e) => setEffect(e.target.value)}
            placeholder="e.g., gets +1/+1, has flying, can't be blocked"
            rows={4}
            className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none resize-none"
          />
        )}
        {nodeErrors.map((error, idx) => (
          <div key={`continuous-error-${idx}`} className="text-xs text-[color:var(--theme-status-error)] mt-1">
            {error.message}
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-[color:var(--theme-border-default)]">
        <Button
          onClick={handleSave}
          variant="primary"
          className="flex-1"
        >
          Save
        </Button>
        <Button
          onClick={onCancel}
          variant="secondary"
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}

