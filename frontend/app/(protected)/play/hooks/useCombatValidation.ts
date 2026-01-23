import { useMemo } from 'react';
import type { EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';

interface UseCombatValidationProps {
  gameState: EngineGameStateSnapshot | null;
  combatState: any;
  isDeclareBlockers: boolean;
  selectedBlockers: Record<string, Set<string>>;
  cardMap: EngineCardMap;
}

interface BlockerValidationResult {
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
}

/**
 * Validates blocker assignments during declare blockers step.
 * Checks for menace requirements, flying/reach restrictions, protection, etc.
 */
export function useCombatValidation({
  gameState,
  combatState,
  isDeclareBlockers,
  selectedBlockers,
  cardMap,
}: UseCombatValidationProps): BlockerValidationResult {
  const blockerErrors = useMemo(() => {
    if (!gameState || !combatState || !isDeclareBlockers) return [];
    
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const errors: string[] = [];
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;

    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = objectMap.get(attackerId);
      if (!attacker) return;

      // Menace check
      if (attacker.keywords?.includes('Menace') && blockerSet.size === 1) {
        const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
        errors.push(`${attackerLabel} has menace and needs 2+ blockers.`);
      }

      blockerSet.forEach((blockerId) => {
        const blocker = objectMap.get(blockerId);
        if (!blocker) return;
        const blockerLabel = cardMap[blockerId]?.name || blocker.name || blockerId;

        // Multiple blocking check
        if (usedBlockers.has(blockerId)) {
          errors.push(`${blockerLabel} can't block multiple attackers.`);
        }
        usedBlockers.add(blockerId);

        // Zone check
        if (blocker.zone !== 'battlefield' || blocker.phased_out) {
          errors.push(`${blockerLabel} can't block (not on battlefield).`);
          return;
        }

        // Controller check
        if (blocker.controller_id !== defendingId) {
          errors.push(`${blockerLabel} isn't controlled by the defender.`);
        }

        // Creature type check
        if (!blocker.types.includes('Creature')) {
          errors.push(`${blockerLabel} isn't a creature.`);
        }

        // Tapped check
        if (blocker.tapped) {
          errors.push(`${blockerLabel} is tapped.`);
        }

        // Flying check
        if (attacker.keywords?.includes('Flying')) {
          const canBlockFly = blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
          if (!canBlockFly) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            errors.push(`${blockerLabel} can't block ${attackerLabel} (flying).`);
          }
        }

        // Protection check
        if (attacker.protections?.length && blocker.colors?.length) {
          if (blocker.colors.some((color) => attacker.protections?.includes(color))) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            errors.push(`${attackerLabel} has protection from ${blockerLabel}.`);
          }
        }
      });
    });

    return Array.from(new Set(errors));
  }, [cardMap, combatState, gameState, isDeclareBlockers, selectedBlockers]);

  const blockerErrorMap = useMemo(() => {
    if (!gameState || !combatState || !isDeclareBlockers) return {};
    
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const map: Record<string, string[]> = {};
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;

    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = objectMap.get(attackerId);
      if (!attacker) return;

      blockerSet.forEach((blockerId) => {
        const blocker = objectMap.get(blockerId);
        if (!blocker) return;
        const blockerLabel = cardMap[blockerId]?.name || blocker.name || blockerId;

        const add = (message: string) => {
          if (!map[blockerId]) map[blockerId] = [];
          if (!map[blockerId].includes(message)) map[blockerId].push(message);
        };

        if (usedBlockers.has(blockerId)) {
          add(`${blockerLabel} can't block multiple attackers.`);
        }
        usedBlockers.add(blockerId);

        if (blocker.zone !== 'battlefield' || blocker.phased_out) {
          add(`${blockerLabel} can't block (not on battlefield).`);
          return;
        }

        if (blocker.controller_id !== defendingId) {
          add(`${blockerLabel} isn't controlled by the defender.`);
        }

        if (!blocker.types.includes('Creature')) {
          add(`${blockerLabel} isn't a creature.`);
        }

        if (blocker.tapped) {
          add(`${blockerLabel} is tapped.`);
        }

        if (attacker.keywords?.includes('Flying')) {
          const canBlockFly = blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
          if (!canBlockFly) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            add(`${blockerLabel} can't block ${attackerLabel} (flying).`);
          }
        }

        if (attacker.protections?.length && blocker.colors?.length) {
          if (blocker.colors.some((color) => attacker.protections?.includes(color))) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            add(`${attackerLabel} has protection from ${blockerLabel}.`);
          }
        }
      });
    });

    return map;
  }, [cardMap, combatState, gameState, isDeclareBlockers, selectedBlockers]);

  return { blockerErrors, blockerErrorMap };
}
