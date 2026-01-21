'use client';

import { useEffect, useState } from 'react';
import { Effect, useBuilderStore, ValidationError } from '@/store/builderStore';
import { EFFECT_TYPE_OPTIONS } from '@/lib/effectTypes';
import { abilities } from '@/lib/abilities';

// Import category components
import {
  EffectTypeField,
  ModeField,
  AmountField,
  TargetField,
  DurationField,
  MaxTargetsField,
  MinTargetsField,
} from './CommonFields';
import { DamageEffectFields, isDamageEffect } from './DamageEffectFields';
import { DrawEffectFields, isDrawEffect } from './DrawEffectFields';
import { LifeEffectFields, isLifeEffect } from './LifeEffectFields';
import { ManaEffectFields, isManaEffect } from './ManaEffectFields';

/**
 * EffectFields - Coordinator component for effect form fields
 * 
 * This component orchestrates the display of effect-specific fields
 * by delegating to category components based on the effect type.
 * 
 * Categories:
 * - DamageEffectFields: damage, damage_all, prevent_damage
 * - DrawEffectFields: draw, mill, discard, loot
 * - LifeEffectFields: gain_life, lose_life, set_life, pay_life
 * - ManaEffectFields: add_mana, ritual
 * - (Additional categories can be added)
 */

// Re-export sub-components
export * from './CommonFields';
export * from './DamageEffectFields';
export * from './DrawEffectFields';
export * from './LifeEffectFields';
export * from './ManaEffectFields';

interface EffectFieldsProps {
  effect: Effect;
  index: number;
  allEffects: Effect[];
  nodeId?: string;
  allowedEffectTypes?: string[];
  modeOptions?: Array<{ value: string; label: string }>;
  onUpdate: (field: string, value: any) => void;
}

export function EffectFields({
  effect,
  index,
  allEffects,
  nodeId,
  allowedEffectTypes,
  modeOptions,
  onUpdate,
}: EffectFieldsProps) {
  const filteredEffectTypes = allowedEffectTypes
    ? EFFECT_TYPE_OPTIONS.filter((opt) => allowedEffectTypes.includes(opt.value))
    : EFFECT_TYPE_OPTIONS;

  const selectedEffectType = EFFECT_TYPE_OPTIONS.find((opt) => opt.value === effect.type);
  
  const shouldShowMaxTargets = !!(
    selectedEffectType?.requiresTarget ||
    selectedEffectType?.requiresUntapTarget ||
    selectedEffectType?.requiresTwoTargets
  );

  const { validationErrors } = useBuilderStore();
  const [keywords, setKeywords] = useState<Array<{ value: string; label: string }>>([]);

  const getNodeErrors = (errors: ValidationError[], id?: string) =>
    id ? errors.filter((error) => error.nodeId === id) : [];

  const nodeErrors = getNodeErrors(validationErrors, nodeId);

  // Fetch keywords for gain_keyword effect
  useEffect(() => {
    if (selectedEffectType?.requiresKeyword) {
      abilities.listKeywords().then((response) => {
        setKeywords(response.keywords.map(k => ({ value: k.name, label: k.name })));
      }).catch(() => {
        setKeywords([]);
      });
    }
  }, [selectedEffectType?.requiresKeyword]);

  // Auto-select first allowed effect type
  useEffect(() => {
    if (!allowedEffectTypes || allowedEffectTypes.length === 0) return;
    if (allowedEffectTypes.includes(effect.type)) return;
    onUpdate('type', allowedEffectTypes[0]);
  }, [allowedEffectTypes, effect.type, onUpdate]);

  // Render category-specific fields based on effect type
  const renderCategoryFields = () => {
    if (isDamageEffect(effect.type)) {
      return <DamageEffectFields effect={effect} onUpdate={onUpdate} />;
    }
    if (isDrawEffect(effect.type)) {
      return <DrawEffectFields effect={effect} onUpdate={onUpdate} />;
    }
    if (isLifeEffect(effect.type)) {
      return <LifeEffectFields effect={effect} onUpdate={onUpdate} />;
    }
    if (isManaEffect(effect.type)) {
      return <ManaEffectFields effect={effect} onUpdate={onUpdate} />;
    }

    // For uncategorized effects, render generic fields based on selectedEffectType requirements
    return (
      <>
        {selectedEffectType?.requiresAmount && (
          <AmountField effect={effect} onUpdate={onUpdate} />
        )}
        {selectedEffectType?.requiresTarget && (
          <TargetField effect={effect} onUpdate={onUpdate} />
        )}
        {shouldShowMaxTargets && (
          <MaxTargetsField effect={effect} onUpdate={onUpdate} />
        )}
        {selectedEffectType?.requiresDuration && (
          <DurationField effect={effect} onUpdate={onUpdate} />
        )}
      </>
    );
  };

  return (
    <div className="space-y-3">
      {/* Effect Type Selection */}
      <EffectTypeField
        effect={effect}
        onUpdate={onUpdate}
        allowedEffectTypes={allowedEffectTypes}
      />

      {/* Mode Selection (for modal spells) */}
      <ModeField
        effect={effect}
        onUpdate={onUpdate}
        modeOptions={modeOptions}
      />

      {/* Category-specific Fields */}
      {renderCategoryFields()}

      {/* Validation Errors */}
      {nodeErrors.length > 0 && (
        <div className="rounded border border-destructive bg-destructive/10 p-2">
          <ul className="text-xs text-destructive space-y-1">
            {nodeErrors.map((error, idx) => (
              <li key={idx}>{error.message}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
