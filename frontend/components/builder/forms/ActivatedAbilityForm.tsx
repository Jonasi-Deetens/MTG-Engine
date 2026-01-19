'use client';

import { useState } from 'react';
import { useBuilderStore, ActivatedAbility, Effect } from '@/store/builderStore';
import { Button } from '@/components/ui/Button';
import { EFFECT_TYPE_OPTIONS } from '@/lib/effectTypes';
import { EffectFields } from './EffectFields';
import { CostListEditor } from '@/components/builder/CostListEditor';

interface ActivatedAbilityFormProps {
  abilityId?: string;
  onSave: () => void;
  onCancel: () => void;
}

export function ActivatedAbilityForm({ abilityId, onSave, onCancel }: ActivatedAbilityFormProps) {
  const { activatedAbilities, addActivatedAbility, updateActivatedAbility } = useBuilderStore();

  const existingAbility = abilityId ? activatedAbilities.find((a) => a.id === abilityId) : null;
  const nodeId = abilityId || existingAbility?.id;

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
      if (field === 'modeId' && !value) {
        delete updated[index].modeId;
      }
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
        if (!selectedType?.requiresDuration) delete updated[index].duration;
        if (!selectedType?.requiresChoice) delete updated[index].choice;
        if (!selectedType?.requiresProtectionType) delete updated[index].protectionType;
        if (!selectedType?.requiresKeyword) delete updated[index].keyword;
        if (!selectedType?.requiresPowerToughness) {
          delete updated[index].powerChange;
          delete updated[index].toughnessChange;
        }
        if (!selectedType?.requiresTwoTargets) {
          delete updated[index].yourCreature;
          delete updated[index].opponentCreature;
          delete updated[index].sourceTarget;
          delete updated[index].redirectTarget;
        }
        if (!selectedType?.requiresDiscardType) delete updated[index].discardType;
        if (!selectedType?.requiresPosition) delete updated[index].position;
        if (value !== 'flicker') delete updated[index].returnUnderOwner;
        if (
          value !== 'put_onto_battlefield' &&
          value !== 'attach' &&
          value !== 'return' &&
          value !== 'exile' &&
          value !== 'destroy'
        ) {
          delete updated[index].fromEffect;
        }
      }
      if (field === 'manaValueComparisonSource' && value !== 'fixed_value') {
        delete updated[index].manaValueComparisonValue;
      }
      if (field === 'fromEffect' && value !== undefined) {
        const fromIndex = typeof value === 'number' ? value : parseInt(value);
        if (fromIndex >= index) {
          delete updated[index].fromEffect;
        }
      }
      return updated;
    });
  };

  const handleAddMode = () => {
    setModalModes((prev) => [...prev, { id: `mode-${prev.length + 1}`, label: `Mode ${prev.length + 1}` }]);
  };

  const handleRemoveMode = (index: number) => {
    setModalModes((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUpdateMode = (index: number, field: 'id' | 'label', value: string) => {
    setModalModes((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], [field]: value };
      return next;
    });
  };

  const handleSave = () => {
    const allowedModes = new Set(modalModes.map((mode) => mode.id));
    const cleanedEffects = isModal
      ? effects.map((effect) => {
          if (!effect.modeId || allowedModes.has(effect.modeId)) return effect;
          const { modeId, ...rest } = effect;
          return rest;
        })
      : effects.map((effect) => {
          const { modeId, ...rest } = effect;
          return rest;
        });
    const modal = isModal
      ? {
          min: Math.max(0, Number(modalMin) || 0),
          max: modalMax === null || modalMax === undefined || modalMax === '' ? null : Math.max(1, Number(modalMax) || 1),
          modes: modalModes.filter((mode) => mode.id && mode.label),
        }
      : undefined;
    const ability: ActivatedAbility = {
      id: abilityId || `activated-${Date.now()}`,
      costs,
      effects: cleanedEffects.filter((e) => e.type && (e.amount !== undefined || !['damage', 'draw', 'token', 'counters', 'life'].includes(e.type))),
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

      <div className="space-y-3">
        <label className="flex items-center gap-2 text-sm font-medium text-[color:var(--theme-text-secondary)]">
          <input type="checkbox" checked={isModal} onChange={(e) => setIsModal(e.target.checked)} />
          Modal ability (choose modes on cast/activation)
        </label>
        {isModal && (
          <div className="space-y-3 rounded border border-[color:var(--theme-card-border)] p-3 bg-[color:var(--theme-card-hover)]">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Min modes</label>
                <input
                  type="number"
                  min="0"
                  value={modalMin}
                  onChange={(e) => setModalMin(parseInt(e.target.value, 10) || 0)}
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs text-[color:var(--theme-text-secondary)] mb-1">Max modes</label>
                <input
                  type="number"
                  min="1"
                  value={modalMax ?? ''}
                  onChange={(e) => setModalMax(e.target.value === '' ? null : parseInt(e.target.value, 10) || 1)}
                  placeholder="No limit"
                  className="w-full px-2 py-1.5 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                />
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-[color:var(--theme-text-secondary)]">Modes</span>
                <Button variant="outline" size="xs" onClick={handleAddMode}>
                  + Add Mode
                </Button>
              </div>
              {modalModes.length === 0 && (
                <div className="text-xs text-[color:var(--theme-text-muted)]">Add at least one mode.</div>
              )}
              {modalModes.map((mode, index) => (
                <div key={`mode-${index}`} className="grid grid-cols-[1fr_1fr_auto] gap-2 items-center">
                  <input
                    value={mode.id}
                    onChange={(e) => handleUpdateMode(index, 'id', e.target.value)}
                    placeholder="mode-id"
                    className="px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                  <input
                    value={mode.label}
                    onChange={(e) => handleUpdateMode(index, 'label', e.target.value)}
                    placeholder="Mode label"
                    className="px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                  <Button
                    variant="link"
                    size="xs"
                    className="text-[color:var(--theme-status-error)] hover:opacity-80"
                    onClick={() => handleRemoveMode(index)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-[color:var(--theme-text-secondary)]">Effects *</label>
          <Button variant="outline" size="xs" onClick={handleAddEffect}>
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
                nodeId={nodeId ? `effect-${nodeId}-${index}` : undefined}
                modeOptions={
                  isModal
                    ? modalModes.map((mode) => ({ value: mode.id, label: mode.label || mode.id }))
                    : []
                }
                onUpdate={(field, value) => handleUpdateEffect(index, field, value)}
              />
            </div>
          ))}
        </div>
      </div>

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

