import { useCallback } from 'react';
import { EngineActionRequest } from '@/lib/engine';
import { ManaPaymentDetail } from '@/lib/manaPayment';

interface UseCastContextArgs {
  currentPriority: number | null;
  selectedHandId: string | null;
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
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
  enterChoices: Record<string, string>;
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
  enterChoices,
}: UseCastContextArgs) => {
  const buildCastContext = useCallback((
    sourceIdOverride?: string | null,
    wardOptions?: WardOptions
  ): EngineActionRequest['context'] => {
    const choices: Record<string, any> = {};
    if (Object.keys(enterChoices).length > 0) {
      choices.enter_choices = enterChoices;
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
    if (copyChooseNewTargets) {
      choices.copy_choose_new_targets = true;
    }
    if (copyTargetsList.length > 0) {
      choices.copy_targets_list = copyTargetsList;
    }
    const usePerEffectTargets = !!(targetsByEffect && Object.keys(targetsByEffect).length > 0);
    const targets = usePerEffectTargets
      ? {}
      : {
          ...(selectedTargetObjectIds.length > 0 ? { target: selectedTargetObjectIds[0] } : {}),
          ...(selectedTargetObjectIds.length > 0
            ? { targets: selectedTargetObjectIds.slice(0, maxObjectTargets ?? selectedTargetObjectIds.length) }
            : {}),
          ...(selectedTargetPlayerIds.length > 0 ? { target_player: selectedTargetPlayerIds[0] } : {}),
          ...(selectedTargetPlayerIds.length > 0
            ? { target_players: selectedTargetPlayerIds.slice(0, maxPlayerTargets ?? selectedTargetPlayerIds.length) }
            : {}),
          ...(targetPlayerFilter !== 'any' ? { target_scope: targetPlayerFilter } : {}),
          ...(targetObjectFilter !== 'any'
            ? { target_object_scope: targetObjectFilter === 'controller' ? 'you_control' : 'opponent_control' }
            : {}),
          ...(targetObjectTypes.length > 0 ? { target_object_types: targetObjectTypes } : {}),
          ...(selectedTargetObjectIds.length > 0 ? { spell_target: selectedTargetObjectIds[0] } : {}),
          ...(selectedTargetObjectIds.length > 0
            ? { spell_targets: selectedTargetObjectIds.slice(0, maxObjectTargets ?? selectedTargetObjectIds.length) }
            : {}),
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
    maxObjectTargets,
    maxPlayerTargets,
    selectedHandId,
    selectedTargetObjectIds,
    selectedTargetPlayerIds,
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
  ]);

  return { buildCastContext };
};

