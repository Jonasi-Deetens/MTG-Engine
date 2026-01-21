'use client';

import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, engineApi } from '@/lib/engine';

/**
 * GameContext - Core game state management
 * 
 * Responsible for:
 * - Game session state (gameId, gameState, cardMap)
 * - Loading and error states
 * - Engine action execution
 * - Priority player tracking
 */

export interface GameContextValue {
  // Core state
  gameId: string | null;
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  loading: boolean;
  error: string | null;
  priorityPlayer: number | null;
  
  // State setters (for composition with other contexts)
  setGameId: (id: string | null) => void;
  setGameState: (state: EngineGameStateSnapshot | null) => void;
  setCardMap: (map: EngineCardMap) => void;
  setPriorityPlayer: (player: number | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions
  runEngineAction: (
    action: string,
    payload?: Record<string, any>,
    replacementChoices?: Record<string, string>
  ) => Promise<void>;
}

const GameContext = createContext<GameContextValue | null>(null);

export function GameProvider({ children }: { children: React.ReactNode }) {
  const value = useGameInternal();
  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
}

function useGameInternal(): GameContextValue {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);

  // Restore game session from localStorage
  useEffect(() => {
    if (gameId || gameState) return;
    const storedGameId = localStorage.getItem('play.game_id');
    if (storedGameId) {
      setGameId(storedGameId);
    }
  }, [gameId, gameState]);

  // Load game session when gameId is set
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
  }, [gameId, gameState]);

  // Execute engine action
  const runEngineAction = useCallback(
    async (
      action: string,
      payload?: Record<string, any>,
      replacementChoices?: Record<string, string>
    ) => {
      if (!gameState) return;
      setLoading(true);
      setError(null);

      try {
        const response = await engineApi.execute({
          action,
          game_id: gameId ?? undefined,
          game_state: gameState,
          ...payload,
          replacement_choices: replacementChoices,
        });

        if (response.game_state) {
          setGameState(response.game_state);
        }

        // Update priority player from response
        if (typeof response.game_state?.turn?.priority_current_index === 'number') {
          const alivePlayers = response.game_state.players.filter((player: any) => !player.has_lost);
          const current = alivePlayers[response.game_state.turn.priority_current_index];
          setPriorityPlayer(current?.id ?? null);
        }
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Action failed');
      } finally {
        setLoading(false);
      }
    },
    [gameId, gameState]
  );

  return {
    gameId,
    gameState,
    cardMap,
    loading,
    error,
    priorityPlayer,
    setGameId,
    setGameState,
    setCardMap,
    setPriorityPlayer,
    setLoading,
    setError,
    runEngineAction,
  };
}
