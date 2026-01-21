'use client';

import { useState } from 'react';
import { useBuilderStore, ActivatedAbility, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { CostListEditor } from '../CostListEditor';
import { AbilityEffectsSection } from './AbilityEffectsSection';
import { buildModalConfig, filterValidEffects, sanitizeEffectsForSave } from './abilityFormHelpers';

interface ActivatedAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

export function ActivatedAbilityForm({ abilityId, onSave, onCancel }: ActivatedAbilityFormProps) {
  const { activatedAbilities, addActivatedAbility, updateActivatedAbility } = useBuilderStore();

  const existingAbility = abilityId ? activatedAbilities.find((a) => a.id === abilityId) : null;
  const [costs, setCosts] = useState(existingAbility?.costs?.length ? existingAbility.costs : [{ type: 'tap_self' }]);
  const [timing, setTiming] = useState(existingAbility?.timing || 'any');
  const [limitScope, setLimitScope] = useState(existingAbility?.limit?.scope || 'none');
  const [limitMax, setLimitMax] = useState(existingAbility?.limit?.max || 1);
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
    const ability: ActivatedAbility = {
      id: abilityId || `activated-${Date.now()}`,
      costs,
      effects: filterValidEffects(cleanedEffects),
      ...(modal ? { modal } : {}),
      timing: timing === 'any' ? undefined : timing,
      limit: limitScope === 'none' ? undefined : { scope: limitScope, max: limitMax },
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
      <CostListEditor label="Activation Costs" value={costs} onChange={setCosts} />

      <div>
        <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)] mb-2">
          Activation Timing
        </label>
        <select
          value={timing}
          onChange={(e) => setTiming(e.target.value)}
          className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
        >
          <option value="any">Any time (instant speed)</option>
          <option value="sorcery">Only as a sorcery</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Activation Limit</label>
          <select
            value={limitScope}
            onChange={(e) => setLimitScope(e.target.value)}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            <option value="none">No limit</option>
            <option value="turn">Once per turn</option>
            <option value="phase">Once per phase</option>
            <option value="combat">Once per combat</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Max Uses</label>
          <input
            type="number"
            min="1"
            value={limitMax}
            onChange={(e) => setLimitMax(parseInt(e.target.value, 10) || 1)}
            disabled={limitScope === 'none'}
            className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          />
        </div>
      </div>

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

