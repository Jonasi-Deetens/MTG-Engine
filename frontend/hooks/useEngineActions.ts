import { useCallback } from 'react';
import { engineApi, EngineActionRequest, EngineActionResponse, EngineGameStateSnapshot } from '@/lib/engine';

interface UseEngineActionsArgs {
  gameState: EngineGameStateSnapshot | null;
  gameId: string | null;
  replacementChoices: Record<string, string>;
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
  setPriorityPlayer: React.Dispatch<React.SetStateAction<number | null>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}

export const useEngineActions = ({
  gameState,
  gameId,
  replacementChoices,
  setGameState,
  setPriorityPlayer,
  setLoading,
  setError,
}: UseEngineActionsArgs) => {
  const runEngineAction = useCallback(
    async (
      action: EngineActionRequest['action'],
      payload: Partial<EngineActionRequest> = {}
    ): Promise<EngineActionResponse | null> => {
      if (!gameState) return null;
      setLoading(true);
      setError(null);
      try {
        const trimmedDebugLog = Array.isArray(gameState.debug_log) ? gameState.debug_log.slice(-200) : [];
        const trimmedGameState = { ...gameState, debug_log: trimmedDebugLog };
        const response = await engineApi.execute({
          action,
          ...(gameId
            ? { game_id: gameId, replacement_choices: replacementChoices }
            : { game_state: { ...trimmedGameState, replacement_choices: replacementChoices } }),
          ...payload,
        });
        setGameState(response.game_state);
        if (typeof response.result?.current_priority === 'number') {
          setPriorityPlayer(response.result.current_priority);
        } else if (typeof response.game_state.turn.priority_current_index === 'number') {
          const alivePlayers = response.game_state.players.filter((player) => !player.has_lost);
          const current = alivePlayers[response.game_state.turn.priority_current_index];
          setPriorityPlayer(current?.id ?? null);
        }
        return response;
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Engine action failed');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [gameId, gameState, replacementChoices, setError, setGameState, setLoading, setPriorityPlayer]
  );

  return { runEngineAction };
};

