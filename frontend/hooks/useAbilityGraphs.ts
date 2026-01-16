import { useCallback, useEffect, useState } from 'react';
import { abilities } from '@/lib/abilities';
import { EngineCardMap, EngineGameStateSnapshot } from '@/lib/engine';

interface UseAbilityGraphsArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
}

export const useAbilityGraphs = ({ gameState, cardMap, setGameState }: UseAbilityGraphsArgs) => {
  const [abilityGraphs, setAbilityGraphs] = useState<Record<string, any>>({});

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
      try {
        const response = await abilities.getCardGraph(cardId);
        if (response?.ability_graph) {
          applyAbilityGraphsToState({ [cardId]: response.ability_graph });
        }
      } catch (err: any) {
        if (err?.status !== 404) {
          console.error('Failed to load ability graph:', err);
        }
      }
    },
    [abilityGraphs, applyAbilityGraphsToState, cardMap]
  );

  useEffect(() => {
    if (!gameState) return;
    const cardIdsToFetch = Array.from(
      new Set(
        gameState.objects
          .filter((obj) => obj.zone === 'battlefield' || obj.zone === 'command')
          .map((obj) => cardMap[obj.id]?.card_id)
          .filter((cardId): cardId is string => Boolean(cardId))
      )
    ).filter((cardId) => !abilityGraphs[cardId]);

    if (cardIdsToFetch.length === 0) return;

    const loadGraphs = async () => {
      try {
        const response = await abilities.getCardGraphs(cardIdsToFetch);
        const graphsByCardId = response.graphs.reduce<Record<string, any>>((acc, graph) => {
          acc[graph.card_id] = graph.ability_graph;
          return acc;
        }, {});
        applyAbilityGraphsToState(graphsByCardId);
      } catch (err: any) {
        if (err?.status !== 404) {
          console.error('Failed to bulk load ability graphs:', err);
        }
      }
    };

    loadGraphs();
  }, [abilityGraphs, applyAbilityGraphsToState, cardMap, gameState]);

  return {
    abilityGraphs,
    applyAbilityGraphsToState,
    loadAbilityGraphForObject,
  };
};

