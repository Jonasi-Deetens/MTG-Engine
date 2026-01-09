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
  // New fields for additional effect types
  const [effectDuration, setEffectDuration] = useState(existingAbility?.effect.duration || 'until_end_of_turn');
  const [effectChoice, setEffectChoice] = useState(existingAbility?.effect.choice || undefined);
  const [effectProtectionType, setEffectProtectionType] = useState(existingAbility?.effect.protectionType || 'white');
  const [effectKeyword, setEffectKeyword] = useState(existingAbility?.effect.keyword || '');
  const [effectPowerChange, setEffectPowerChange] = useState(existingAbility?.effect.powerChange || 0);
  const [effectToughnessChange, setEffectToughnessChange] = useState(existingAbility?.effect.toughnessChange || 0);
  const [effectYourCreature, setEffectYourCreature] = useState(existingAbility?.effect.yourCreature || 'creature');
  const [effectOpponentCreature, setEffectOpponentCreature] = useState(existingAbility?.effect.opponentCreature || 'creature');
  const [effectDiscardType, setEffectDiscardType] = useState(existingAbility?.effect.discardType || 'chosen');
  const [effectPosition, setEffectPosition] = useState(existingAbility?.effect.position || 'top');
  const [effectReturnUnderOwner, setEffectReturnUnderOwner] = useState(existingAbility?.effect.returnUnderOwner || false);
  const [effectSourceTarget, setEffectSourceTarget] = useState(existingAbility?.effect.sourceTarget || 'creature');
  const [effectRedirectTarget, setEffectRedirectTarget] = useState(existingAbility?.effect.redirectTarget || 'creature');
  
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
      // New fields
      duration: effectDuration,
      choice: effectChoice,
      protectionType: effectProtectionType,
      keyword: effectKeyword,
      powerChange: effectPowerChange,
      toughnessChange: effectToughnessChange,
      yourCreature: effectYourCreature,
      opponentCreature: effectOpponentCreature,
      discardType: effectDiscardType,
      position: effectPosition,
      returnUnderOwner: effectReturnUnderOwner,
      sourceTarget: effectSourceTarget,
      redirectTarget: effectRedirectTarget,
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
    if (!selectedEffectType?.requiresDuration) delete effect.duration;
    if (!selectedEffectType?.requiresChoice) delete effect.choice;
    if (!selectedEffectType?.requiresProtectionType) delete effect.protectionType;
    if (!selectedEffectType?.requiresKeyword) delete effect.keyword;
    if (!selectedEffectType?.requiresPowerToughness) {
      delete effect.powerChange;
      delete effect.toughnessChange;
    }
    if (!selectedEffectType?.requiresTwoTargets) {
      delete effect.yourCreature;
      delete effect.opponentCreature;
      delete effect.sourceTarget;
      delete effect.redirectTarget;
    }
    if (!selectedEffectType?.requiresDiscardType) delete effect.discardType;
    if (!selectedEffectType?.requiresPosition) delete effect.position;
    if (effectType !== 'flicker') delete effect.returnUnderOwner;

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
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Activation Cost *
        </label>
        <input
          type="text"
          value={cost}
          onChange={(e) => setCost(e.target.value)}
          placeholder="e.g., {T}, {1}{R}, Sacrifice a creature"
          className="w-full px-3 py-2 bg-white text-slate-900 rounded border border-amber-200/50 focus:border-amber-500 focus:outline-none"
        />
        <p className="text-xs text-slate-600 mt-1">
          Use mana symbols like {'{T}'}, {'{1}{R}'}, or describe other costs
        </p>
      </div>

      {/* Effect */}
      <div>
        <label className="block text-sm font-medium text-slate-700 mb-2">
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
            duration: effectDuration,
            choice: effectChoice,
            protectionType: effectProtectionType,
            keyword: effectKeyword,
            powerChange: effectPowerChange,
            toughnessChange: effectToughnessChange,
            yourCreature: effectYourCreature,
            opponentCreature: effectOpponentCreature,
            discardType: effectDiscardType,
            position: effectPosition,
            returnUnderOwner: effectReturnUnderOwner,
            sourceTarget: effectSourceTarget,
            redirectTarget: effectRedirectTarget,
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
            duration: effectDuration,
            choice: effectChoice,
            protectionType: effectProtectionType,
            keyword: effectKeyword,
            powerChange: effectPowerChange,
            toughnessChange: effectToughnessChange,
            yourCreature: effectYourCreature,
            opponentCreature: effectOpponentCreature,
            discardType: effectDiscardType,
            position: effectPosition,
            returnUnderOwner: effectReturnUnderOwner,
            sourceTarget: effectSourceTarget,
            redirectTarget: effectRedirectTarget,
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
              case 'duration':
                setEffectDuration(value);
                break;
              case 'choice':
                setEffectChoice(value);
                break;
              case 'protectionType':
                setEffectProtectionType(value);
                // If chosen_color, auto-set choice to color
                if (value === 'chosen_color') {
                  setEffectChoice('color');
                } else if (effectProtectionType === 'chosen_color') {
                  setEffectChoice(undefined);
                }
                break;
              case 'keyword':
                setEffectKeyword(value);
                break;
              case 'powerChange':
                setEffectPowerChange(value);
                break;
              case 'toughnessChange':
                setEffectToughnessChange(value);
                break;
              case 'yourCreature':
                setEffectYourCreature(value);
                break;
              case 'opponentCreature':
                setEffectOpponentCreature(value);
                break;
              case 'discardType':
                setEffectDiscardType(value);
                break;
              case 'position':
                setEffectPosition(value);
                break;
              case 'returnUnderOwner':
                setEffectReturnUnderOwner(value);
                break;
              case 'sourceTarget':
                setEffectSourceTarget(value);
                break;
              case 'redirectTarget':
                setEffectRedirectTarget(value);
                break;
            }
          }}
        />
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-amber-200/50">
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

