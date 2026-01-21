import { useCallback, useEffect, useMemo, useState } from 'react';
import { decks, DeckDetailResponse, DeckResponse } from '@/lib/decks';
import { buildGameSnapshot, engineApi, EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';

const PLAYER_COUNT = 4;

interface UseGameSetupArgs {
  setGameState: React.Dispatch<React.SetStateAction<EngineGameStateSnapshot | null>>;
  setCardMap: React.Dispatch<React.SetStateAction<EngineCardMap>>;
  setPriorityPlayer: React.Dispatch<React.SetStateAction<number | null>>;
  setGameId: React.Dispatch<React.SetStateAction<string | null>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
}

export const useGameSetup = ({
  setGameState,
  setCardMap,
  setPriorityPlayer,
  setGameId,
  setError,
}: UseGameSetupArgs) => {
  const [deckList, setDeckList] = useState<DeckResponse[]>([]);
  const [selectedDeckIds, setSelectedDeckIds] = useState<Array<number | null>>(
    Array.from({ length: PLAYER_COUNT }, () => null)
  );
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadDecks = async () => {
      try {
        const response = await decks.getDecks('Commander');
        setDeckList(response);
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load decks');
      }
    };
    loadDecks();
  }, [setError]);

  const canStart = useMemo(() => {
    if (selectedDeckIds.some((id) => id === null)) {
      return false;
    }
    return selectedDeckIds.every((id) => {
      const deck = deckList.find((entry) => entry.id === id);
      return deck?.format === 'Commander' && deck.commander_count > 0;
    });
  }, [selectedDeckIds, deckList]);

  const handleSelectDeck = useCallback((index: number, value: string) => {
    const next = [...selectedDeckIds];
    next[index] = value ? parseInt(value, 10) : null;
    setSelectedDeckIds(next);
  }, [selectedDeckIds]);

  const startGame = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const deckDetails: DeckDetailResponse[] = [];
      for (const deckId of selectedDeckIds) {
        if (deckId === null) {
          throw new Error('Please select a deck for each player.');
        }
        const detail = await decks.getDeck(deckId);
        if (detail.format !== 'Commander' || detail.commander_count < 1) {
          throw new Error(`Deck "${detail.name}" is not a valid Commander deck.`);
        }
        deckDetails.push(detail);
      }

      const { snapshot, cardMap: newCardMap } = buildGameSnapshot(deckDetails);
      setCardMap(newCardMap);
      const session = await engineApi.createSession(snapshot);
      setGameId(session.game_id);
      localStorage.setItem('play.game_id', session.game_id);
      localStorage.setItem('play.card_map', JSON.stringify(newCardMap));
      const response = await engineApi.execute({
        action: 'advance_turn',
        game_id: session.game_id,
      });
      setGameState(response.game_state);
      if (typeof response.result?.current_priority === 'number') {
        setPriorityPlayer(response.result.current_priority);
      } else if (typeof response.game_state.turn.priority_current_index === 'number') {
        setPriorityPlayer(response.game_state.turn.priority_current_index);
      } else {
        setPriorityPlayer(response.game_state.turn.active_player_index);
      }
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to start game');
    } finally {
      setLoading(false);
    }
  }, [selectedDeckIds, setCardMap, setError, setGameId, setGameState, setPriorityPlayer]);

  return {
    deckList,
    selectedDeckIds,
    loading,
    canStart,
    handleSelectDeck,
    startGame,
  };
};

