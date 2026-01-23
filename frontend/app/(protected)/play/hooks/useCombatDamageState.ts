import { useEffect, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import type { EngineGameStateSnapshot } from '@/lib/engine';
import {
  buildDefaultCombatAssignments,
  hasFirstStrikeCombat as computeHasFirstStrikeCombat,
  isEligibleForCombatPass,
} from '@/lib/combatDamage';

interface UseCombatDamageStateProps {
  gameState: EngineGameStateSnapshot | null;
}

interface UseCombatDamageStateResult {
  combatDamageAssignments: Record<string, Record<string, number>>;
  setCombatDamageAssignments: Dispatch<SetStateAction<Record<string, Record<string, number>>>>;
  hasFirstStrikeCombat: boolean;
  combatDamagePass: 'first_strike' | 'regular' | null;
  hasManualCombatChoices: boolean;
}

/**
 * Manages combat damage assignments and first strike phases.
 */
export function useCombatDamageState({
  gameState,
}: UseCombatDamageStateProps): UseCombatDamageStateResult {
  const [combatDamageAssignments, setCombatDamageAssignments] = useState<Record<string, Record<string, number>>>({});

  const hasFirstStrikeCombat = useMemo(() => computeHasFirstStrikeCombat(gameState), [gameState]);

  const combatDamagePass = useMemo(() => {
    if (!hasFirstStrikeCombat) return null;
    const resolved = gameState?.turn?.combat_state?.first_strike_resolved;
    return resolved ? 'regular' : 'first_strike';
  }, [gameState, hasFirstStrikeCombat]);

  const hasManualCombatChoices = useMemo(() => {
    if (!gameState?.turn?.combat_state) return false;
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    
    return gameState.turn.combat_state.attackers.some((attackerId) => {
      const attacker = objectMap.get(attackerId);
      if (!isEligibleForCombatPass(attacker?.keywords, combatDamagePass ?? undefined)) return false;
      
      const blockers = gameState.turn.combat_state?.blockers?.[attackerId] ?? [];
      if (blockers.length > 1) return true;
      if (blockers.length > 0 && attacker?.keywords?.includes('Trample')) return true;
      
      return false;
    });
  }, [combatDamagePass, gameState]);

  // Auto-populate damage assignments when entering combat damage step
  useEffect(() => {
    if (!gameState) return;
    
    if (gameState.turn.step === 'combat_damage') {
      setCombatDamageAssignments(buildDefaultCombatAssignments(gameState, combatDamagePass ?? undefined));
      return;
    }
    
    if (Object.keys(combatDamageAssignments).length > 0) {
      setCombatDamageAssignments({});
    }
  }, [combatDamagePass, gameState?.turn.step, gameState?.turn.turn_number]);

  return {
    combatDamageAssignments,
    setCombatDamageAssignments,
    hasFirstStrikeCombat,
    combatDamagePass,
    hasManualCombatChoices,
  };
}
