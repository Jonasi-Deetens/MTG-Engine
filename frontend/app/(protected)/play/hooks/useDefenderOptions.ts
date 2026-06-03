import { useMemo } from 'react';
import type { EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';

interface UseDefenderOptionsProps {
  gameState: EngineGameStateSnapshot | null;
  activePlayerIndex: number;
  cardMap: EngineCardMap;
}

interface DefenderOption {
  value: string;
  label: string;
}

/**
 * Computes available defender options (players and planeswalkers) for attack declarations.
 */
export function useDefenderOptions({
  gameState,
  activePlayerIndex,
  cardMap,
}: UseDefenderOptionsProps): DefenderOption[] {
  return useMemo(() => {
    if (!gameState) return [];

    const activePlayerId = gameState.players[activePlayerIndex]?.id;
    const options: DefenderOption[] = [];

    // Add opponent players
    gameState.players.forEach((player) => {
      if (player.id === activePlayerId) return;
      options.push({ value: `player:${player.id}`, label: `Player ${player.id + 1}` });
    });

    // Add opponent planeswalkers
    gameState.objects.forEach((obj) => {
      if (obj.zone !== 'battlefield') return;
      if (!obj.types?.includes('Planeswalker')) return;
      if (obj.controller_id === activePlayerId) return;
      const label = cardMap[obj.id]?.name || obj.name || obj.id;
      options.push({ value: `planeswalker:${obj.id}`, label: `${label} (Planeswalker)` });
    });

    return options;
  }, [activePlayerIndex, cardMap, gameState]);
}
