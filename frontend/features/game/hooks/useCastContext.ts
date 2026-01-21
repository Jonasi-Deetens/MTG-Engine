import { useCallback } from 'react';
import { EngineActionRequest } from '@/lib/engine';
import { ManaPaymentDetail } from '@/lib/manaPayment';

interface UseCastContextArgs {
  currentPriority: number | null;
  selectedHandId: string | null;
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  useStackTargets?: boolean;
  maxObjectTargets?: number;
  maxPlayerTargets?: number;
  targetPlayerFilter?: 'any' | 'opponent' | 'controller';
  targetObjectFilter?: 'any' | 'opponent' | 'controller';
  targetObjectTypes?: string[];
  targetsByEffect?: Record<string, Record<string, any>>;
  requiredTargetsByEffect?: Record<string, string[]>;
  requiredTargetsGlobal?: string[];
  distinctTargetsByEffect?: Record<string, string[]>;
  distinctTargetsGlobal?: string[];
  minTargetsByEffect?: Record<string, Record<string, number>>;
  minTargetsGlobal?: Record<string, number>;
  copyChooseNewTargets?: boolean;
  copyTargetsList?: Array<Record<string, any>>;
  copyTargetsByEffectList?: Array<Record<string, Record<string, any>>>;
  copyRequiredTargetsByEffectList?: Array<Record<string, string[]>>;
  copyDistinctTargetsByEffectList?: Array<Record<string, string[]>>;
  copyMinTargetsByEffectList?: Array<Record<string, Record<string, number>>>;
  enterChoices: Record<string, string>;
  modalChoices?: string[];
  optionalCostSelections?: Record<string, number>;
  optionalCostPayments?: any;
  conspireTaps?: string[];
  spliceCards?: string[];
  splicePayments?: any;
}

type WardOptions = {
  wardAutoPay?: boolean;
  wardPayments?: Record<string, any>;
  costPayments?: any;
  additionalCostPayments?: any;
  alternativeCostTag?: string | null;
  alternativeCostPayments?: any;
};

