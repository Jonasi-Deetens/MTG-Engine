"use client";

import { useEffect, useMemo, useState } from 'react';
import { decks, DeckDetailResponse, DeckResponse } from '@/lib/decks';
import { engineApi, buildGameSnapshot, EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { PlayerZone } from '@/components/engine/PlayerZone';
import { StackView } from '@/components/engine/StackView';

const PLAYER_COUNT = 4;

export default function PlayPage() {
  const [deckList, setDeckList] = useState<DeckResponse[]>([]);
  const [selectedDeckIds, setSelectedDeckIds] = useState<Array<number | null>>(
    Array.from({ length: PLAYER_COUNT }, () => null)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);

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
  }, []);

  const canStart = useMemo(() => {
    if (selectedDeckIds.some((id) => id === null)) {
      return false;
    }
    return selectedDeckIds.every((id) => {
      const deck = deckList.find((entry) => entry.id === id);
      return deck?.format === 'Commander' && deck.commander_count > 0;
    });
  }, [selectedDeckIds, deckList]);

  const handleSelectDeck = (index: number, value: string) => {
    const next = [...selectedDeckIds];
    next[index] = value ? parseInt(value, 10) : null;
    setSelectedDeckIds(next);
  };

  const startGame = async () => {
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
      const response = await engineApi.execute({
        action: 'advance_turn',
        game_state: snapshot,
      });
      setGameState(response.game_state);
      if (typeof response.result?.current_priority === 'number') {
        setPriorityPlayer(response.result.current_priority);
      } else {
        setPriorityPlayer(response.game_state.turn.active_player_index);
      }
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to start game');
    } finally {
      setLoading(false);
    }
  };

  const runEngineAction = async (action: 'advance_turn' | 'pass_priority') => {
    if (!gameState) return;
    setLoading(true);
    setError(null);
    try {
      const response = await engineApi.execute({
        action,
        game_state: gameState,
        player_id: action === 'pass_priority' ? priorityPlayer ?? 0 : undefined,
      });
      setGameState(response.game_state);
      if (typeof response.result?.current_priority === 'number') {
        setPriorityPlayer(response.result.current_priority);
      }
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Engine action failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
          Playtest Commander
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Select four Commander decks and play using the engine rules.
        </p>
      </div>

      {error && (
        <Card variant="bordered" className="p-4 text-[color:var(--theme-status-error)]">
          {error}
        </Card>
      )}

      {!gameState && (
        <Card variant="bordered" className="p-4 space-y-4">
          <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
            Select decks for each player
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedDeckIds.map((deckId, index) => (
              <div key={`player-${index}`} className="space-y-2">
                <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">
                  Player {index + 1}
                </div>
                <select
                  value={deckId ?? ''}
                  onChange={(e) => handleSelectDeck(index, e.target.value)}
                  className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  <option value="">Select Commander deck...</option>
                  {deckList.map((deck) => (
                    <option key={deck.id} value={deck.id}>
                      {deck.name}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
          <div className="flex justify-end">
            <Button variant="primary" onClick={startGame} disabled={!canStart || loading}>
              {loading ? 'Starting...' : 'Start Game'}
            </Button>
          </div>
        </Card>
      )}

      {gameState && (
        <div className="space-y-6">
          <Card variant="bordered" className="p-4 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="text-sm text-[color:var(--theme-text-secondary)]">Turn</div>
              <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
                {gameState.turn.turn_number} · {gameState.turn.phase} / {gameState.turn.step}
              </div>
              <div className="text-xs text-[color:var(--theme-text-secondary)]">
                Active Player: {gameState.turn.active_player_index + 1}
                {priorityPlayer !== null && ` · Priority: ${priorityPlayer + 1}`}
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => runEngineAction('pass_priority')} disabled={loading}>
                Pass Priority
              </Button>
              <Button variant="primary" onClick={() => runEngineAction('advance_turn')} disabled={loading}>
                Advance Step
              </Button>
            </div>
          </Card>

          <StackView stack={gameState.stack} />

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {gameState.players.map((player, index) => (
              <PlayerZone
                key={`player-zone-${player.id}`}
                player={player}
                objects={gameState.objects}
                cardMap={cardMap}
                isActive={gameState.turn.active_player_index === index}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
