'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, EngineCombatStateSnapshot } from '@/lib/engine';
import {
  buildDefaultCombatAssignments,
  hasFirstStrikeCombat as computeHasFirstStrikeCombat,
  isEligibleForCombatPass,
} from '@/lib/combatDamage';

/**
 * CombatContext - Combat phase state management
 * 
 * Responsible for:
 * - Attacker/blocker selection
 * - Blocker ordering
 * - Combat damage assignments
 * - Defender selection (player or planeswalker)
 * - Combat validation errors
 */

export interface CombatContextValue {
  // Selection state
  selectedAttackers: Set<string>;
  selectedBlockers: Record<string, Set<string>>;
  selectedBlockerOrder: Record<string, string[]>;
  activeAttackerId: string | null;
  selectedDefenderId: string | null;
  combatDamageAssignments: Record<string, Record<string, number>>;
  
  // Derived state
  combatState: EngineCombatStateSnapshot | null | undefined;
  defenderOptions: Array<{ value: string; label: string }>;
  defendingPlayerId: number | null;
  defendingObjectId: string | null;
  hasFirstStrikeCombat: boolean;
  combatDamagePass: 'first_strike' | 'regular' | null;
  hasManualCombatChoices: boolean;
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
  activeBlockerOrder: string[];
  blockersPayload: Record<string, string[]>;
  
  // Actions
  setActiveAttackerId: (id: string | null) => void;
  setSelectedDefenderId: (id: string | null) => void;
  toggleAttacker: (id: string) => void;
  toggleBlocker: (id: string) => void;
  setSelectedBlockerOrder: (order: Record<string, string[]>) => void;
  setCombatDamageAssignments: (assignments: Record<string, Record<string, number>>) => void;
}

interface CombatProviderProps {
  children: React.ReactNode;
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
}

const CombatContext = createContext<CombatContextValue | null>(null);

export function CombatProvider({ children, gameState, cardMap, priorityPlayer }: CombatProviderProps) {
  const value = useCombatInternal({ gameState, cardMap, priorityPlayer });
  return <CombatContext.Provider value={value}>{children}</CombatContext.Provider>;
}

export function useCombat() {
  const context = useContext(CombatContext);
  if (!context) {
    throw new Error('useCombat must be used within CombatProvider');
  }
  return context;
}

interface UseCombatInternalArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
}

