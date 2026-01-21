import { useEffect, useRef } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';

interface ResolveCleanupArgs {
  gameState: EngineGameStateSnapshot | null;
  selectedHandId: string | null;
  onResolve: () => void;
  onClearSelectedHand: (next: string | null) => void;
}

export const useResolveCleanup = ({
  gameState,
  selectedHandId,
  onResolve,
  onClearSelectedHand,
}: ResolveCleanupArgs) => {
  const previousStackCountRef = useRef<number | null>(null);

  useEffect(() => {
    if (!selectedHandId || !gameState) return;
    const stackIds = new Set(
      gameState.stack
        .map((item) => item.payload?.object_id)
        .filter((id): id is string => Boolean(id))
    );
    const inStack = stackIds.has(selectedHandId);
    const inHand = gameState.players.some((player) => player.hand.includes(selectedHandId));
    if (!inHand && !inStack) {
      onClearSelectedHand(null);
    }
  }, [gameState, onClearSelectedHand, selectedHandId]);

  useEffect(() => {
    if (!gameState) return;
    const currentCount = gameState.stack.length;
    const previousCount = previousStackCountRef.current;
    previousStackCountRef.current = currentCount;
    if (previousCount !== null && currentCount < previousCount) {
      onResolve();
    }
  }, [gameState, onResolve]);
};
