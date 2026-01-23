import { useCallback, useEffect, useRef, useState } from 'react';
import { abilities } from '@/lib/abilities';
import { EngineCardMap, EngineGameStateSnapshot } from '@/lib/engine';

interface UseAbilityGraphsArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
}

export const useAbilityGraphs = ({ gameState, cardMap, setGameState }: UseAbilityGraphsArgs) => {
  const [abilityGraphs, setAbilityGraphs] = useState<Record<string, any>>({});
  const missingCardIdsRef = useRef(new Set<string>());
  const inFlightCardIdsRef = useRef(new Set<string>());

  const filterFetchableCardIds = useCallback(
    (cardIds: string[]) =>
      cardIds.filter(
        (cardId) =>
          !abilityGraphs[cardId] &&
          !missingCardIdsRef.current.has(cardId) &&
          !inFlightCardIdsRef.current.has(cardId)
      ),
    [abilityGraphs]
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

  const applyAbilityGraphsToState = useCallback(
    (graphsByCardId: Record<string, any>) => {
      if (Object.keys(graphsByCardId).length === 0) return;
      setAbilityGraphs((prev) => ({ ...prev, ...graphsByCardId }));
      setGameState((prevState) => {
        if (!prevState) return prevState;
        const updatedObjects = prevState.objects.map((obj) => {
          const objCardId = cardMap[obj.id]?.card_id;
          const graph = objCardId ? graphsByCardId[objCardId] : undefined;
          if (!graph) return obj;
          if (obj.ability_graphs && obj.ability_graphs.length > 0) return obj;
          return {
            ...obj,
            ability_graphs: [graph],
          };
        });
        return { ...prevState, objects: updatedObjects };
      });
    },
    [cardMap, setGameState]
  );

  const loadAbilityGraphForObject = useCallback(
    async (objectId: string) => {
      const card = cardMap[objectId];
      const cardId = card?.card_id;
      if (!cardId || abilityGraphs[cardId]) return;
      if (missingCardIdsRef.current.has(cardId) || inFlightCardIdsRef.current.has(cardId)) return;
      markInFlight([cardId]);
      try {
        const response = await abilities.getCardGraph(cardId);
        if (response?.ability_graph) {
          applyAbilityGraphsToState({ [cardId]: response.ability_graph });
        }
      } catch (err: any) {
        if (err?.status === 404) {
          markMissing([cardId]);
        } else {
          console.error('Failed to load ability graph:', err);
        }
      } finally {
        clearInFlight([cardId]);
      }
    },
    [
      abilityGraphs,
      applyAbilityGraphsToState,
      cardMap,
      clearInFlight,
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
      const chunkSize = 25;
      for (let i = 0; i < cardIdsToFetch.length; i += chunkSize) {
        const chunk = cardIdsToFetch.slice(i, i + chunkSize);
        if (chunk.length === 0) continue;
        markInFlight(chunk);
        try {
          const response = await abilities.getCardGraphs(chunk);
          const graphsByCardId = response.graphs.reduce<Record<string, any>>((acc, graph) => {
            acc[graph.card_id] = graph.ability_graph;
            return acc;
          }, {});
          applyAbilityGraphsToState(graphsByCardId);
          if (response.missing?.length) {
            markMissing(response.missing);
          }
        } catch (err: any) {
          if (err?.status !== 404) {
            console.error('Failed to bulk load ability graphs:', err);
          }
        } finally {
          clearInFlight(chunk);
        }
      }
    };

    loadGraphs();
  }, [
    abilityGraphs,
    applyAbilityGraphsToState,
    cardMap,
    clearInFlight,
    filterFetchableCardIds,
    gameState,
    markInFlight,
    markMissing,
  ]);

  return {
    abilityGraphs,
    applyAbilityGraphsToState,
    loadAbilityGraphForObject,
  };
};

