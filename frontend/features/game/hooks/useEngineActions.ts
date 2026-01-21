import { useCallback } from 'react';
import { engineApi, EngineActionRequest, EngineActionResponse, EngineGameStateSnapshot } from '@/lib/engine';

/**
 * Pending search choice from the engine when stack resolution needs player input.
 */
export interface PendingSearchChoice {
  node_id: string;
  player_id: number;
  zone: string;
  options: Array<{ id: string; name: string; mana_value?: number; type_line?: string }>;
  min_selections: number;
  max_selections: number;
  source_id?: string;
}

interface UseEngineActionsArgs {
  gameState: EngineGameStateSnapshot | null;
  gameId: string | null;
  replacementChoices: Record<string, string>;
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
  setPriorityPlayer: React.Dispatch<React.SetStateAction<number | null>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  setPendingSearchChoices?: React.Dispatch<React.SetStateAction<PendingSearchChoice[]>>;
}

export const useEngineActions = ({
  gameState,
  gameId,
  replacementChoices,
  setGameState,
  setPriorityPlayer,
  setLoading,
  setError,
  setPendingSearchChoices,
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
        
        // Handle pending search choices from stack resolution
        if (response.result?.status === 'needs_input' && response.result?.pending_search_choices) {
          setPendingSearchChoices?.(response.result.pending_search_choices);
        } else {
          // Clear pending choices when resolution proceeds
          setPendingSearchChoices?.([]);
        }
        
        return response;
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Engine action failed');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [gameId, gameState, replacementChoices, setError, setGameState, setLoading, setPriorityPlayer, setPendingSearchChoices]
  );

  return { runEngineAction };
};

