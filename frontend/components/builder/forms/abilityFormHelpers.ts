import { Effect, ModalChoiceConfig } from '@/store/builderStore';
import { EFFECT_TYPE_OPTIONS } from '@/lib/effectTypes';

const EFFECTS_REQUIRE_AMOUNT = new Set(['damage', 'draw', 'token', 'counters', 'life']);

export const updateEffectsWithField = (
  prevEffects: Effect[],
  index: number,
  field: string,
  value: any
) => {
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
    const fromIndex = typeof value === 'number' ? value : parseInt(value, 10);
    if (Number.isFinite(fromIndex) && fromIndex >= index) {
      delete updated[index].fromEffect;
    }
  }

  return updated;
};

export const sanitizeEffectsForSave = (
  effects: Effect[],
  isModal: boolean,
  modalModes: Array<{ id: string; label: string }>
) => {
  const allowedModes = new Set(modalModes.map((mode) => mode.id));
  return isModal
    ? effects.map((effect) => {
        if (!effect.modeId || allowedModes.has(effect.modeId)) return effect;
        const { modeId, ...rest } = effect;
        return rest;
      })
    : effects.map((effect) => {
        const { modeId, ...rest } = effect;
        return rest;
      });
};

export const buildModalConfig = (
  isModal: boolean,
  modalMin: number,
  modalMax: number | null | undefined | '',
  modalModes: Array<{ id: string; label: string }>
): ModalChoiceConfig | undefined => {
  if (!isModal) return undefined;
  const maxValue =
    modalMax === null || modalMax === undefined || modalMax === ''
      ? null
      : Math.max(1, Number(modalMax) || 1);
  return {
    min: Math.max(0, Number(modalMin) || 0),
    max: maxValue,
    modes: modalModes.filter((mode) => mode.id && mode.label),
  };
};

export const filterValidEffects = (effects: Effect[]) =>
  effects.filter(
    (effect) =>
      effect.type &&
      (effect.amount !== undefined || !EFFECTS_REQUIRE_AMOUNT.has(effect.type))
  );
