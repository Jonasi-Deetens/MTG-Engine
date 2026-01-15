'use client';

// frontend/components/builder/forms/TriggeredAbilityForm.tsx

import { useState, useEffect } from 'react';
import { useBuilderStore, TriggeredAbility, Effect, StructuredCondition } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { ConditionBuilder } from '@/components/builder/ConditionBuilder';
import { EffectFields } from './EffectFields';
import { EFFECT_TYPE_OPTIONS } from '@/lib/effectTypes';

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
  { value: 'card_enters', label: 'Card Enters Zone', hasEntersWhere: true, hasEntersFrom: true },
  { value: 'spell_cast', label: 'Spell Cast' },
];

const ZONE_OPTIONS = [
  { value: 'battlefield', label: 'Battlefield' },
  { value: 'graveyard', label: 'Graveyard' },
  { value: 'hand', label: 'Hand' },
  { value: 'library', label: 'Library' },
  { value: 'exile', label: 'Exile' },
  { value: 'command', label: 'Command Zone' },
];

const FROM_ZONE_OPTIONS = [
  { value: '', label: 'Any Zone' },
  { value: 'hand', label: 'Hand' },
  { value: 'library', label: 'Library' },
  { value: 'graveyard', label: 'Graveyard' },
  { value: 'exile', label: 'Exile' },
  { value: 'battlefield', label: 'Battlefield' },
  { value: 'command', label: 'Command Zone' },
];

const CARD_TYPE_OPTIONS = [
  { value: '', label: 'Any Card Type' },
  { value: 'creature', label: 'Creature' },
  { value: 'aura', label: 'Aura' },
  { value: 'enchantment', label: 'Enchantment' },
  { value: 'artifact', label: 'Artifact' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'planeswalker', label: 'Planeswalker' },
  { value: 'land', label: 'Land' },
  { value: 'instant', label: 'Instant' },
  { value: 'sorcery', label: 'Sorcery' },
  { value: 'permanent', label: 'Permanent' },
];

