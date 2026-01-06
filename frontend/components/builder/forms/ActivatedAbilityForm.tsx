'use client';

// frontend/components/builder/forms/ActivatedAbilityForm.tsx

import { useState } from 'react';
import { useBuilderStore, ActivatedAbility, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { EFFECT_TYPE_OPTIONS } from '@/lib/effectTypes';
import { EffectFields } from './EffectFields';

interface ActivatedAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

export function ActivatedAbilityForm({ abilityId, onSave, onCancel }: ActivatedAbilityFormProps) {
  const { activatedAbilities, addActivatedAbility, updateActivatedAbility } = useBuilderStore();
  
  const existingAbility = abilityId ? activatedAbilities.find((a) => a.id === abilityId) : null;
  
  const [cost, setCost] = useState(existingAbility?.cost || '{T}');
  const [effectType, setEffectType] = useState(existingAbility?.effect.type || 'damage');
  const [effectAmount, setEffectAmount] = useState(existingAbility?.effect.amount || 0);
  const [effectTarget, setEffectTarget] = useState(existingAbility?.effect.target || 'any');
  const [effectManaType, setEffectManaType] = useState(existingAbility?.effect.manaType || 'C');
  const [effectUntapTarget, setEffectUntapTarget] = useState(existingAbility?.effect.untapTarget || 'self');
  const [effectZone, setEffectZone] = useState(existingAbility?.effect.zone || 'library');
  const [effectCardType, setEffectCardType] = useState(existingAbility?.effect.cardType || 'any');
  const [effectManaValueComparison, setEffectManaValueComparison] = useState(existingAbility?.effect.manaValueComparison || '<=');
  const [effectManaValueComparisonValue, setEffectManaValueComparisonValue] = useState(existingAbility?.effect.manaValueComparisonValue || undefined);
  const [effectManaValueComparisonSource, setEffectManaValueComparisonSource] = useState<string | undefined>(existingAbility?.effect.manaValueComparisonSource || 'fixed_value');
  const [effectDifferentName, setEffectDifferentName] = useState(existingAbility?.effect.differentName || false);
  const [effectAttachTo, setEffectAttachTo] = useState(existingAbility?.effect.attachTo || 'self');
  
  const selectedEffectType = EFFECT_TYPE_OPTIONS.find((opt) => opt.value === effectType);

  const handleSave = () => {
    const effect: Effect = {
      type: effectType,
      amount: effectAmount,
      target: effectTarget,
      manaType: effectManaType,
      untapTarget: effectUntapTarget,
      zone: effectZone,
      cardType: effectCardType,
      manaValueComparison: effectManaValueComparison,
      manaValueComparisonValue: effectManaValueComparisonValue,
      manaValueComparisonSource: effectManaValueComparisonSource || 'fixed_value',
      differentName: effectDifferentName,
      attachTo: effectAttachTo,
    };

    // Clean up undefined fields
    if (!selectedEffectType?.requiresAmount) delete effect.amount;
    if (!selectedEffectType?.requiresTarget) delete effect.target;
    if (!selectedEffectType?.requiresManaType) delete effect.manaType;
    if (!selectedEffectType?.requiresUntapTarget) delete effect.untapTarget;
    if (!selectedEffectType?.requiresSearchFilters) {
      delete effect.zone;
      delete effect.cardType;
      delete effect.manaValueComparison;
      delete effect.manaValueComparisonValue;
      delete effect.manaValueComparisonSource;
      delete effect.differentName;
    }
    if (!selectedEffectType?.requiresZone) delete effect.zone;
    if (!selectedEffectType?.requiresAttachTarget) delete effect.attachTo;

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
        <EffectFields
          effect={{
            type: effectType,
            amount: effectAmount,
            target: effectTarget,
            manaType: effectManaType,
            untapTarget: effectUntapTarget,
            zone: effectZone,
            cardType: effectCardType,
            manaValueComparison: effectManaValueComparison,
            manaValueComparisonValue: effectManaValueComparisonValue,
            manaValueComparisonSource: effectManaValueComparisonSource,
            differentName: effectDifferentName,
            attachTo: effectAttachTo,
          }}
          index={0}
          allEffects={[{
            type: effectType,
            amount: effectAmount,
            target: effectTarget,
            manaType: effectManaType,
            untapTarget: effectUntapTarget,
            zone: effectZone,
            cardType: effectCardType,
            manaValueComparison: effectManaValueComparison,
            manaValueComparisonValue: effectManaValueComparisonValue,
            manaValueComparisonSource: effectManaValueComparisonSource,
            differentName: effectDifferentName,
            attachTo: effectAttachTo,
          }]}
          onUpdate={(field, value) => {
            switch (field) {
              case 'type':
                setEffectType(value);
                break;
              case 'amount':
                setEffectAmount(value);
                break;
              case 'target':
                setEffectTarget(value);
                break;
              case 'manaType':
                setEffectManaType(value);
                break;
              case 'untapTarget':
                setEffectUntapTarget(value);
                break;
              case 'zone':
                setEffectZone(value);
                break;
              case 'cardType':
                setEffectCardType(value);
                break;
              case 'manaValueComparison':
                setEffectManaValueComparison(value);
                break;
              case 'manaValueComparisonValue':
                setEffectManaValueComparisonValue(value);
                break;
              case 'manaValueComparisonSource':
                setEffectManaValueComparisonSource(value);
                break;
              case 'differentName':
                setEffectDifferentName(value);
                break;
              case 'attachTo':
                setEffectAttachTo(value);
                break;
            }
          }}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-slate-700">
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

