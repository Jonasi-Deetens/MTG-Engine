import { useCallback } from 'react';
import { EngineActionRequest } from '@/lib/engine';

interface UseCastContextArgs {
  currentPriority: number | null;
  selectedHandId: string | null;
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  maxObjectTargets?: number;
  maxPlayerTargets?: number;
  enterChoices: Record<string, string>;
}

export const useCastContext = ({
  currentPriority,
  selectedHandId,
  selectedTargetObjectIds,
  selectedTargetPlayerIds,
  maxObjectTargets,
  maxPlayerTargets,
  enterChoices,
}: UseCastContextArgs) => {
  const buildCastContext = useCallback((sourceIdOverride?: string | null): EngineActionRequest['context'] => ({
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
    ...(Object.keys(enterChoices).length > 0 ? { choices: { enter_choices: enterChoices } } : {}),
  }), [
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