export function TriggeredAbilityForm({ abilityId, onSave, onCancel }: TriggeredAbilityFormProps) {
  const { triggeredAbilities, addTriggeredAbility, updateTriggeredAbility } = useBuilderStore();
  
  const existingAbility = abilityId ? triggeredAbilities.find((a) => a.id === abilityId) : null;
  
  const [event, setEvent] = useState(existingAbility?.event || 'enters_battlefield');
  const [condition, setCondition] = useState<StructuredCondition | string | undefined>(existingAbility?.condition);
  const [effects, setEffects] = useState<Effect[]>(existingAbility?.effects || [{ type: 'damage', amount: 0 }]);
  const [entersWhere, setEntersWhere] = useState(existingAbility?.entersWhere || 'battlefield');
  const [entersFrom, setEntersFrom] = useState(existingAbility?.entersFrom || '');
  const [cardType, setCardType] = useState(existingAbility?.cardType || '');

  const handleAddEffect = () => {
    setEffects([...effects, { type: 'damage', amount: 0 }]);
  };

  const handleRemoveEffect = (index: number) => {
    setEffects(effects.filter((_, i) => i !== index));
  };

  const handleUpdateEffect = (index: number, field: string, value: any) => {
    setEffects((prevEffects) => {
      const updated = [...prevEffects];
      updated[index] = { ...updated[index], [field]: value };

      // Clean up fields when effect type changes
      if (field === 'type') {
        const selectedType = EFFECT_TYPE_OPTIONS.find((opt) => opt.value === value);
        if (!selectedType?.requiresAmount) delete updated[index].amount;
        if (!selectedType?.requiresTarget) delete updated[index].target;
        if (!selectedType?.requiresManaType) delete updated[index].manaType;
        if (!selectedType?.requiresUntapTarget) delete updated[index].untapTarget;
        if (!selectedType?.requiresSearchFilters) {
          delete updated[index].cardType;
          delete updated[index].manaValueComparison;
          delete updated[index].manaValueComparisonValue;
          delete updated[index].manaValueComparisonSource;
          delete updated[index].differentName;
        }
        if (!selectedType?.requiresZone) delete updated[index].zone;
        if (!selectedType?.requiresAttachTarget) delete updated[index].attachTo;
        
        // Clear fromEffect if the new type doesn't support it
        if (value !== 'put_onto_battlefield' && value !== 'attach' && value !== 'return' && value !== 'exile' && value !== 'destroy') {
          delete updated[index].fromEffect;
        }
      }
      
      // When manaValueComparisonSource changes away from 'fixed_value', clear the value
      if (field === 'manaValueComparisonSource' && value !== 'fixed_value') {
        delete updated[index].manaValueComparisonValue;
      }
      
      // Validate fromEffect - must be less than current index
      if (field === 'fromEffect' && value !== undefined) {
        const fromIndex = typeof value === 'number' ? value : parseInt(value);
        if (fromIndex >= index) {
          // Invalid reference, clear it
          delete updated[index].fromEffect;
        }
      }
      
      return updated;
    });
  };

  const handleSave = () => {
    const ability: TriggeredAbility = {
      id: abilityId || `triggered-${Date.now()}`,
      event,
      condition: condition || undefined,
      effects: effects.filter((e) => e.type && (e.amount !== undefined || !['damage', 'draw', 'token', 'counters', 'life'].includes(e.type))),
      ...(event === 'card_enters' && {
        entersWhere: entersWhere || 'battlefield',
        entersFrom: entersFrom || undefined,
        cardType: cardType || undefined,
      }),
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
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
          Trigger Event *
        </label>
        <select
          value={event}
          onChange={(e) => setEvent(e.target.value)}
          className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
        >
          {EVENT_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Card Enters Zone Parameters */}
      {event === 'card_enters' && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              Enters Zone *
            </label>
            <select
              value={entersWhere}
              onChange={(e) => setEntersWhere(e.target.value)}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              Card Type <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
            </label>
            <select
              value={cardType}
              onChange={(e) => setCardType(e.target.value)}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {CARD_TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-[color:var(--theme-text-secondary)] mt-1">
              Leave as "Any Card Type" to trigger for all card types
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
              From Zone <span className="text-[color:var(--theme-text-muted)]">(optional)</span>
            </label>
            <select
              value={entersFrom}
              onChange={(e) => setEntersFrom(e.target.value)}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              {FROM_ZONE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-[color:var(--theme-text-secondary)] mt-1">
              Leave as "Any Zone" to trigger regardless of where the card came from
            </p>
          </div>
        </div>
      )}

      {/* Condition (Optional) */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)]">
            Condition (Optional)
          </label>
          {!condition && (
            <Button
              type="button"
              onClick={() => {
                setCondition({ type: 'control_count', value: 1, permanentType: 'creature' });
              }}
              variant="link"
              size="xs"
              className="text-[color:var(--theme-accent-primary)] hover:text-[color:var(--theme-accent-hover)]"
            >
              + Add Condition
            </Button>
          )}
        </div>
        {condition !== undefined && condition !== null && (
          <ConditionBuilder
            condition={condition}
            onChange={(cond) => {
              if (cond !== undefined) {
                setCondition(cond);
              }
            }}
            onRemove={() => setCondition(undefined)}
          />
        )}
      </div>

      {/* Effects */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)]">
            Effects *
          </label>
          <Button
            onClick={handleAddEffect}
            variant="ghost"
            size="xs"
            className="text-[color:var(--theme-accent-primary)] hover:text-[color:var(--theme-accent-hover)]"
          >
            + Add Effect
          </Button>
        </div>
        <div className="space-y-3">
          {effects.map((effect, index) => (
            <div key={index} className="bg-[color:var(--theme-card-hover)] rounded p-3 border border-[color:var(--theme-card-border)]">
              <div className="flex items-start justify-between mb-2">
                <span className="text-xs text-[color:var(--theme-text-secondary)]">Effect {index + 1}</span>
                {effects.length > 1 && (
                  <Button
                    onClick={() => handleRemoveEffect(index)}
                    variant="link"
                    size="xs"
                    className="text-[color:var(--theme-status-error)] hover:opacity-80"
                  >
                    Remove
                  </Button>
                )}
              </div>
              <EffectFields
                effect={effect}
                index={index}
                allEffects={effects}
                nodeId={abilityId ? `effect-${abilityId}-${index}` : undefined}
                onUpdate={(field, value) => handleUpdateEffect(index, field, value)}
              />
            </div>
          ))}
        </div>
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

