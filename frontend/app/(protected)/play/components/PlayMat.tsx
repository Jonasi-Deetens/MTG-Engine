'use client';

import { useEffect, useMemo, useState } from 'react';
import { PlayerMat } from '@/features/game/components/playmat/PlayerMat';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';
import {
  usePlayGame,
  usePlayCombat,
  usePlaySelection,
  usePlayTurn,
} from '@/app/(protected)/play/PlayProviders';

type ViewMode = 'single' | 'all';

export function PlayMat() {
  // Use focused hooks for specific state slices
  const { gameState, cardMap } = usePlayGame();
  const {
    currentPriority,
    activePlayerIndex,
    isDeclareAttackers,
    isDeclareBlockers,
  } = usePlayTurn();
  const {
    selectedAttackers,
    selectedBlockers,
    activeAttackerId,
    toggleAttacker,
    toggleBlocker,
    defendingPlayerId,
  } = usePlayCombat();
  const {
    selectedHandId,
    selectedCommandId,
    selectedBattlefieldId,
    setSelectedHandId,
    setSelectedCommandId,
    setSelectedBattlefieldId,
    loadEffectGraphForObject,
  } = usePlaySelection();

  const [viewMode, setViewMode] = useState<ViewMode>('single');
  const [selectedPlayerId, setSelectedPlayerId] = useState<number>(currentPriority ?? 0);

  useEffect(() => {
    if (!gameState) return;
    if (gameState.players.some((player) => player.id === selectedPlayerId)) return;
    setSelectedPlayerId(gameState.players[0]?.id ?? 0);
  }, [gameState, selectedPlayerId]);

  const playerOptions = useMemo(
    () =>
      (gameState?.players ?? []).map((player) => ({
        value: String(player.id),
        label: `Player ${player.id + 1}`,
      })),
    [gameState?.players]
  );

  if (!gameState) return null;

  const playersToRender =
    viewMode === 'all'
      ? gameState.players
      : gameState.players.filter((player) => player.id === selectedPlayerId);

  return (
    <div className="space-y-4">
      <div className="play-mat-toolbar">
        <div className="flex items-center gap-2">
          <Button
            type="button"
            size="sm"
            variant={viewMode === 'single' ? 'secondary' : 'outline'}
            onClick={() => setViewMode('single')}
          >
            Single View
          </Button>
          <Button
            type="button"
            size="sm"
            variant={viewMode === 'all' ? 'secondary' : 'outline'}
            onClick={() => setViewMode('all')}
          >
            All Players
          </Button>
        </div>
        {viewMode === 'single' && (
          <div className="text-sm text-[color:var(--theme-text-secondary)] flex items-center gap-2">
            <span>Focus</span>
            <Select
              className="min-w-[160px]"
              options={playerOptions}
              value={String(selectedPlayerId)}
              onChange={(value) => setSelectedPlayerId(Number(value))}
            />
          </div>
        )}
      </div>

      <div className="space-y-6">
        {playersToRender.map((player) => {
          const isActive = gameState.turn.active_player_index === player.id;
          const isAttackerView = isDeclareAttackers && player.id === activePlayerIndex;
          const isDefenderView = isDeclareBlockers && player.id === defendingPlayerId;
          return (
            <PlayerMat
              key={`player-mat-${player.id}`}
              player={player}
              objects={gameState.objects}
              cardMap={cardMap}
              isActive={isActive}
              selectedHandId={player.id === currentPriority ? selectedHandId : null}
              selectedCommandId={player.id === currentPriority ? selectedCommandId : null}
              onSelectHand={
                player.id === currentPriority
                  ? (objectId) => {
                      const obj = gameState.objects.find((entry) => entry.id === objectId);
                      if (!obj || obj.zone !== 'hand') return;
                      setSelectedHandId(objectId);
                      setSelectedCommandId(null);
                      setSelectedBattlefieldId(null);
                      loadEffectGraphForObject(objectId);
                    }
                  : undefined
              }
              onSelectCommand={
                player.id === currentPriority
                  ? (objectId) => {
                      setSelectedCommandId(objectId);
                      setSelectedHandId(null);
                      setSelectedBattlefieldId(null);
                      loadEffectGraphForObject(objectId);
                    }
                  : undefined
              }
              selectedBattlefieldIds={
                isAttackerView
                  ? selectedAttackers
                  : isDefenderView
                    ? selectedBlockers[activeAttackerId ?? ''] ?? new Set()
                    : undefined
              }
              onToggleBattlefield={
                isAttackerView
                  ? toggleAttacker
                  : isDefenderView
                    ? toggleBlocker
                    : undefined
              }
              selectedBattlefieldId={
                !isDeclareAttackers && !isDeclareBlockers && player.id === currentPriority
                  ? selectedBattlefieldId
                  : null
              }
              onSelectBattlefield={
                !isDeclareAttackers && !isDeclareBlockers && player.id === currentPriority
                  ? (objectId) => {
                      setSelectedBattlefieldId(objectId);
                      setSelectedHandId(null);
                      setSelectedCommandId(null);
                      loadEffectGraphForObject(objectId);
                    }
                  : undefined
              }
            />
          );
        })}
      </div>
    </div>
  );
}
