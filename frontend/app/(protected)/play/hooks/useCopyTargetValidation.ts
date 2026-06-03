import { useEffect, useState } from 'react';
import type { EngineGameStateSnapshot } from '@/lib/engine';
import { engineApi } from '@/lib/engine';

interface CopyTargetSelection {
  objectIds: string[];
  playerIds: number[];
}

interface UseCopyTargetValidationProps {
  gameState: EngineGameStateSnapshot | null;
  copySpellConfig: { enabled: boolean; amount: number };
  hasEffectTargets: boolean;
  copyTargetSelections: CopyTargetSelection[];
  targetHints: {
    playerFilter: string;
    objectFilter: string;
    objectTypes: Set<string>;
  };
  currentPriority: number | null;
  selectedHandId: string | null;
  requiredTargetsGlobal: string[];
  distinctTargetsGlobal: string[];
  minTargetsGlobal: Record<string, number> | null;
}

/**
 * Validates copy spell target selections against game rules.
 * Only runs validation when copy spells are enabled and effect targets aren't used.
 */
export function useCopyTargetValidation({
  gameState,
  copySpellConfig,
  hasEffectTargets,
  copyTargetSelections,
  targetHints,
  currentPriority,
  selectedHandId,
  requiredTargetsGlobal,
  distinctTargetsGlobal,
  minTargetsGlobal,
}: UseCopyTargetValidationProps): string[] {
  const [copyTargetErrorsGlobal, setCopyTargetErrorsGlobal] = useState<string[]>([]);

  useEffect(() => {
    if (!copySpellConfig.enabled) {
      setCopyTargetErrorsGlobal([]);
      return;
    }
  }, [copySpellConfig.enabled]);

  useEffect(() => {
    if (!gameState || !copySpellConfig.enabled || hasEffectTargets) {
      setCopyTargetErrorsGlobal([]);
      return;
    }
    if (copyTargetSelections.length === 0) {
      setCopyTargetErrorsGlobal([]);
      return;
    }

    const contexts = copyTargetSelections.map((entry) => {
      const targets: Record<string, any> = {
        ...(entry.objectIds.length > 0 ? { target: entry.objectIds[0], targets: entry.objectIds } : {}),
        ...(entry.playerIds.length > 0 ? { target_player: entry.playerIds[0], target_players: entry.playerIds } : {}),
      };
      
      if (targetHints.playerFilter !== 'any') {
        targets.target_scope = targetHints.playerFilter;
      }
      if (targetHints.objectFilter !== 'any') {
        targets.target_object_scope = targetHints.objectFilter === 'controller' ? 'you_control' : 'opponent_control';
      }
      if (targetHints.objectTypes.size > 0) {
        targets.target_object_types = Array.from(targetHints.objectTypes);
      }

      return {
        controller_id: currentPriority,
        source_id: selectedHandId ?? undefined,
        targets,
        ...(requiredTargetsGlobal.length > 0 ? { required_targets_by_effect: { _global: requiredTargetsGlobal } } : {}),
        ...(distinctTargetsGlobal.length > 0 ? { distinct_targets_by_effect: { _global: distinctTargetsGlobal } } : {}),
        ...(Object.keys(minTargetsGlobal ?? {}).length > 0 ? { min_targets_by_effect: { _global: minTargetsGlobal } } : {}),
      };
    });

    const checkTargets = async () => {
      try {
        const response = await engineApi.execute({
          action: 'check_targets',
          game_state: gameState,
          contexts,
        });
        const checks = (response.result?.checks as Array<{ issues?: string[] }> | undefined) ?? [];
        const errors: string[] = [];
        checks.forEach((check, index) => {
          (check.issues ?? []).forEach((issue) => {
            errors.push(`Copy ${index + 1}: ${issue}`);
          });
        });
        setCopyTargetErrorsGlobal(errors);
      } catch {
        setCopyTargetErrorsGlobal([]);
      }
    };

    checkTargets();
  }, [
    copySpellConfig.enabled,
    copyTargetSelections,
    currentPriority,
    distinctTargetsGlobal,
    gameState,
    hasEffectTargets,
    minTargetsGlobal,
    requiredTargetsGlobal,
    selectedHandId,
    targetHints,
  ]);

  return copyTargetErrorsGlobal;
}
