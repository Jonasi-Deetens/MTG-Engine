import { useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';

interface UseCombatSelectionArgs {
  gameState: EngineGameStateSnapshot | null;
}

export const useCombatSelection = ({ gameState }: UseCombatSelectionArgs) => {
  const [selectedAttackers, setSelectedAttackers] = useState<Set<string>>(new Set());
  const [selectedBlockers, setSelectedBlockers] = useState<Record<string, Set<string>>>({});
  const [selectedBlockerOrder, setSelectedBlockerOrder] = useState<Record<string, string[]>>({});
  const [activeAttackerId, setActiveAttackerId] = useState<string | null>(null);
  const [selectedDefenderId, setSelectedDefenderId] = useState<string | null>(null);

  useEffect(() => {
    if (!gameState) return;
    setSelectedAttackers(new Set());
    setSelectedBlockers({});
    setSelectedBlockerOrder({});
    setActiveAttackerId(null);
    if (gameState.turn.step === 'declare_attackers') {
      const activeIndex = gameState.turn.active_player_index;
      const defenderIndex = (activeIndex + 1) % gameState.players.length;
      const defenderId = gameState.players[defenderIndex]?.id;
      setSelectedDefenderId(defenderId != null ? `player:${defenderId}` : null);
    }
    if (gameState.turn.step === 'declare_blockers') {
      setActiveAttackerId(gameState.turn.combat_state?.attackers[0] ?? null);
    }
  }, [gameState?.turn.step, gameState?.turn.turn_number]);

  const toggleAttacker = (objectId: string) => {
    setSelectedAttackers((prev) => {
      const next = new Set(prev);
      if (next.has(objectId)) {
        next.delete(objectId);
      } else {
        next.add(objectId);
      }
      return next;
    });
  };

  const toggleBlocker = (objectId: string) => {
    if (!activeAttackerId) return;
    setSelectedBlockers((prev) => {
      const next: Record<string, Set<string>> = { ...prev };
      // Ensure a blocker can only block one attacker.
      Object.keys(next).forEach((attackerId) => {
        if (attackerId !== activeAttackerId && next[attackerId]?.has(objectId)) {
          const updated = new Set(next[attackerId]);
          updated.delete(objectId);
          next[attackerId] = updated;
        }
      });
      const existing = next[activeAttackerId] ?? new Set<string>();
      const updated = new Set(existing);
      if (updated.has(objectId)) {
        updated.delete(objectId);
      } else {
        updated.add(objectId);
      }
      next[activeAttackerId] = updated;
      return next;
    });
    setSelectedBlockerOrder((prev) => {
      const next = { ...prev };
      // Remove from other attackers' order lists.
      Object.keys(next).forEach((attackerId) => {
        if (attackerId !== activeAttackerId && next[attackerId]?.includes(objectId)) {
          next[attackerId] = next[attackerId].filter((id) => id !== objectId);
        }
      });
      const currentOrder = next[activeAttackerId] ?? [];
      if (currentOrder.includes(objectId)) {
        next[activeAttackerId] = currentOrder.filter((id) => id !== objectId);
      } else {
        next[activeAttackerId] = [...currentOrder, objectId];
      }
      return next;
    });
  };

  const blockersPayload = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(selectedBlockers).map(([attackerId, blockerSet]) => {
          const order = selectedBlockerOrder[attackerId] ?? [];
          const ordered = order.filter((id) => blockerSet.has(id));
          const extras = Array.from(blockerSet).filter((id) => !ordered.includes(id));
          return [attackerId, [...ordered, ...extras]];
        })
      ),
    [selectedBlockers, selectedBlockerOrder]
  );

  const activeBlockerOrder = activeAttackerId ? blockersPayload[activeAttackerId] ?? [] : [];

  return {
    selectedAttackers,
    setSelectedAttackers,
    selectedBlockers,
    setSelectedBlockers,
    selectedBlockerOrder,
    setSelectedBlockerOrder,
    activeAttackerId,
    setActiveAttackerId,
    selectedDefenderId,
    setSelectedDefenderId,
    toggleAttacker,
    toggleBlocker,
    blockersPayload,
    activeBlockerOrder,
  };
};