export const useCastContext = ({
  currentPriority,
  selectedHandId,
  selectedTargetObjectIds,
  selectedTargetPlayerIds,
  useStackTargets = false,
  maxObjectTargets,
  maxPlayerTargets,
  targetPlayerFilter = 'any',
  targetObjectFilter = 'any',
  targetObjectTypes = [],
  targetsByEffect,
  requiredTargetsByEffect,
  requiredTargetsGlobal = [],
  distinctTargetsByEffect,
  distinctTargetsGlobal = [],
  minTargetsByEffect,
  minTargetsGlobal = {},
  copyChooseNewTargets = false,
  copyTargetsList = [],
  copyTargetsByEffectList = [],
  copyRequiredTargetsByEffectList = [],
  copyDistinctTargetsByEffectList = [],
  copyMinTargetsByEffectList = [],
  enterChoices,
  modalChoices = [],
  optionalCostSelections = {},
  optionalCostPayments,
  conspireTaps = [],
  spliceCards = [],
  splicePayments,
}: UseCastContextArgs) => {
  const buildCastContext = useCallback((
    sourceIdOverride?: string | null,
    wardOptions?: WardOptions
  ): EngineActionRequest['context'] => {
    const choices: Record<string, any> = {};
    if (Object.keys(enterChoices).length > 0) {
      choices.enter_choices = enterChoices;
    }
    if (modalChoices.length > 0) {
      choices.chosen_modes = modalChoices;
    }
    if (wardOptions?.wardAutoPay) {
      choices.ward_auto_pay = true;
    }
    if (wardOptions?.wardPayments) {
      choices.ward_payments = wardOptions.wardPayments;
    }
    if (wardOptions?.costPayments) {
      choices.cost_payments = wardOptions.costPayments;
    }
    if (wardOptions?.additionalCostPayments) {
      choices.additional_cost_payments = wardOptions.additionalCostPayments;
    }
    if (wardOptions?.alternativeCostTag) {
      choices.alternative_cost_tag = wardOptions.alternativeCostTag;
    }
    if (wardOptions?.alternativeCostPayments) {
      choices.alternative_cost_payments = wardOptions.alternativeCostPayments;
    }
    if (Object.keys(optionalCostSelections).length > 0) {
      choices.optional_costs = optionalCostSelections;
    }
    if (optionalCostPayments) {
      choices.optional_cost_payments = optionalCostPayments;
    }
    if (conspireTaps.length > 0) {
      choices.conspire_taps = conspireTaps;
    }
    if (spliceCards.length > 0) {
      choices.splice_cards = spliceCards;
    }
    if (splicePayments) {
      choices.splice_payments = splicePayments;
    }
    if (copyChooseNewTargets) {
      choices.copy_choose_new_targets = true;
    }
    if (copyTargetsList.length > 0) {
      choices.copy_targets_list = copyTargetsList;
    }
    if (copyTargetsByEffectList.length > 0) {
      choices.copy_targets_by_effect_list = copyTargetsByEffectList;
    }
    if (copyRequiredTargetsByEffectList.length > 0) {
      choices.copy_required_targets_by_effect_list = copyRequiredTargetsByEffectList;
    }
    if (copyDistinctTargetsByEffectList.length > 0) {
      choices.copy_distinct_targets_by_effect_list = copyDistinctTargetsByEffectList;
    }
    if (copyMinTargetsByEffectList.length > 0) {
      choices.copy_min_targets_by_effect_list = copyMinTargetsByEffectList;
    }
    const usePerEffectTargets = !!(targetsByEffect && Object.keys(targetsByEffect).length > 0);
    const objectTargets = selectedTargetObjectIds.slice(0, maxObjectTargets ?? selectedTargetObjectIds.length);
    const playerTargets = selectedTargetPlayerIds.slice(0, maxPlayerTargets ?? selectedTargetPlayerIds.length);
    const targets = usePerEffectTargets
      ? {}
      : {
          ...(objectTargets.length > 0 && !useStackTargets ? { target: objectTargets[0] } : {}),
          ...(objectTargets.length > 0 && !useStackTargets ? { targets: objectTargets } : {}),
          ...(objectTargets.length > 0 && useStackTargets ? { spell_target: objectTargets[0] } : {}),
          ...(objectTargets.length > 0 && useStackTargets ? { spell_targets: objectTargets } : {}),
          ...(playerTargets.length > 0 ? { target_player: playerTargets[0] } : {}),
          ...(playerTargets.length > 0 ? { target_players: playerTargets } : {}),
          ...(targetPlayerFilter !== 'any' ? { target_scope: targetPlayerFilter } : {}),
          ...(targetObjectFilter !== 'any'
            ? { target_object_scope: targetObjectFilter === 'controller' ? 'you_control' : 'opponent_control' }
            : {}),
          ...(targetObjectTypes.length > 0 ? { target_object_types: targetObjectTypes } : {}),
        };
    return {
      controller_id: currentPriority,
      source_id: sourceIdOverride ?? selectedHandId ?? undefined,
      targets,
      ...(usePerEffectTargets ? { targets_by_effect: targetsByEffect } : {}),
      ...(usePerEffectTargets && requiredTargetsByEffect
        ? { required_targets_by_effect: requiredTargetsByEffect }
        : {}),
      ...(usePerEffectTargets && distinctTargetsByEffect
        ? { distinct_targets_by_effect: distinctTargetsByEffect }
        : {}),
      ...(usePerEffectTargets && minTargetsByEffect ? { min_targets_by_effect: minTargetsByEffect } : {}),
      ...(!usePerEffectTargets && requiredTargetsGlobal.length > 0
        ? { required_targets_by_effect: { _global: requiredTargetsGlobal } }
        : {}),
      ...(!usePerEffectTargets && distinctTargetsGlobal.length > 0
        ? { distinct_targets_by_effect: { _global: distinctTargetsGlobal } }
        : {}),
      ...(!usePerEffectTargets && Object.keys(minTargetsGlobal).length > 0
        ? { min_targets_by_effect: { _global: minTargetsGlobal } }
        : {}),
      ...(Object.keys(choices).length > 0 ? { choices } : {}),
    };
  }, [
    currentPriority,
    enterChoices,
    modalChoices,
    optionalCostSelections,
    optionalCostPayments,
    conspireTaps,
    spliceCards,
    splicePayments,
    maxObjectTargets,
    maxPlayerTargets,
    selectedHandId,
    selectedTargetObjectIds,
    selectedTargetPlayerIds,
    useStackTargets,
    targetPlayerFilter,
    targetObjectFilter,
    targetObjectTypes,
    targetsByEffect,
    requiredTargetsByEffect,
    requiredTargetsGlobal,
    distinctTargetsByEffect,
    distinctTargetsGlobal,
    minTargetsByEffect,
    minTargetsGlobal,
    copyChooseNewTargets,
    copyTargetsList,
    copyTargetsByEffectList,
    copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList,
  ]);

  return { buildCastContext };
};

