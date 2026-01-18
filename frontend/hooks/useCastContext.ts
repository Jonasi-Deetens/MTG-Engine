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
    return {
      controller_id: currentPriority,
      source_id: sourceIdOverride ?? selectedHandId ?? undefined,
      targets: {
        ...(selectedTargetObjectIds.length > 0 ? { target: selectedTargetObjectIds[0] } : {}),
        ...(selectedTargetObjectIds.length > 0
          ? { targets: selectedTargetObjectIds.slice(0, maxObjectTargets ?? selectedTargetObjectIds.length) }
          : {}),
        ...(selectedTargetPlayerIds.length > 0 ? { target_player: selectedTargetPlayerIds[0] } : {}),
        ...(selectedTargetPlayerIds.length > 0
          ? { target_players: selectedTargetPlayerIds.slice(0, maxPlayerTargets ?? selectedTargetPlayerIds.length) }
          : {}),
        ...(selectedTargetObjectIds.length > 0 ? { spell_target: selectedTargetObjectIds[0] } : {}),
        ...(selectedTargetObjectIds.length > 0
          ? { spell_targets: selectedTargetObjectIds.slice(0, maxObjectTargets ?? selectedTargetObjectIds.length) }
          : {}),
      },
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
  ]);

  return { buildCastContext };
};

