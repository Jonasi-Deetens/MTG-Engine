import { useCallback, useEffect, useRef, useState } from 'react';
import { effects } from '@/lib/effects';
import { EngineCardMap, EngineGameStateSnapshot } from '@/lib/engine';

interface UseEffectGraphsArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
}

export const useEffectGraphs = ({ gameState, cardMap, setGameState }: UseEffectGraphsArgs) => {
  const [effectGraphs, setEffectGraphs] = useState<Record<string, any>>({});
  const missingCardIdsRef = useRef(new Set<string>());
  const inFlightCardIdsRef = useRef(new Set<string>());

  const filterFetchableCardIds = useCallback(
    (cardIds: string[]) =>
      cardIds.filter(
        (cardId) =>
          !effectGraphs[cardId] &&
          !missingCardIdsRef.current.has(cardId) &&
          !inFlightCardIdsRef.current.has(cardId)
      ),
    [effectGraphs]
  );

  const markInFlight = useCallback((cardIds: string[]) => {
    cardIds.forEach((cardId) => inFlightCardIdsRef.current.add(cardId));
  }, []);

  const clearInFlight = useCallback((cardIds: string[]) => {
    cardIds.forEach((cardId) => inFlightCardIdsRef.current.delete(cardId));
  }, []);

  const markMissing = useCallback((cardIds: string[]) => {
    cardIds.forEach((cardId) => missingCardIdsRef.current.add(cardId));
  }, []);

  const applyEffectGraphsToState = useCallback(
    (graphsByCardId: Record<string, any>) => {
      if (Object.keys(graphsByCardId).length === 0) return;
      setEffectGraphs((prev) => ({ ...prev, ...graphsByCardId }));
      setGameState((prevState) => {
        if (!prevState) return prevState;
        const updatedObjects = prevState.objects.map((obj) => {
          const objCardId = cardMap[obj.id]?.card_id;
          const graph = objCardId ? graphsByCardId[objCardId] : undefined;
          if (!graph) return obj;
          if (obj.effect_graphs && obj.effect_graphs.length > 0) return obj;
          return {
            ...obj,
            effect_graphs: [graph],
          };
        });
        return { ...prevState, objects: updatedObjects };
      });
    },
    [cardMap, setGameState]
  );

  const loadEffectGraphForObject = useCallback(
    async (objectId: string) => {
      const card = cardMap[objectId];
      const cardId = card?.card_id;
      if (!cardId || effectGraphs[cardId]) return;
      if (missingCardIdsRef.current.has(cardId) || inFlightCardIdsRef.current.has(cardId)) return;
      markInFlight([cardId]);
      try {
        const response = await effects.getCardEffectGraph(cardId);
        if (response?.effect_graph) {
          applyEffectGraphsToState({ [cardId]: response.effect_graph });
        }
      } catch (err: any) {
        if (err?.status === 404) {
          markMissing([cardId]);
        } else {
          console.error('Failed to load effect graph:', err);
        }
      } finally {
        clearInFlight([cardId]);
      }
    },
    [
      applyEffectGraphsToState,
      cardMap,
      clearInFlight,
      effectGraphs,
      markInFlight,
      markMissing,
    ]
  );

  useEffect(() => {
    if (!gameState) return;
    const cardIdsToFetch = filterFetchableCardIds(
      Array.from(
        new Set(
          gameState.objects
            .filter((obj) => obj.zone === 'battlefield' || obj.zone === 'command')
            .map((obj) => cardMap[obj.id]?.card_id)
            .filter((cardId): cardId is string => Boolean(cardId))
        )
      )
    );

    if (cardIdsToFetch.length === 0) return;

    const loadGraphs = async () => {
      const chunkSize = 10;
      for (let i = 0; i < cardIdsToFetch.length; i += chunkSize) {
        const chunk = cardIdsToFetch.slice(i, i + chunkSize);
        if (chunk.length === 0) continue;
        markInFlight(chunk);
        try {
          for (const cardId of chunk) {
            try {
              const response = await effects.getCardEffectGraph(cardId);
              if (response?.effect_graph) {
                applyEffectGraphsToState({ [cardId]: response.effect_graph });
              }
            } catch (err: any) {
              if (err?.status === 404) {
                markMissing([cardId]);
              } else {
                console.error('Failed to load effect graph:', err);
              }
            }
          }
        } finally {
          clearInFlight(chunk);
        }
      }
    };

    loadGraphs();
  }, [
    applyEffectGraphsToState,
    cardMap,
    clearInFlight,
    filterFetchableCardIds,
    gameState,
    markInFlight,
    markMissing,
  ]);

  return {
    effectGraphs,
    applyEffectGraphsToState,
    loadEffectGraphForObject,
  };
};