function useCombatInternal({ gameState, cardMap, priorityPlayer }: UseCombatInternalArgs): CombatContextValue {
  const [selectedAttackers, setSelectedAttackers] = useState<Set<string>>(new Set());
  const [selectedBlockers, setSelectedBlockers] = useState<Record<string, Set<string>>>({});
  const [selectedBlockerOrder, setSelectedBlockerOrder] = useState<Record<string, string[]>>({});
  const [activeAttackerId, setActiveAttackerId] = useState<string | null>(null);
  const [selectedDefenderId, setSelectedDefenderId] = useState<string | null>(null);
  const [combatDamageAssignments, setCombatDamageAssignments] = useState<Record<string, Record<string, number>>>({});

  const objectMap = useMemo(
    () => new Map(gameState?.objects.map((obj) => [obj.id, obj]) ?? []),
    [gameState?.objects]
  );

  const activePlayerIndex = gameState?.turn?.active_player_index ?? 0;
  const combatState = gameState?.turn?.combat_state;

  // Reset combat selection on turn/step change
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

  // Combat damage pass tracking
  const hasFirstStrikeCombat = useMemo(() => computeHasFirstStrikeCombat(gameState), [gameState]);
  
  const combatDamagePass = useMemo(() => {
    if (!hasFirstStrikeCombat) return null;
    const resolved = gameState?.turn?.combat_state?.first_strike_resolved;
    return resolved ? 'regular' : 'first_strike';
  }, [gameState, hasFirstStrikeCombat]);

  // Check if manual damage assignment is needed
  const hasManualCombatChoices = useMemo(() => {
    if (!gameState?.turn?.combat_state) return false;
    const localObjectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    return gameState.turn.combat_state.attackers.some((attackerId) => {
      const attacker = localObjectMap.get(attackerId);
      if (!isEligibleForCombatPass(attacker?.keywords, combatDamagePass ?? undefined)) return false;
      const blockers = gameState.turn.combat_state?.blockers?.[attackerId] ?? [];
      if (blockers.length > 1) return true;
      if (blockers.length > 0 && attacker?.keywords?.includes('Trample')) return true;
      return false;
    });
  }, [combatDamagePass, gameState]);

  // Initialize combat damage assignments
  useEffect(() => {
    if (!gameState) return;
    if (gameState.turn.step === 'combat_damage') {
      setCombatDamageAssignments(buildDefaultCombatAssignments(gameState, combatDamagePass ?? undefined));
      return;
    }
    if (Object.keys(combatDamageAssignments).length > 0) {
      setCombatDamageAssignments({});
    }
  }, [combatDamagePass, gameState?.turn.step, gameState?.turn.turn_number]);

  // Toggle attacker selection
  const toggleAttacker = useCallback((objectId: string) => {
    setSelectedAttackers((prev) => {
      const next = new Set(prev);
      if (next.has(objectId)) {
        next.delete(objectId);
      } else {
        next.add(objectId);
      }
      return next;
    });
  }, []);

  // Toggle blocker selection
  const toggleBlocker = useCallback((objectId: string) => {
    if (!activeAttackerId) return;
    setSelectedBlockers((prev) => {
      const next: Record<string, Set<string>> = { ...prev };
      // Ensure a blocker can only block one attacker
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
      // Remove from other attackers' order lists
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
  }, [activeAttackerId]);

  // Build blockers payload for engine
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

  // Derive defender options
  const defenderOptions = useMemo(() => {
    if (!gameState) return [];
    const activePlayerId = gameState.players[activePlayerIndex]?.id;
    const options: Array<{ value: string; label: string }> = [];
    gameState.players.forEach((player) => {
      if (player.id === activePlayerId) return;
      options.push({ value: `player:${player.id}`, label: `Player ${player.id + 1}` });
    });
    gameState.objects.forEach((obj) => {
      if (obj.zone !== 'battlefield') return;
      if (!obj.types?.includes('Planeswalker')) return;
      if (obj.controller_id === activePlayerId) return;
      const label = cardMap[obj.id]?.name || obj.name || obj.id;
      options.push({ value: `planeswalker:${obj.id}`, label: `${label} (Planeswalker)` });
    });
    return options;
  }, [activePlayerIndex, cardMap, gameState]);

  // Derive defending player/object IDs
  const defendingObjectId = combatState?.defending_object_id ?? (
    selectedDefenderId?.startsWith('planeswalker:') ? selectedDefenderId.split(':')[1] : null
  );

  const selectedDefendingPlayerId = useMemo(() => {
    if (!selectedDefenderId) return null;
    if (selectedDefenderId.startsWith('player:')) {
      const raw = selectedDefenderId.split(':')[1];
      return raw ? Number(raw) : null;
    }
    if (selectedDefenderId.startsWith('planeswalker:')) {
      const objId = selectedDefenderId.split(':')[1];
      const obj = objId ? objectMap.get(objId) : undefined;
      return obj ? obj.controller_id : null;
    }
    return null;
  }, [objectMap, selectedDefenderId]);

  const defendingPlayerId = combatState?.defending_player_id ?? selectedDefendingPlayerId;

  // Validate blocker selections
  const isDeclareBlockers = gameState?.turn?.step === 'declare_blockers';
  
  const blockerErrors = useMemo(() => {
    if (!gameState || !combatState || !isDeclareBlockers) return [];
    const localObjectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const errors: string[] = [];
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;
    
    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = localObjectMap.get(attackerId);
      if (!attacker) return;
      if (attacker.keywords?.includes('Menace') && blockerSet.size === 1) {
        const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
        errors.push(`${attackerLabel} has menace and needs 2+ blockers.`);
      }
      blockerSet.forEach((blockerId) => {
        const blocker = localObjectMap.get(blockerId);
        if (!blocker) return;
        const blockerLabel = cardMap[blockerId]?.name || blocker.name || blockerId;
        if (usedBlockers.has(blockerId)) {
          errors.push(`${blockerLabel} can't block multiple attackers.`);
        }
        usedBlockers.add(blockerId);
        if (blocker.zone !== 'battlefield' || blocker.phased_out) {
          errors.push(`${blockerLabel} can't block (not on battlefield).`);
          return;
        }
        if (blocker.controller_id !== defendingId) {
          errors.push(`${blockerLabel} isn't controlled by the defender.`);
        }
        if (!blocker.types.includes('Creature')) {
          errors.push(`${blockerLabel} isn't a creature.`);
        }
        if (blocker.tapped) {
          errors.push(`${blockerLabel} is tapped.`);
        }
        if (attacker.keywords?.includes('Flying')) {
          const canBlockFly = blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
          if (!canBlockFly) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            errors.push(`${blockerLabel} can't block ${attackerLabel} (flying).`);
          }
        }
        if (attacker.protections?.length && blocker.colors?.length) {
          if (blocker.colors.some((color) => attacker.protections?.includes(color))) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            errors.push(`${attackerLabel} has protection from ${blockerLabel}.`);
          }
        }
      });
    });
    return Array.from(new Set(errors));
  }, [cardMap, combatState, gameState, isDeclareBlockers, selectedBlockers]);

  const blockerErrorMap = useMemo(() => {
    if (!gameState || !combatState || !isDeclareBlockers) return {};
    const localObjectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const map: Record<string, string[]> = {};
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;
    
    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = localObjectMap.get(attackerId);
      if (!attacker) return;
      blockerSet.forEach((blockerId) => {
        const blocker = localObjectMap.get(blockerId);
        if (!blocker) return;
        const blockerLabel = cardMap[blockerId]?.name || blocker.name || blockerId;
        const add = (message: string) => {
          if (!map[blockerId]) map[blockerId] = [];
          if (!map[blockerId].includes(message)) map[blockerId].push(message);
        };
        if (usedBlockers.has(blockerId)) {
          add(`${blockerLabel} can't block multiple attackers.`);
        }
        usedBlockers.add(blockerId);
        if (blocker.zone !== 'battlefield' || blocker.phased_out) {
          add(`${blockerLabel} can't block (not on battlefield).`);
          return;
        }
        if (blocker.controller_id !== defendingId) {
          add(`${blockerLabel} isn't controlled by the defender.`);
        }
        if (!blocker.types.includes('Creature')) {
          add(`${blockerLabel} isn't a creature.`);
        }
        if (blocker.tapped) {
          add(`${blockerLabel} is tapped.`);
        }
        if (attacker.keywords?.includes('Flying')) {
          const canBlockFly = blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
          if (!canBlockFly) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            add(`${blockerLabel} can't block ${attackerLabel} (flying).`);
          }
        }
        if (attacker.protections?.length && blocker.colors?.length) {
          if (blocker.colors.some((color) => attacker.protections?.includes(color))) {
            const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
            add(`${attackerLabel} has protection from ${blockerLabel}.`);
          }
        }
      });
    });
    return map;
  }, [cardMap, combatState, gameState, isDeclareBlockers, selectedBlockers]);

  return {
    selectedAttackers,
    selectedBlockers,
    selectedBlockerOrder,
    activeAttackerId,
    selectedDefenderId,
    combatDamageAssignments,
    combatState,
    defenderOptions,
    defendingPlayerId,
    defendingObjectId,
    hasFirstStrikeCombat,
    combatDamagePass,
    hasManualCombatChoices,
    blockerErrors,
    blockerErrorMap,
    activeBlockerOrder,
    blockersPayload,
    setActiveAttackerId,
    setSelectedDefenderId,
    toggleAttacker,
    toggleBlocker,
    setSelectedBlockerOrder,
    setCombatDamageAssignments,
  };
}
