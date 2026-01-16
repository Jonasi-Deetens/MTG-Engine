import { useEffect } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';

interface UseTurnResetArgs {
  gameState: EngineGameStateSnapshot | null;
  setReplacementChoices: React.Dispatch<React.SetStateAction<Record<string, string>>>;
  setSelectedHandId: React.Dispatch<React.SetStateAction<string | null>>;
  setSelectedBattlefieldId: React.Dispatch<React.SetStateAction<string | null>>;
  setSelectedTargetObjectIds: React.Dispatch<React.SetStateAction<string[]>>;
  setSelectedTargetPlayerIds: React.Dispatch<React.SetStateAction<number[]>>;
  setActiveAttackerId: React.Dispatch<React.SetStateAction<string | null>>;
  setSelectedDefenderId: React.Dispatch<React.SetStateAction<number | null>>;
}

export const useTurnReset = ({
  gameState,
  setReplacementChoices,
  setSelectedHandId,
  setSelectedBattlefieldId,
  setSelectedTargetObjectIds,
  setSelectedTargetPlayerIds,
  setActiveAttackerId,
  setSelectedDefenderId,
}: UseTurnResetArgs) => {
  useEffect(() => {
    if (!gameState) return;
    if (gameState.replacement_choices) {
      setReplacementChoices(gameState.replacement_choices);
    }
    setSelectedHandId(null);
    setSelectedBattlefieldId(null);
    setSelectedTargetObjectIds([]);
    setSelectedTargetPlayerIds([]);
    if (gameState.turn.step === 'declare_attackers') {
      const activeIndex = gameState.turn.active_player_index;
      const defenderIndex = (activeIndex + 1) % gameState.players.length;
      setSelectedDefenderId(gameState.players[defenderIndex]?.id ?? null);
    }
    if (gameState.turn.step === 'declare_blockers') {
      setActiveAttackerId(gameState.turn.combat_state?.attackers[0] ?? null);
    }
  }, [gameState?.turn.step, gameState?.turn.turn_number]);
};

