'use client';

import { useState } from 'react';
import { useBuilderStore, Effect, SpellAbility } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { AbilityEffectsSection } from './AbilityEffectsSection';
import { buildModalConfig, filterValidEffects, sanitizeEffectsForSave } from './abilityFormHelpers';

interface SpellAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

export function SpellAbilityForm({ abilityId, onSave, onCancel }: SpellAbilityFormProps) {
  const { spellAbilities, addSpellAbility, updateSpellAbility } = useBuilderStore();
  const existingAbility = abilityId ? spellAbilities.find((a) => a.id === abilityId) : null;

  const [effects, setEffects] = useState<Effect[]>(
    existingAbility?.effects?.length ? existingAbility.effects : [{ type: 'damage', amount: 0 }]
  );
  const [isModal, setIsModal] = useState(!!existingAbility?.modal);
  const [modalMin, setModalMin] = useState(existingAbility?.modal?.min ?? 1);
  const [modalMax, setModalMax] = useState(existingAbility?.modal?.max ?? 1);
  const [modalModes, setModalModes] = useState(existingAbility?.modal?.modes ?? []);

  const handleSave = () => {
    const cleanedEffects = sanitizeEffectsForSave(effects, isModal, modalModes);
    const modal = buildModalConfig(isModal, modalMin, modalMax, modalModes);
    const ability: SpellAbility = {
      id: abilityId || `spell-${Date.now()}`,
      effects: filterValidEffects(cleanedEffects),
      ...(modal ? { modal } : {}),
    };

    if (abilityId) {
      updateSpellAbility(abilityId, ability);
    } else {
      addSpellAbility(ability);
    }
    onSave();
  };

  return (
    <div className="space-y-6">
      <AbilityEffectsSection
        effects={effects}
        setEffects={setEffects}
        isModal={isModal}
        setIsModal={setIsModal}
        modalMin={modalMin}
        setModalMin={setModalMin}
        modalMax={modalMax}
        setModalMax={setModalMax}
        modalModes={modalModes}
        setModalModes={setModalModes}
      />

      <div className="flex gap-3 pt-4 border-t border-[color:var(--theme-border-default)]">
        <Button onClick={handleSave} variant="primary" className="flex-1">
          Save
        </Button>
        <Button onClick={onCancel} variant="secondary" className="flex-1">
          Cancel
        </Button>
      </div>
    </div>
  );
}
