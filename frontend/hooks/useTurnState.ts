import { useMemo } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';

interface UseTurnStateArgs {
  gameState: EngineGameStateSnapshot | null;
  priorityPlayer: number | null;
}

export const useTurnState = ({ gameState, priorityPlayer }: UseTurnStateArgs) => {
  const currentPriority =
    gameState?.turn.priority_current_index ??
    priorityPlayer ??
    gameState?.turn.active_player_index ??
    0;
  const activePlayerIndex = gameState?.turn.active_player_index ?? 0;
  const currentStep = gameState?.turn.step ?? '';
  const isMainPhase = currentStep === 'precombat_main' || currentStep === 'postcombat_main';
  const isDeclareAttackers = currentStep === 'declare_attackers';
  const isDeclareBlockers = currentStep === 'declare_blockers';
  const isCombatDamage = currentStep === 'combat_damage';
  const combatState = gameState?.turn.combat_state;

  const isPriorityActivePlayer = currentPriority === activePlayerIndex;
  const isPriorityDefender = useMemo(() => {
    if (combatState?.defending_player_id == null) return false;
    return currentPriority === combatState.defending_player_id;
  }, [combatState?.defending_player_id, currentPriority]);

  return {
    currentPriority,
    activePlayerIndex,
    currentStep,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    combatState,
    isPriorityActivePlayer,
    isPriorityDefender,
  };
};

