import { useEffect } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, engineApi } from '@/lib/engine';

interface UseGameSessionPersistenceProps {
  gameId: string | null;
  gameState: EngineGameStateSnapshot | null;
  setGameId: Dispatch<SetStateAction<string | null>>;
  setGameState: Dispatch<SetStateAction<EngineGameStateSnapshot | null>>;
  setCardMap: Dispatch<SetStateAction<EngineCardMap>>;
  setPriorityPlayer: Dispatch<SetStateAction<number | null>>;
  setError: Dispatch<SetStateAction<string | null>>;
}

/**
 * Handles game session persistence via localStorage and API.
 * Restores game state on mount if a stored session exists.
 */
export function useGameSessionPersistence({
  gameId,
  gameState,
  setGameId,
  setGameState,
  setCardMap,
  setPriorityPlayer,
  setError,
}: UseGameSessionPersistenceProps) {
  // Restore game ID from localStorage on mount
  useEffect(() => {
    if (gameId || gameState) return;
    const storedGameId = localStorage.getItem('play.game_id');
    if (storedGameId) {
      setGameId(storedGameId);
    }
  }, [gameId, gameState, setGameId]);

  // Load game session from API when we have a game ID but no state
  useEffect(() => {
    if (!gameId || gameState) return;
    
    const loadSession = async () => {
      try {
        const session = await engineApi.getSession(gameId);
        setGameState(session.game_state);
        
        const storedCardMap = localStorage.getItem('play.card_map');
        if (storedCardMap) {
          setCardMap(JSON.parse(storedCardMap));
        }
        
        if (typeof session.game_state.turn.priority_current_index === 'number') {
          const alivePlayers = session.game_state.players.filter((player) => !player.has_lost);
          const current = alivePlayers[session.game_state.turn.priority_current_index];
          setPriorityPlayer(current?.id ?? null);
        }
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load game session');
        localStorage.removeItem('play.game_id');
        localStorage.removeItem('play.card_map');
        setGameId(null);
      }
    };
    
    loadSession();
  }, [gameId, gameState, setCardMap, setError, setGameId, setGameState, setPriorityPlayer]);
}
