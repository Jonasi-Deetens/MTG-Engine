'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type Dispatch, type SetStateAction } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, engineApi } from '@/lib/engine';
import { useAbilityGraphs } from '@/features/game/hooks/useAbilityGraphs';
import { useTargeting } from '@/features/game/hooks/useTargeting';
import { useEffectTargeting } from '@/features/game/hooks/useEffectTargeting';
import { useCopyEffectTargeting } from '@/features/game/hooks/useCopyEffectTargeting';
import { useSearchChoices } from '@/features/game/hooks/useSearchChoices';
import { useCasting } from '@/features/game/hooks/useCasting';
import { useCombatSelection } from '@/features/game/hooks/useCombatSelection';
import { useEngineActions } from '@/features/game/hooks/useEngineActions';
import { useGameSetup } from '@/features/game/hooks/useGameSetup';
import { useTurnReset } from '@/features/game/hooks/useTurnReset';
import { useReplacementConflicts } from '@/features/game/hooks/useReplacementConflicts';
import { useCastContext } from '@/features/game/hooks/useCastContext';
import { useTurnState } from '@/features/game/hooks/useTurnState';
import { useWardPayments } from '@/features/game/hooks/useWardPayments';
import { useActivationCosts } from '@/features/game/hooks/useActivationCosts';
import { useResolveCleanup } from '@/features/game/hooks/useResolveCleanup';
import {
  deriveAdditionalCostsFromGraph,
  deriveAlternativeCastCostsFromGraph,
  deriveAlternativeExtraCostsFromGraph,
  deriveOptionalCastCostsFromGraph,
  deriveSpliceCardsFromHand,
} from '@/lib/graphCosts';
import {
  buildDefaultCombatAssignments,
  hasFirstStrikeCombat as computeHasFirstStrikeCombat,
  isEligibleForCombatPass,
} from '@/lib/combatDamage';
import {
  buildEnterChoiceConfig,
  buildEnterChoiceDefaults,
  buildEnterChoiceErrors,
  buildEnterChoiceTargetOptions,
} from '@/lib/enterChoices';
import { buildModalChoiceErrors, deriveModalConfig } from '@/lib/modalChoices';
import type { GameContextValue } from '@/features/game/contexts/GameContext';
import type { ManaPaymentDetail } from '@/lib/manaPayment';

/**
 * PlayProviders - Unified context provider with focused APIs for game state
 * 
 * This file contains all the state management for the play page and exposes
 * focused context hooks for different concerns:
 * - usePlayGame() for game state
 * - usePlayCombat() for combat state  
 * - usePlayChoices() for modal/enter/replacement choices
 * - usePlaySelection() for hand/battlefield selection
 * - usePlayTurn() for turn/phase state
 * - usePlayTargeting() for target selection
 * - usePlayCasting() for spell casting
 * - usePlaySetup() for deck setup
 */

// ============================================================================
// Context Interfaces
// ============================================================================

export interface SetupContextValue {
  deckList: any[];
  selectedDeckIds: (number | null)[];
  setupLoading: boolean;
  canStart: boolean;
  handleSelectDeck: (index: number, deckId: string) => void;
  startGame: () => void;
}

export interface SelectionContextValue {
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  selectedStackIndex: number | null;
  setSelectedHandId: Dispatch<SetStateAction<string | null>>;
  setSelectedCommandId: Dispatch<SetStateAction<string | null>>;
  setSelectedBattlefieldId: Dispatch<SetStateAction<string | null>>;
  setSelectedStackIndex: Dispatch<SetStateAction<number | null>>;
  loadAbilityGraphForObject: (objectId: string) => void;
  abilityGraphs: Record<string, any>;
  selectedGraph: any;
}

export interface TurnContextValue {
  currentPriority: number | null;
  activePlayerIndex: number;
  isMainPhase: boolean;
  isDeclareAttackers: boolean;
  isDeclareBlockers: boolean;
  isCombatDamage: boolean;
  isPriorityActivePlayer: boolean;
  isPriorityDefender: boolean;
  objectMap: Map<string, any>;
}

export interface CastingContextValue {
  preparedCast: { objectId: string; cost: any } | null;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  manaPaymentStatus: { errors: string[] };
  costLabel: string;
  autoPayMana: boolean;
  isComplexCost: boolean;
  handlePrepareCast: () => void;
  handleFinalizeCast: () => void;
  setManaPayment: Dispatch<SetStateAction<Record<string, number>>>;
  setManaPaymentDetail: Dispatch<SetStateAction<ManaPaymentDetail>>;
  setAutoPayMana: Dispatch<SetStateAction<boolean>>;
  buildCastContext: (objectId?: string, options?: any) => any;
  // Activation costs
  activationCosts: any[];
  activationPayments: any[];
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  hasActivationCostErrors: boolean;
  activationCostPaymentsPayload: any;
  setActivationPayments: Dispatch<SetStateAction<any[]>>;
  setActivationPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Additional costs
  additionalCastCosts: any[];
  additionalCastPayments: any[];
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  hasAdditionalCastCostErrors: boolean;
  setAdditionalCastPayments: Dispatch<SetStateAction<any[]>>;
  setAdditionalCastPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Alternative costs
  alternativeCostOptions: any[];
  selectedAlternativeCostTag: string | null;
  alternativeExtraCostEntries: any[];
  alternativeExtraPayments: any[];
  alternativeExtraPaymentDetails: Record<number, ManaPaymentDetail>;
  alternativeExtraCostErrors: string[];
  hasAlternativeExtraCostErrors: boolean;
  setSelectedAlternativeCostTag: Dispatch<SetStateAction<string | null>>;
  setAlternativeExtraPayments: Dispatch<SetStateAction<any[]>>;
  setAlternativeExtraPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Optional costs
  optionalCostOptions: any[];
  optionalCostSelections: Record<string, number>;
  optionalCostEntries: any[];
  optionalCostPayments: any[];
  optionalCostPaymentDetails: Record<number, ManaPaymentDetail>;
  optionalCostErrors: string[];
  optionalCostPaymentErrors: string[];
  hasOptionalCostErrors: boolean;
  handleToggleOptionalCost: (tag: string) => void;
  handleUpdateOptionalCostCount: (tag: string, count: number) => void;
  setOptionalCostPayments: Dispatch<SetStateAction<any[]>>;
  setOptionalCostPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Conspire
  conspireSelected: boolean;
  conspireOptions: any[];
  conspireTaps: string[];
  conspireError: string | null;
  handleToggleConspireTap: (value: string) => void;
  // Splice
  spliceOptions: any[];
  spliceSelections: string[];
  spliceCosts: any[];
  splicePayments: any[];
  splicePaymentDetails: Record<number, ManaPaymentDetail>;
  spliceCostErrors: string[];
  handleToggleSpliceCard: (cardId: string) => void;
  setSplicePayments: Dispatch<SetStateAction<any[]>>;
  setSplicePaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
}

export interface PlayCombatContextValue {
  selectedAttackers: Set<string>;
  selectedBlockers: Record<string, Set<string>>;
  selectedBlockerOrder: Record<string, string[]>;
  activeAttackerId: string | null;
  selectedDefenderId: string | null;
  combatDamageAssignments: Record<string, Record<string, number>>;
  combatState: any;
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
  setActiveAttackerId: Dispatch<SetStateAction<string | null>>;
  setSelectedDefenderId: Dispatch<SetStateAction<string | null>>;
  toggleAttacker: (id: string) => void;
  toggleBlocker: (id: string) => void;
  setSelectedBlockerOrder: Dispatch<SetStateAction<Record<string, string[]>>>;
  setCombatDamageAssignments: Dispatch<SetStateAction<Record<string, Record<string, number>>>>;
}

export interface PlayChoicesContextValue {
  modalChoiceConfig: any;
  selectedModalModes: string[];
  modalChoiceErrors: string[];
  modalChoicesForCast: string[];
  entwineSelected: boolean;
  handleToggleModalMode: (modeId: string) => void;
  setSelectedModalModes: Dispatch<SetStateAction<string[]>>;
  enterChoiceConfig: any[];
  enterChoices: Record<string, string>;
  enterChoiceErrors: string[];
  enterChoiceTargetOptions: Array<{ value: string; label: string }>;
  setEnterChoices: Dispatch<SetStateAction<Record<string, string>>>;
  onEnterChoiceChange: (type: string, value: string) => void;
  replacementChoices: Record<string, string>;
  replacementConflicts: any[];
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: any[];
  highlightedReplacementKey: string | null;
  setReplacementChoices: Dispatch<SetStateAction<Record<string, string>>>;
  setHighlightedReplacementKey: Dispatch<SetStateAction<string | null>>;
  wardTargets: any[];
  wardPayments: Record<string, any>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  wardPaymentsPayload: Record<string, any>;
  hasWardPaymentErrors: boolean;
  autoPayWard: boolean;
  setWardPayments: Dispatch<SetStateAction<Record<string, any>>>;
  setWardPaymentDetails: Dispatch<SetStateAction<Record<string, ManaPaymentDetail>>>;
  setAutoPayWard: Dispatch<SetStateAction<boolean>>;
}

export interface PlayTargetingContextValue {
  targetHints: any;
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  objectTargetStatus: Record<string, boolean | null>;
  playerTargetStatus: Record<number, boolean | null>;
  stackTargetChecks: any[];
  stackSpellObjects: any[];
  filteredTargetableObjects: any[];
  filteredTargetPlayers: any[];
  shouldUseStackTargets: boolean;
  requiredTargetsGlobal: string[];
  distinctTargetsGlobal: string[];
  minTargetsGlobal: Record<string, number> | null;
  effectTargetGroups: any[];
  targetsByEffect: Record<string, Record<string, any>>;
  requiredTargetsByEffect: Record<string, string[]>;
  distinctTargetsByEffect: Record<string, string[]>;
  minTargetsByEffect: Record<string, Record<string, number>>;
  globalTargetErrors: string[];
  effectTargetObjectIds: string[];
  effectTargetPlayerIds: number[];
  hasEffectTargets: boolean;
  mergedTargetsByEffect: Record<string, Record<string, any>>;
  searchEntries: any[];
  searchTargetsByEffect: Record<string, Record<string, any>>;
  searchErrors: string[];
  copySpellConfig: { enabled: boolean; amount: number };
  copyTargetSelections: Array<{ objectIds: string[]; playerIds: number[] }>;
  copyTargetErrorsGlobal: string[];
  copyTargetsByEffectCount: number;
  copyEffectTargetGroups: any[];
  copyTargetsByEffectList: any[];
  copyRequiredTargetsByEffectList: any[];
  copyDistinctTargetsByEffectList: any[];
  copyMinTargetsByEffectList: any[];
  copyTargetErrors: string[];
  resolvedTargetObjectIds: string[];
  resolvedTargetPlayerIds: number[];
  targetSelectionErrors: string[];
  setSelectedTargetObjectIds: Dispatch<SetStateAction<string[]>>;
  setSelectedTargetPlayerIds: Dispatch<SetStateAction<number[]>>;
  setCopyTargetSelections: Dispatch<SetStateAction<Array<{ objectIds: string[]; playerIds: number[] }>>>;
  clearEffectTargets: () => void;
}

// ============================================================================
// Contexts
// ============================================================================

const PlayGameContext = createContext<GameContextValue | null>(null);
const PlayCombatContext = createContext<PlayCombatContextValue | null>(null);
const PlayChoicesContext = createContext<PlayChoicesContextValue | null>(null);
const PlaySelectionContext = createContext<SelectionContextValue | null>(null);
const PlayTurnContext = createContext<TurnContextValue | null>(null);
const PlayTargetingContext = createContext<PlayTargetingContextValue | null>(null);
const PlayCastingContext = createContext<CastingContextValue | null>(null);
const PlaySetupContext = createContext<SetupContextValue | null>(null);

// ============================================================================
// Context Hooks
// ============================================================================

export function usePlayGame(): GameContextValue {
  const context = useContext(PlayGameContext);
  if (!context) {
    throw new Error('usePlayGame must be used within PlayProviders');
  }
  return context;
}

export function usePlayCombat(): PlayCombatContextValue {
  const context = useContext(PlayCombatContext);
  if (!context) {
    throw new Error('usePlayCombat must be used within PlayProviders');
  }
  return context;
}

export function usePlayChoices(): PlayChoicesContextValue {
  const context = useContext(PlayChoicesContext);
  if (!context) {
    throw new Error('usePlayChoices must be used within PlayProviders');
  }
  return context;
}

export function usePlaySelection(): SelectionContextValue {
  const context = useContext(PlaySelectionContext);
  if (!context) {
    throw new Error('usePlaySelection must be used within PlayProviders');
  }
  return context;
}

export function usePlayTurn(): TurnContextValue {
  const context = useContext(PlayTurnContext);
  if (!context) {
    throw new Error('usePlayTurn must be used within PlayProviders');
  }
  return context;
}

export function usePlayTargeting(): PlayTargetingContextValue {
  const context = useContext(PlayTargetingContext);
  if (!context) {
    throw new Error('usePlayTargeting must be used within PlayProviders');
  }
  return context;
}

export function usePlayCasting(): CastingContextValue {
  const context = useContext(PlayCastingContext);
  if (!context) {
    throw new Error('usePlayCasting must be used within PlayProviders');
  }
  return context;
}

export function usePlaySetup(): SetupContextValue {
  const context = useContext(PlaySetupContext);
  if (!context) {
    throw new Error('usePlaySetup must be used within PlayProviders');
  }
  return context;
}

// ============================================================================
// Internal State Hook
// ============================================================================

function usePlayStateInternal() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);
  const [selectedHandId, setSelectedHandId] = useState<string | null>(null);
  const [selectedCommandId, setSelectedCommandId] = useState<string | null>(null);
  const [selectedBattlefieldId, setSelectedBattlefieldId] = useState<string | null>(null);
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});
  const [enterChoices, setEnterChoices] = useState<Record<string, string>>({});
  const [highlightedReplacementKey, setHighlightedReplacementKey] = useState<string | null>(null);
  const [combatDamageAssignments, setCombatDamageAssignments] = useState<Record<string, Record<string, number>>>({});
  const [selectedStackIndex, setSelectedStackIndex] = useState<number | null>(null);
  const [autoPayWard, setAutoPayWard] = useState(true);
  const [selectedAlternativeCostTag, setSelectedAlternativeCostTag] = useState<string | null>(null);
  const [selectedModalModes, setSelectedModalModes] = useState<string[]>([]);
  const [optionalCostSelections, setOptionalCostSelections] = useState<Record<string, number>>({});
  const [conspireTaps, setConspireTaps] = useState<string[]>([]);
  const [spliceSelections, setSpliceSelections] = useState<string[]>([]);
  const { abilityGraphs, loadAbilityGraphForObject } = useAbilityGraphs({
    gameState,
    cardMap,
    setGameState,
  });

  const { deckList, selectedDeckIds, loading: setupLoading, canStart, handleSelectDeck, startGame } = useGameSetup({
    setGameState,
    setCardMap,
    setPriorityPlayer,
    setGameId,
    setError,
  });

  useEffect(() => {
    if (gameId || gameState) return;
    const storedGameId = localStorage.getItem('play.game_id');
    if (storedGameId) {
      setGameId(storedGameId);
    }
  }, [gameId, gameState]);

  useEffect(() => {
    if (!gameId || gameState) return;
    const loadSession = async () => {
      try {
        const session = await engineApi.getSession(gameId);
        setGameState(session.game_state);
        const storedCardMap = localStorage.getItem('play.card_map');
        if (storedCardMap) {
          setCardMap(JSON.parse(storedCardMap));
        }
        if (typeof session.game_state.turn.priority_current_index === 'number') {
          const alivePlayers = session.game_state.players.filter((player) => !player.has_lost);
          const current = alivePlayers[session.game_state.turn.priority_current_index];
          setPriorityPlayer(current?.id ?? null);
        }
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load game session');
        localStorage.removeItem('play.game_id');
        localStorage.removeItem('play.card_map');
        setGameId(null);
      }
    };
    loadSession();
  }, [gameId, gameState, setCardMap, setError, setGameState, setPriorityPlayer]);

  const {
    selectedAttackers,
    selectedBlockers,
    selectedBlockerOrder,
    activeAttackerId,
    setActiveAttackerId,
    selectedDefenderId,
    setSelectedDefenderId,
    toggleAttacker,
    toggleBlocker,
    blockersPayload,
    activeBlockerOrder,
    setSelectedBlockerOrder,
  } = useCombatSelection({ gameState });

  const objectMap = useMemo(
    () => new Map(gameState?.objects.map((obj) => [obj.id, obj]) ?? []),
    [gameState?.objects]
  );

  const replacementConflicts = useReplacementConflicts(gameState);
  const hasUnresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.some(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );
  const unresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.filter(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );

  const hasFirstStrikeCombat = useMemo(() => computeHasFirstStrikeCombat(gameState), [gameState]);
  const combatDamagePass = useMemo(() => {
    if (!hasFirstStrikeCombat) return null;
    const resolved = gameState?.turn?.combat_state?.first_strike_resolved;
    return resolved ? 'regular' : 'first_strike';
  }, [gameState, hasFirstStrikeCombat]);
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
  useEffect(() => {
    if (unresolvedDamageReplacements.length === 0) {
      setHighlightedReplacementKey(null);
      return;
    }
    if (!highlightedReplacementKey || !unresolvedDamageReplacements.some((entry) => entry.key === highlightedReplacementKey)) {
      setHighlightedReplacementKey(unresolvedDamageReplacements[0].key);
    }
  }, [highlightedReplacementKey, unresolvedDamageReplacements]);

  const { runEngineAction } = useEngineActions({
    gameState,
    gameId,
    replacementChoices,
    setGameState,
    setPriorityPlayer,
    setLoading,
    setError,
  });

  const {
    currentPriority,
    activePlayerIndex,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    combatState,
    isPriorityActivePlayer,
    isPriorityDefender,
  } = useTurnState({ gameState, priorityPlayer });
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
          const canBlockFly =
            blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
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
          const canBlockFly =
            blocker.keywords?.includes('Flying') || blocker.keywords?.includes('Reach');
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
  const selectedGraph = selectedHandId ? abilityGraphs[cardMap[selectedHandId]?.card_id ?? ''] : undefined;
  const selectedStackGraph =
    selectedStackIndex !== null ? (gameState?.stack?.[selectedStackIndex]?.payload as any)?.graph : undefined;
  const activeGraph = selectedStackGraph ?? selectedGraph;
  const modalChoiceConfig = useMemo(() => deriveModalConfig(activeGraph), [activeGraph]);
  const modalChoiceErrors = useMemo(
    () => buildModalChoiceErrors(modalChoiceConfig, selectedModalModes),
    [modalChoiceConfig, selectedModalModes]
  );
  useEffect(() => {
    setSelectedModalModes([]);
  }, [selectedGraph, selectedHandId]);
  const copySpellConfig = useMemo(() => {
    const nodes = selectedGraph?.nodes ?? [];
    const copyNode = nodes.find((node: any) => node?.type === 'EFFECT' && node?.data?.type === 'copy_spell');
    if (!copyNode) {
      return { enabled: false, amount: 0 };
    }
    const amount = Number(copyNode?.data?.amount ?? 1);
    const chooseNewTargets = !!copyNode?.data?.chooseNewTargets;
    return { enabled: chooseNewTargets && amount > 0, amount: Math.max(amount, 1) };
  }, [selectedGraph]);
  const [copyTargetSelections, setCopyTargetSelections] = useState<Array<{ objectIds: string[]; playerIds: number[] }>>([]);
  const [copyTargetErrorsGlobal, setCopyTargetErrorsGlobal] = useState<string[]>([]);
  useEffect(() => {
    if (!copySpellConfig.enabled) {
      setCopyTargetErrorsGlobal([]);
    }
  }, [copySpellConfig.enabled]);
  const {
    targetHints,
    selectedTargetObjectIds,
    setSelectedTargetObjectIds,
    selectedTargetPlayerIds,
    setSelectedTargetPlayerIds,
    objectTargetStatus,
    playerTargetStatus,
    stackTargetChecks,
    stackSpellObjects,
    filteredTargetableObjects,
    filteredTargetPlayers,
    shouldUseStackTargets,
    requiredTargets: requiredTargetsGlobal,
    distinctTargets: distinctTargetsGlobal,
    minTargets: minTargetsGlobal,
  } = useTargeting({
    gameState,
    selectedHandId,
    selectedGraph,
    currentPriority,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
  });
  const {
    targetGroups: effectTargetGroups,
    targetsByEffect,
    requiredTargetsByEffect,
    distinctTargetsByEffect,
    minTargetsByEffect,
    globalTargetErrors,
    allSelectedObjectIds: effectTargetObjectIds,
    allSelectedPlayerIds: effectTargetPlayerIds,
    clearAllTargets: clearEffectTargets,
  } = useEffectTargeting({
    gameState,
    selectedGraph: activeGraph,
    currentPriority,
    selectedHandId,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
  });
  const {
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
  } = useSearchChoices({
    gameState,
    selectedGraph: activeGraph,
    currentPriority,
    context: (() => {
      const stackContext =
        selectedStackIndex !== null
          ? (gameState?.stack?.[selectedStackIndex]?.payload?.context as Record<string, any> | undefined)
          : undefined;
      const targets = stackContext?.targets as Record<string, any> | undefined;
      if (stackContext) {
        return {
          sourceId: stackContext.source_id ?? null,
          triggeringSourceId: stackContext.triggering_source_id ?? null,
          triggeringAuraId: stackContext.triggering_aura_id ?? stackContext.triggering_source_id ?? null,
          triggeringSpellId: stackContext.triggering_spell_id ?? stackContext.triggering_source_id ?? null,
          targetId: targets?.target ?? targets?.spell_target ?? null,
        };
      }
      return {
        sourceId: selectedHandId ?? selectedBattlefieldId ?? null,
        triggeringSourceId: selectedHandId ?? null,
        triggeringAuraId: selectedHandId ?? null,
        targetId: selectedBattlefieldId ?? null,
      };
    })(),
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
  });
  const hasEffectTargets = effectTargetGroups.length > 0 || searchEntries.length > 0;
  const mergedTargetsByEffect = useMemo(() => {
    const result: Record<string, Record<string, any>> = { ...(targetsByEffect || {}) };
    Object.entries(searchTargetsByEffect).forEach(([nodeId, extra]) => {
      result[nodeId] = { ...(result[nodeId] || {}), ...(extra || {}) };
    });
    return result;
  }, [searchTargetsByEffect, targetsByEffect]);
  const copyTargetsByEffectCount = copySpellConfig.enabled && hasEffectTargets ? copySpellConfig.amount : 0;
  const {
    copyTargetGroups: copyEffectTargetGroups,
    copyTargetsByEffectList,
    copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList,
    copyTargetErrors,
  } = useCopyEffectTargeting({
    gameState,
    selectedGraph: activeGraph,
    currentPriority,
    selectedHandId,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
    copies: copyTargetsByEffectCount,
  });
  const resolvedTargetObjectIds = hasEffectTargets ? effectTargetObjectIds : selectedTargetObjectIds;
  const resolvedTargetPlayerIds = hasEffectTargets ? effectTargetPlayerIds : selectedTargetPlayerIds;
  useEffect(() => {
    if (!gameState || !copySpellConfig.enabled || hasEffectTargets) {
      setCopyTargetErrorsGlobal([]);
      return;
    }
    if (copyTargetSelections.length === 0) {
      setCopyTargetErrorsGlobal([]);
      return;
    }
    const contexts = copyTargetSelections.map((entry) => {
      const targets: Record<string, any> = {
        ...(entry.objectIds.length > 0 ? { target: entry.objectIds[0], targets: entry.objectIds } : {}),
        ...(entry.playerIds.length > 0 ? { target_player: entry.playerIds[0], target_players: entry.playerIds } : {}),
      };
      if (targetHints.playerFilter !== 'any') {
        targets.target_scope = targetHints.playerFilter;
      }
      if (targetHints.objectFilter !== 'any') {
        targets.target_object_scope = targetHints.objectFilter === 'controller' ? 'you_control' : 'opponent_control';
      }
      if (targetHints.objectTypes.size > 0) {
        targets.target_object_types = Array.from(targetHints.objectTypes);
      }
      return {
        controller_id: currentPriority,
        source_id: selectedHandId ?? undefined,
        targets,
        ...(requiredTargetsGlobal.length > 0 ? { required_targets_by_effect: { _global: requiredTargetsGlobal } } : {}),
        ...(distinctTargetsGlobal.length > 0 ? { distinct_targets_by_effect: { _global: distinctTargetsGlobal } } : {}),
        ...(Object.keys(minTargetsGlobal ?? {}).length > 0 ? { min_targets_by_effect: { _global: minTargetsGlobal } } : {}),
      };
    });
    const checkTargets = async () => {
      try {
        const response = await engineApi.execute({
          action: 'check_targets',
          game_state: gameState,
          contexts,
        });
        const checks = (response.result?.checks as Array<{ issues?: string[] }> | undefined) ?? [];
        const errors: string[] = [];
        checks.forEach((check, index) => {
          (check.issues ?? []).forEach((issue) => {
            errors.push(`Copy ${index + 1}: ${issue}`);
          });
        });
        setCopyTargetErrorsGlobal(errors);
      } catch {
        setCopyTargetErrorsGlobal([]);
      }
    };
    checkTargets();
  }, [
    copySpellConfig.enabled,
    copyTargetSelections,
    currentPriority,
    distinctTargetsGlobal,
    gameState,
    hasEffectTargets,
    minTargetsGlobal,
    requiredTargetsGlobal,
    selectedHandId,
    targetHints,
  ]);
  const targetSelectionErrors = useMemo(() => {
    if (hasEffectTargets) {
      const errors: string[] = [];
      effectTargetGroups.forEach((group) => {
        const min = group.minTargets ?? 0;
        if (min > 0) {
          const count = group.selectedObjectIds.length + group.selectedPlayerIds.length;
          if (count < min) {
            errors.push(`${group.label}: select at least ${min} target${min === 1 ? '' : 's'}.`);
          }
        }
        if (group.errors && group.errors.length > 0) {
          group.errors.forEach((error) => {
            errors.push(`${group.label}: ${error}`);
          });
        }
      });
      if (globalTargetErrors.length > 0) {
        errors.push(...globalTargetErrors);
      }
      if (searchErrors.length > 0) {
        errors.push(...searchErrors);
      }
      if (copyTargetErrors.length > 0) {
        errors.push(...copyTargetErrors);
      }
      return errors;
    }
    const min = minTargetsGlobal?.target ?? 0;
    const count = resolvedTargetObjectIds.length + resolvedTargetPlayerIds.length;
    if (min > 0 && count < min) {
      return [`Select at least ${min} target${min === 1 ? '' : 's'}.`];
    }
    if (copyTargetErrorsGlobal.length > 0) {
      return copyTargetErrorsGlobal;
    }
    return [];
  }, [
    effectTargetGroups,
    globalTargetErrors,
    searchErrors,
    hasEffectTargets,
    minTargetsGlobal,
    copyTargetErrors,
    copyTargetErrorsGlobal,
    resolvedTargetObjectIds.length,
    resolvedTargetPlayerIds.length,
  ]);
  useTurnReset({
    gameState,
    setReplacementChoices,
    setSelectedHandId,
    setSelectedBattlefieldId,
    setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds,
    setActiveAttackerId,
    setSelectedDefenderId,
    onResetTargets: clearEffectTargets,
  });
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

  useEffect(() => {
    if (!gameState) return;
    const stackLength = gameState.stack.length;
    if (stackLength === 0) {
      if (selectedStackIndex !== null) {
        setSelectedStackIndex(null);
      }
      return;
    }
    if (selectedStackIndex === null || selectedStackIndex >= stackLength) {
      setSelectedStackIndex(stackLength - 1);
    }
  }, [gameState, selectedStackIndex]);

  useEffect(() => {
    if (!gameState) return;
    if (gameState.replacement_choices) {
      setReplacementChoices(gameState.replacement_choices);
    }
    setSelectedHandId(null);
    setSelectedBattlefieldId(null);
    setSelectedTargetObjectIds([]);
    setSelectedTargetPlayerIds([]);
    clearEffectTargets();
  }, [gameState?.turn.step, gameState?.turn.turn_number]);

  const priorityPlayerState = gameState?.players.find((player) => player.id === currentPriority);
  const manaPool = priorityPlayerState?.mana_pool ?? {};
  const {
    wardTargets,
    wardPayments,
    setWardPayments,
    wardPaymentDetails,
    setWardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
  } = useWardPayments({
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    selectedTargetObjectIds: resolvedTargetObjectIds,
    manaPool,
    autoPayWard,
  });
  const enterChoiceConfig = useMemo(() => buildEnterChoiceConfig(selectedGraph), [selectedGraph]);
  const enterChoiceTargetOptions = useMemo(
    () => buildEnterChoiceTargetOptions(gameState, cardMap),
    [gameState, cardMap]
  );
  const enterChoiceErrors = useMemo(
    () => buildEnterChoiceErrors(enterChoiceConfig, enterChoices),
    [enterChoiceConfig, enterChoices]
  );
  const hasWardPaymentErrors = useMemo(
    () => Object.values(wardPaymentErrors).some((entries) => entries.length > 0),
    [wardPaymentErrors]
  );
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
  const hasActivatedAbility =
    selectedBattlefieldObject?.ability_graphs && selectedBattlefieldObject.ability_graphs.length > 0;
  const selectedHandObject = gameState?.objects.find((obj) => obj.id === selectedHandId);
  const clearSelectionsOnResolve = useCallback(() => {
    setSelectedHandId(null);
    setSelectedBattlefieldId(null);
    setSelectedTargetObjectIds([]);
    setSelectedTargetPlayerIds([]);
    clearEffectTargets();
    setSelectedModalModes([]);
    setSelectedAlternativeCostTag(null);
    setOptionalCostSelections({});
    setConspireTaps([]);
    setSpliceSelections([]);
    setEnterChoices({});
    setCopyTargetSelections([]);
  }, [
    clearEffectTargets,
    setConspireTaps,
    setCopyTargetSelections,
    setEnterChoices,
    setOptionalCostSelections,
    setSelectedAlternativeCostTag,
    setSelectedBattlefieldId,
    setSelectedHandId,
    setSelectedModalModes,
    setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds,
    setSpliceSelections,
  ]);
  useResolveCleanup({
    gameState,
    selectedHandId,
    onResolve: clearSelectionsOnResolve,
    onClearSelectedHand: setSelectedHandId,
  });
  const activatedCosts = useMemo(() => {
    if (!selectedBattlefieldObject?.ability_graphs?.length) return [];
    const graph = selectedBattlefieldObject.ability_graphs[0];
    const nodes = graph?.nodes ?? [];
    const activatedNode = nodes.find((node: any) => node?.type === 'ACTIVATED');
    return Array.isArray(activatedNode?.data?.costs) ? activatedNode?.data?.costs : [];
  }, [selectedBattlefieldObject]);
  const {
    costEntries: activationCosts,
    payments: activationPayments,
    setPayments: setActivationPayments,
    paymentDetails: activationPaymentDetails,
    setPaymentDetails: setActivationPaymentDetails,
    paymentErrors: activationCostErrors,
    paymentsPayload: activationCostPaymentsPayload,
  } = useActivationCosts({
    costs: activatedCosts,
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    manaPool,
  });
  const hasActivationCostErrors = activationCostErrors.length > 0;
  const additionalCosts = useMemo(
    () => deriveAdditionalCostsFromGraph(selectedGraph),
    [selectedGraph]
  );
  const {
    costEntries: additionalCastCosts,
    payments: additionalCastPayments,
    setPayments: setAdditionalCastPayments,
    paymentDetails: additionalCastPaymentDetails,
    setPaymentDetails: setAdditionalCastPaymentDetails,
    paymentErrors: additionalCastCostErrors,
    paymentsPayload: additionalCastPaymentsPayload,
  } = useActivationCosts({
    costs: additionalCosts,
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    manaPool,
  });
  const hasAdditionalCastCostErrors = additionalCastCostErrors.length > 0;
  const alternativeCostOptions = useMemo(
    () => deriveAlternativeCastCostsFromGraph(selectedGraph),
    [selectedGraph]
  );
  const alternativeExtraCostOptions = useMemo(
    () => deriveAlternativeExtraCostsFromGraph(selectedGraph, selectedAlternativeCostTag),
    [selectedGraph, selectedAlternativeCostTag]
  );
  const optionalCostOptions = useMemo(
    () => deriveOptionalCastCostsFromGraph(selectedGraph),
    [selectedGraph]
  );
  const optionalCopyCount = useMemo(() => {
    let total = 0;
    optionalCostOptions.forEach((option) => {
      const count = optionalCostSelections[option.tag] ?? 0;
      if (option.kind === 'replicate') {
        total += Math.max(0, count);
      }
      if (option.kind === 'conspire' && count > 0) {
        total += 1;
      }
    });
    return total;
  }, [optionalCostOptions, optionalCostSelections]);
  const copyTargetsEnabled = useMemo(
    () => copySpellConfig.enabled || optionalCopyCount > 0,
    [copySpellConfig.enabled, optionalCopyCount]
  );
  const copyTargetsCount = useMemo(
    () => (copySpellConfig.enabled ? copySpellConfig.amount : 0) + optionalCopyCount,
    [copySpellConfig.amount, copySpellConfig.enabled, optionalCopyCount]
  );
  useEffect(() => {
    if (!copyTargetsEnabled) {
      setCopyTargetSelections([]);
      return;
    }
    setCopyTargetSelections((prev) => {
      const next = [...prev];
      while (next.length < copyTargetsCount) {
        next.push({ objectIds: [], playerIds: [] });
      }
      return next.slice(0, copyTargetsCount);
    });
  }, [copyTargetsCount, copyTargetsEnabled]);
  const {
    costEntries: alternativeExtraCostEntries,
    payments: alternativeExtraPayments,
    setPayments: setAlternativeExtraPayments,
    paymentDetails: alternativeExtraPaymentDetails,
    setPaymentDetails: setAlternativeExtraPaymentDetails,
    paymentErrors: alternativeExtraCostErrors,
    paymentsPayload: alternativeExtraPaymentsPayload,
  } = useActivationCosts({
    costs: alternativeExtraCostOptions,
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    manaPool,
  });
  const hasAlternativeExtraCostErrors = alternativeExtraCostErrors.length > 0;

  useEffect(() => {
    if (!optionalCostOptions.length) {
      setOptionalCostSelections({});
      return;
    }
    setOptionalCostSelections((prev) => {
      const next: Record<string, number> = {};
      optionalCostOptions.forEach((option) => {
        const value = prev[option.tag];
        if (typeof value === 'number' && value > 0) {
          next[option.tag] = value;
        }
      });
      return next;
    });
  }, [optionalCostOptions, selectedHandId]);

  const optionalCostCosts = useMemo(() => {
    if (optionalCostOptions.length === 0) return [];
    const costs: any[] = [];
    optionalCostOptions.forEach((option) => {
      const count = optionalCostSelections[option.tag] ?? 0;
      if (count > 0) {
        const repeat = option.repeatable ? count : 1;
        for (let i = 0; i < repeat; i += 1) {
          costs.push(...option.costs);
        }
      }
    });
    return costs;
  }, [optionalCostOptions, optionalCostSelections]);
  const conspireSelected = useMemo(
    () => optionalCostOptions.some((option) => option.kind === 'conspire' && (optionalCostSelections[option.tag] ?? 0) > 0),
    [optionalCostOptions, optionalCostSelections]
  );
  const conspireOptions = useMemo(() => {
    if (!conspireSelected || !selectedHandObject) return [];
    const spellColors = new Set(selectedHandObject.colors ?? []);
    if (spellColors.size === 0) return [];
    const player = gameState?.players.find((entry) => entry.id === currentPriority);
    const battlefieldIds = player?.battlefield ?? [];
    return battlefieldIds
      .map((objectId) => objectMap.get(objectId))
      .filter((obj) => {
        if (!obj) return false;
        if (obj.tapped) return false;
        if (!obj.types?.includes('Creature')) return false;
        const colors = obj.colors ?? [];
        return colors.some((color) => spellColors.has(color));
      })
      .map((obj) => ({
        value: obj?.id ?? '',
        label: cardMap[obj?.id ?? '']?.name || obj?.name || obj?.id || '',
      }))
      .filter((entry) => entry.value);
  }, [cardMap, conspireSelected, currentPriority, gameState, objectMap, selectedHandObject]);
  const conspireError = conspireSelected && conspireTaps.length !== 2
    ? 'Select exactly two creatures.'
    : null;
  useEffect(() => {
    if (!conspireSelected) {
      setConspireTaps([]);
    }
  }, [conspireSelected, selectedHandId]);
  const handleToggleConspireTap = (value: string) => {
    setConspireTaps((prev) => {
      if (prev.includes(value)) {
        return prev.filter((entry) => entry !== value);
      }
      if (prev.length >= 2) {
        return prev;
      }
      return [...prev, value];
    });
  };
  const isArcaneSpell = !!selectedHandObject?.types?.includes('Arcane');
  useEffect(() => {
    if (!gameState || !isArcaneSpell) return;
    const player = gameState.players.find((entry) => entry.id === currentPriority);
    (player?.hand ?? []).forEach((objectId) => {
      loadAbilityGraphForObject(objectId);
    });
  }, [currentPriority, gameState, isArcaneSpell, loadAbilityGraphForObject]);
  const spliceOptions = useMemo(() => {
    if (!isArcaneSpell || !gameState) return [];
    const player = gameState.players.find((entry) => entry.id === currentPriority);
    const handIds = player?.hand ?? [];
    const graphMap: Record<string, any> = {};
    handIds.forEach((objectId) => {
      const cardId = cardMap[objectId]?.card_id;
      if (!cardId) return;
      const graph = abilityGraphs[cardId];
      if (graph) {
        graphMap[objectId] = graph;
      }
    });
    return deriveSpliceCardsFromHand(handIds, graphMap).map((entry) => ({
      cardId: entry.cardId,
      costs: entry.costs,
      label: cardMap[entry.cardId]?.name || objectMap.get(entry.cardId)?.name || entry.cardId,
    }));
  }, [abilityGraphs, cardMap, currentPriority, gameState, isArcaneSpell, objectMap]);
  useEffect(() => {
    if (!isArcaneSpell) {
      setSpliceSelections([]);
      return;
    }
    setSpliceSelections((prev) => prev.filter((id) => spliceOptions.some((entry) => entry.cardId === id)));
  }, [isArcaneSpell, selectedHandId, spliceOptions]);
  const handleToggleSpliceCard = (cardId: string) => {
    setSpliceSelections((prev) =>
      prev.includes(cardId) ? prev.filter((entry) => entry !== cardId) : [...prev, cardId]
    );
  };
  const spliceCostList = useMemo(() => {
    if (spliceSelections.length === 0) return [];
    return spliceSelections.flatMap(
      (id) => spliceOptions.find((option) => option.cardId === id)?.costs ?? []
    );
  }, [spliceOptions, spliceSelections]);
  const entwineSelected = useMemo(
    () => optionalCostOptions.some((option) => option.kind === 'entwine' && (optionalCostSelections[option.tag] ?? 0) > 0),
    [optionalCostOptions, optionalCostSelections]
  );
  const modalChoicesForCast = useMemo(() => {
    if (!entwineSelected || !modalChoiceConfig) return selectedModalModes;
    return modalChoiceConfig.modes.map((mode: any) => mode.id);
  }, [entwineSelected, modalChoiceConfig, selectedModalModes]);
  useEffect(() => {
    if (!entwineSelected || !modalChoiceConfig) return;
    setSelectedModalModes(modalChoiceConfig.modes.map((mode: any) => mode.id));
  }, [entwineSelected, modalChoiceConfig]);

  const {
    costEntries: optionalCostEntries,
    payments: optionalCostPayments,
    setPayments: setOptionalCostPayments,
    paymentDetails: optionalCostPaymentDetails,
    setPaymentDetails: setOptionalCostPaymentDetails,
    paymentErrors: optionalCostPaymentErrors,
    paymentsPayload: optionalCostPaymentsPayload,
  } = useActivationCosts({
    costs: optionalCostCosts,
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    manaPool,
  });
  const {
    costEntries: spliceCosts,
    payments: splicePayments,
    setPayments: setSplicePayments,
    paymentDetails: splicePaymentDetails,
    setPaymentDetails: setSplicePaymentDetails,
    paymentErrors: spliceCostErrors,
    paymentsPayload: splicePaymentsPayload,
  } = useActivationCosts({
    costs: spliceCostList,
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: currentPriority,
    manaPool,
  });
  const hasOptionalCostErrors =
    optionalCostPaymentErrors.length > 0 ||
    spliceCostErrors.length > 0 ||
    (conspireSelected && conspireTaps.length !== 2);
  const optionalCostErrors = useMemo(
    () => optionalCostPaymentErrors,
    [optionalCostPaymentErrors]
  );

  useEffect(() => {
    if (enterChoiceConfig.length === 0) {
      setEnterChoices({});
      return;
    }
    setEnterChoices((prev) => buildEnterChoiceDefaults(enterChoiceConfig, prev));
  }, [selectedHandId, enterChoiceConfig]);

  const handleToggleOptionalCost = (tag: string) => {
    setOptionalCostSelections((prev) => {
      const next = { ...prev };
      if ((next[tag] ?? 0) > 0) {
        delete next[tag];
        return next;
      }
      next[tag] = 1;
      return next;
    });
  };

  const handleUpdateOptionalCostCount = (tag: string, count: number) => {
    setOptionalCostSelections((prev) => ({
      ...prev,
      [tag]: Math.max(0, count),
    }));
  };

  const handleToggleModalMode = (modeId: string) => {
    if (entwineSelected) return;
    setSelectedModalModes((prev) => {
      if (!modalChoiceConfig) return prev;
      if (modalChoiceConfig.max === 1) {
        return prev.includes(modeId) ? [] : [modeId];
      }
      const exists = prev.includes(modeId);
      const next = exists ? prev.filter((entry) => entry !== modeId) : [...prev, modeId];
      if (modalChoiceConfig.max !== null && next.length > modalChoiceConfig.max) {
        return next.slice(0, modalChoiceConfig.max);
      }
      return next;
    });
  };

  useEffect(() => {
    setSelectedAlternativeCostTag(null);
  }, [selectedHandId]);

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

  const { buildCastContext } = useCastContext({
    currentPriority,
    selectedHandId,
    selectedTargetObjectIds: resolvedTargetObjectIds,
    selectedTargetPlayerIds: resolvedTargetPlayerIds,
    useStackTargets: shouldUseStackTargets,
    maxObjectTargets: targetHints.maxObjectTargets ?? undefined,
    maxPlayerTargets: targetHints.maxPlayerTargets ?? undefined,
    targetPlayerFilter: targetHints.playerFilter,
    targetObjectFilter: targetHints.objectFilter,
    targetObjectTypes: Array.from(targetHints.objectTypes ?? []),
    targetsByEffect: hasEffectTargets ? mergedTargetsByEffect : undefined,
    requiredTargetsByEffect: hasEffectTargets ? requiredTargetsByEffect : undefined,
    requiredTargetsGlobal: !hasEffectTargets ? requiredTargetsGlobal : undefined,
    distinctTargetsByEffect: hasEffectTargets ? distinctTargetsByEffect : undefined,
    distinctTargetsGlobal: !hasEffectTargets ? distinctTargetsGlobal : undefined,
    minTargetsByEffect: hasEffectTargets ? minTargetsByEffect : undefined,
    minTargetsGlobal: !hasEffectTargets ? minTargetsGlobal : undefined,
    copyChooseNewTargets: copyTargetsEnabled,
    copyTargetsList: !hasEffectTargets
      ? copyTargetSelections.map((entry) => ({
          ...(entry.objectIds.length > 0 ? { target: entry.objectIds[0], targets: entry.objectIds } : {}),
          ...(entry.playerIds.length > 0 ? { target_player: entry.playerIds[0], target_players: entry.playerIds } : {}),
        }))
      : [],
    copyTargetsByEffectList: hasEffectTargets ? copyTargetsByEffectList : [],
    copyRequiredTargetsByEffectList: hasEffectTargets
      ? copyRequiredTargetsByEffectList
      : copyTargetsEnabled
      ? copyTargetSelections.map(() => ({ _global: requiredTargetsGlobal }))
      : [],
    copyDistinctTargetsByEffectList: hasEffectTargets
      ? copyDistinctTargetsByEffectList
      : copyTargetsEnabled
      ? copyTargetSelections.map(() => ({ _global: distinctTargetsGlobal }))
      : [],
    copyMinTargetsByEffectList: hasEffectTargets
      ? copyMinTargetsByEffectList
      : copyTargetsEnabled
      ? copyTargetSelections.map(() => ({ _global: minTargetsGlobal }))
      : [],
    enterChoices,
    modalChoices: modalChoicesForCast,
    optionalCostSelections,
    optionalCostPayments: optionalCostPaymentsPayload,
    conspireTaps,
    spliceCards: spliceSelections,
    splicePayments: splicePaymentsPayload,
  });
  const {
    preparedCast,
    manaPayment,
    setManaPayment,
    manaPaymentDetail,
    setManaPaymentDetail,
    autoPayMana,
    setAutoPayMana,
    isComplexCost,
    manaPaymentStatus,
    costLabel,
    handlePrepareCast,
    handleFinalizeCast,
  } = useCasting({
    selectedHandId,
    selectedCommandId,
    currentPriority,
    abilityGraphs,
    cardMap,
    manaPool,
    buildCastContext,
    wardPayments: wardPaymentsPayload,
    autoPayWard,
    additionalCostPayments: additionalCastPaymentsPayload,
    alternativeCostTag: selectedAlternativeCostTag,
    alternativeCostPayments: alternativeExtraPaymentsPayload,
    runEngineAction,
  });

  return {
    loading,
    error,
    gameState,
    cardMap,
    priorityPlayer,
    setPriorityPlayer,
    selectedHandId,
    setSelectedHandId,
    selectedCommandId,
    setSelectedCommandId,
    selectedBattlefieldId,
    setSelectedBattlefieldId,
    replacementChoices,
    setReplacementChoices,
    enterChoices,
    setEnterChoices,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    combatDamageAssignments,
    setCombatDamageAssignments,
    selectedStackIndex,
    setSelectedStackIndex,
    autoPayWard,
    setAutoPayWard,
    selectedAlternativeCostTag,
    setSelectedAlternativeCostTag,
    selectedModalModes,
    setSelectedModalModes,
    optionalCostSelections,
    setOptionalCostSelections,
    conspireTaps,
    setConspireTaps,
    spliceSelections,
    setSpliceSelections,
    abilityGraphs,
    loadAbilityGraphForObject,
    deckList,
    selectedDeckIds,
    setupLoading,
    canStart,
    handleSelectDeck,
    startGame,
    selectedAttackers,
    selectedBlockers,
    selectedBlockerOrder,
    activeAttackerId,
    setActiveAttackerId,
    selectedDefenderId,
    setSelectedDefenderId,
    toggleAttacker,
    toggleBlocker,
    blockersPayload,
    activeBlockerOrder,
    setSelectedBlockerOrder,
    objectMap,
    replacementConflicts,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    hasFirstStrikeCombat,
    combatDamagePass,
    hasManualCombatChoices,
    runEngineAction,
    currentPriority,
    activePlayerIndex,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    combatState,
    isPriorityActivePlayer,
    isPriorityDefender,
    blockerErrors,
    blockerErrorMap,
    selectedGraph,
    modalChoiceConfig,
    modalChoiceErrors,
    copySpellConfig,
    copyTargetSelections,
    setCopyTargetSelections,
    copyTargetErrorsGlobal,
    targetHints,
    selectedTargetObjectIds,
    setSelectedTargetObjectIds,
    selectedTargetPlayerIds,
    setSelectedTargetPlayerIds,
    objectTargetStatus,
    playerTargetStatus,
    stackTargetChecks,
    stackSpellObjects,
    filteredTargetableObjects,
    filteredTargetPlayers,
    shouldUseStackTargets,
    requiredTargetsGlobal,
    distinctTargetsGlobal,
    minTargetsGlobal,
    effectTargetGroups,
    targetsByEffect,
    requiredTargetsByEffect,
    distinctTargetsByEffect,
    minTargetsByEffect,
    globalTargetErrors,
    effectTargetObjectIds,
    effectTargetPlayerIds,
    clearEffectTargets,
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
    hasEffectTargets,
    mergedTargetsByEffect,
    copyTargetsByEffectCount,
    copyEffectTargetGroups,
    copyTargetsByEffectList,
    copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList,
    copyTargetErrors,
    resolvedTargetObjectIds,
    resolvedTargetPlayerIds,
    targetSelectionErrors,
    defendingObjectId,
    selectedDefendingPlayerId,
    defendingPlayerId,
    defenderOptions,
    manaPool,
    wardTargets,
    wardPayments,
    setWardPayments,
    wardPaymentDetails,
    setWardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
    enterChoiceConfig,
    enterChoiceTargetOptions,
    enterChoiceErrors,
    hasWardPaymentErrors,
    selectedBattlefieldObject,
    hasActivatedAbility,
    selectedHandObject,
    activatedCosts,
    activationCosts,
    activationPayments,
    setActivationPayments,
    activationPaymentDetails,
    setActivationPaymentDetails,
    activationCostErrors,
    activationCostPaymentsPayload,
    hasActivationCostErrors,
    additionalCosts,
    additionalCastCosts,
    additionalCastPayments,
    setAdditionalCastPayments,
    additionalCastPaymentDetails,
    setAdditionalCastPaymentDetails,
    additionalCastCostErrors,
    additionalCastPaymentsPayload,
    hasAdditionalCastCostErrors,
    alternativeCostOptions,
    alternativeExtraCostOptions,
    optionalCostOptions,
    optionalCopyCount,
    copyTargetsEnabled,
    copyTargetsCount,
    alternativeExtraCostEntries,
    alternativeExtraPayments,
    setAlternativeExtraPayments,
    alternativeExtraPaymentDetails,
    setAlternativeExtraPaymentDetails,
    alternativeExtraCostErrors,
    alternativeExtraPaymentsPayload,
    hasAlternativeExtraCostErrors,
    optionalCostCosts,
    conspireSelected,
    conspireOptions,
    conspireError,
    handleToggleConspireTap,
    isArcaneSpell,
    spliceOptions,
    handleToggleSpliceCard,
    spliceCostList,
    entwineSelected,
    modalChoicesForCast,
    optionalCostEntries,
    optionalCostPayments,
    setOptionalCostPayments,
    optionalCostPaymentDetails,
    setOptionalCostPaymentDetails,
    optionalCostPaymentErrors,
    optionalCostPaymentsPayload,
    spliceCosts,
    splicePayments,
    setSplicePayments,
    splicePaymentDetails,
    setSplicePaymentDetails,
    spliceCostErrors,
    splicePaymentsPayload,
    hasOptionalCostErrors,
    optionalCostErrors,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    handleToggleModalMode,
    buildCastContext,
    preparedCast,
    manaPayment,
    setManaPayment,
    manaPaymentDetail,
    setManaPaymentDetail,
    autoPayMana,
    setAutoPayMana,
    isComplexCost,
    manaPaymentStatus,
    costLabel,
    handlePrepareCast,
    handleFinalizeCast,
  };
}

// ============================================================================
// Provider Component
// ============================================================================

export function PlayProviders({ children }: { children: React.ReactNode }) {
  const playState = usePlayStateInternal();

  // Derive GameContext-compatible value
  const gameValue = useMemo<GameContextValue>(() => ({
    gameId: null,
    gameState: playState.gameState,
    cardMap: playState.cardMap,
    loading: playState.loading,
    error: playState.error,
    priorityPlayer: playState.priorityPlayer,
    setGameId: () => {},
    setGameState: () => {},
    setCardMap: () => {},
    setPriorityPlayer: playState.setPriorityPlayer,
    setLoading: () => {},
    setError: () => {},
    runEngineAction: playState.runEngineAction as unknown as GameContextValue['runEngineAction'],
  }), [
    playState.gameState,
    playState.cardMap,
    playState.loading,
    playState.error,
    playState.priorityPlayer,
    playState.setPriorityPlayer,
    playState.runEngineAction,
  ]);

  // Derive CombatContext-compatible value
  const combatValue = useMemo<PlayCombatContextValue>(() => ({
    selectedAttackers: playState.selectedAttackers,
    selectedBlockers: playState.selectedBlockers,
    selectedBlockerOrder: playState.selectedBlockerOrder,
    activeAttackerId: playState.activeAttackerId,
    selectedDefenderId: playState.selectedDefenderId,
    combatDamageAssignments: playState.combatDamageAssignments,
    combatState: playState.combatState,
    defenderOptions: playState.defenderOptions,
    defendingPlayerId: playState.defendingPlayerId,
    defendingObjectId: playState.defendingObjectId,
    hasFirstStrikeCombat: playState.hasFirstStrikeCombat,
    combatDamagePass: playState.combatDamagePass as 'first_strike' | 'regular' | null,
    hasManualCombatChoices: playState.hasManualCombatChoices,
    blockerErrors: playState.blockerErrors,
    blockerErrorMap: playState.blockerErrorMap,
    activeBlockerOrder: playState.activeBlockerOrder,
    blockersPayload: playState.blockersPayload,
    setActiveAttackerId: playState.setActiveAttackerId,
    setSelectedDefenderId: playState.setSelectedDefenderId,
    toggleAttacker: playState.toggleAttacker,
    toggleBlocker: playState.toggleBlocker,
    setSelectedBlockerOrder: playState.setSelectedBlockerOrder,
    setCombatDamageAssignments: playState.setCombatDamageAssignments,
  }), [
    playState.selectedAttackers,
    playState.selectedBlockers,
    playState.selectedBlockerOrder,
    playState.activeAttackerId,
    playState.selectedDefenderId,
    playState.combatDamageAssignments,
    playState.combatState,
    playState.defenderOptions,
    playState.defendingPlayerId,
    playState.defendingObjectId,
    playState.hasFirstStrikeCombat,
    playState.combatDamagePass,
    playState.hasManualCombatChoices,
    playState.blockerErrors,
    playState.blockerErrorMap,
    playState.activeBlockerOrder,
    playState.blockersPayload,
    playState.setActiveAttackerId,
    playState.setSelectedDefenderId,
    playState.toggleAttacker,
    playState.toggleBlocker,
    playState.setSelectedBlockerOrder,
    playState.setCombatDamageAssignments,
  ]);

  // Derive ChoicesContext-compatible value
  const choicesValue = useMemo<PlayChoicesContextValue>(() => ({
    modalChoiceConfig: playState.modalChoiceConfig,
    selectedModalModes: playState.selectedModalModes,
    modalChoiceErrors: playState.modalChoiceErrors,
    modalChoicesForCast: playState.modalChoicesForCast,
    entwineSelected: playState.entwineSelected,
    handleToggleModalMode: playState.handleToggleModalMode,
    setSelectedModalModes: playState.setSelectedModalModes,
    enterChoiceConfig: playState.enterChoiceConfig,
    enterChoices: playState.enterChoices,
    enterChoiceErrors: playState.enterChoiceErrors,
    enterChoiceTargetOptions: playState.enterChoiceTargetOptions,
    setEnterChoices: playState.setEnterChoices,
    onEnterChoiceChange: (type: string, value: string) => {
      playState.setEnterChoices((prev: Record<string, string>) => ({ ...prev, [type]: value }));
    },
    replacementChoices: playState.replacementChoices,
    replacementConflicts: playState.replacementConflicts,
    hasUnresolvedDamageReplacements: playState.hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements: playState.unresolvedDamageReplacements,
    highlightedReplacementKey: playState.highlightedReplacementKey,
    setReplacementChoices: playState.setReplacementChoices,
    setHighlightedReplacementKey: playState.setHighlightedReplacementKey,
    wardTargets: playState.wardTargets,
    wardPayments: playState.wardPayments,
    wardPaymentDetails: playState.wardPaymentDetails,
    wardPaymentErrors: playState.wardPaymentErrors,
    wardPaymentsPayload: playState.wardPaymentsPayload ?? {},
    hasWardPaymentErrors: playState.hasWardPaymentErrors,
    autoPayWard: playState.autoPayWard,
    setWardPayments: playState.setWardPayments,
    setWardPaymentDetails: playState.setWardPaymentDetails,
    setAutoPayWard: playState.setAutoPayWard,
  }), [
    playState.modalChoiceConfig,
    playState.selectedModalModes,
    playState.modalChoiceErrors,
    playState.modalChoicesForCast,
    playState.entwineSelected,
    playState.handleToggleModalMode,
    playState.setSelectedModalModes,
    playState.enterChoiceConfig,
    playState.enterChoices,
    playState.enterChoiceErrors,
    playState.enterChoiceTargetOptions,
    playState.setEnterChoices,
    playState.replacementChoices,
    playState.replacementConflicts,
    playState.hasUnresolvedDamageReplacements,
    playState.unresolvedDamageReplacements,
    playState.highlightedReplacementKey,
    playState.setReplacementChoices,
    playState.setHighlightedReplacementKey,
    playState.wardTargets,
    playState.wardPayments,
    playState.wardPaymentDetails,
    playState.wardPaymentErrors,
    playState.wardPaymentsPayload,
    playState.hasWardPaymentErrors,
    playState.autoPayWard,
    playState.setWardPayments,
    playState.setWardPaymentDetails,
    playState.setAutoPayWard,
  ]);

  // Derive SelectionContext-compatible value
  const selectionValue = useMemo<SelectionContextValue>(() => ({
    selectedHandId: playState.selectedHandId,
    selectedCommandId: playState.selectedCommandId,
    selectedBattlefieldId: playState.selectedBattlefieldId,
    selectedStackIndex: playState.selectedStackIndex,
    setSelectedHandId: playState.setSelectedHandId,
    setSelectedCommandId: playState.setSelectedCommandId,
    setSelectedBattlefieldId: playState.setSelectedBattlefieldId,
    setSelectedStackIndex: playState.setSelectedStackIndex,
    loadAbilityGraphForObject: playState.loadAbilityGraphForObject,
    abilityGraphs: playState.abilityGraphs,
    selectedGraph: playState.selectedGraph,
  }), [
    playState.selectedHandId,
    playState.selectedCommandId,
    playState.selectedBattlefieldId,
    playState.selectedStackIndex,
    playState.setSelectedHandId,
    playState.setSelectedCommandId,
    playState.setSelectedBattlefieldId,
    playState.setSelectedStackIndex,
    playState.loadAbilityGraphForObject,
    playState.abilityGraphs,
    playState.selectedGraph,
  ]);

  // Derive TurnContext-compatible value
  const turnValue = useMemo<TurnContextValue>(() => ({
    currentPriority: playState.currentPriority,
    activePlayerIndex: playState.activePlayerIndex,
    isMainPhase: playState.isMainPhase,
    isDeclareAttackers: playState.isDeclareAttackers,
    isDeclareBlockers: playState.isDeclareBlockers,
    isCombatDamage: playState.isCombatDamage,
    isPriorityActivePlayer: playState.isPriorityActivePlayer,
    isPriorityDefender: playState.isPriorityDefender,
    objectMap: playState.objectMap,
  }), [
    playState.currentPriority,
    playState.activePlayerIndex,
    playState.isMainPhase,
    playState.isDeclareAttackers,
    playState.isDeclareBlockers,
    playState.isCombatDamage,
    playState.isPriorityActivePlayer,
    playState.isPriorityDefender,
    playState.objectMap,
  ]);

  // Derive TargetingContext-compatible value
  const targetingValue = useMemo<PlayTargetingContextValue>(() => ({
    targetHints: playState.targetHints,
    selectedTargetObjectIds: playState.selectedTargetObjectIds ?? [],
    selectedTargetPlayerIds: playState.selectedTargetPlayerIds ?? [],
    objectTargetStatus: playState.objectTargetStatus,
    playerTargetStatus: playState.playerTargetStatus,
    stackTargetChecks: Object.values(playState.stackTargetChecks ?? {}),
    stackSpellObjects: playState.stackSpellObjects,
    filteredTargetableObjects: playState.filteredTargetableObjects,
    filteredTargetPlayers: playState.filteredTargetPlayers,
    shouldUseStackTargets: playState.shouldUseStackTargets,
    requiredTargetsGlobal: playState.requiredTargetsGlobal,
    distinctTargetsGlobal: playState.distinctTargetsGlobal,
    minTargetsGlobal: playState.minTargetsGlobal,
    effectTargetGroups: playState.effectTargetGroups,
    targetsByEffect: playState.targetsByEffect,
    requiredTargetsByEffect: playState.requiredTargetsByEffect,
    distinctTargetsByEffect: playState.distinctTargetsByEffect,
    minTargetsByEffect: playState.minTargetsByEffect,
    globalTargetErrors: playState.globalTargetErrors,
    effectTargetObjectIds: playState.effectTargetObjectIds,
    effectTargetPlayerIds: playState.effectTargetPlayerIds,
    hasEffectTargets: playState.hasEffectTargets,
    mergedTargetsByEffect: playState.mergedTargetsByEffect,
    searchEntries: playState.searchEntries,
    searchTargetsByEffect: playState.searchTargetsByEffect,
    searchErrors: playState.searchErrors,
    copySpellConfig: playState.copySpellConfig,
    copyTargetSelections: playState.copyTargetSelections,
    copyTargetErrorsGlobal: playState.copyTargetErrorsGlobal,
    copyTargetsByEffectCount: playState.copyTargetsByEffectCount,
    copyEffectTargetGroups: playState.copyEffectTargetGroups,
    copyTargetsByEffectList: playState.copyTargetsByEffectList,
    copyRequiredTargetsByEffectList: playState.copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList: playState.copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList: playState.copyMinTargetsByEffectList,
    copyTargetErrors: playState.copyTargetErrors,
    resolvedTargetObjectIds: playState.resolvedTargetObjectIds,
    resolvedTargetPlayerIds: playState.resolvedTargetPlayerIds,
    targetSelectionErrors: playState.targetSelectionErrors,
    setSelectedTargetObjectIds: playState.setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds: playState.setSelectedTargetPlayerIds,
    setCopyTargetSelections: playState.setCopyTargetSelections,
    clearEffectTargets: playState.clearEffectTargets,
  }), [
    playState.targetHints,
    playState.selectedTargetObjectIds,
    playState.selectedTargetPlayerIds,
    playState.objectTargetStatus,
    playState.playerTargetStatus,
    playState.stackTargetChecks,
    playState.stackSpellObjects,
    playState.filteredTargetableObjects,
    playState.filteredTargetPlayers,
    playState.shouldUseStackTargets,
    playState.requiredTargetsGlobal,
    playState.distinctTargetsGlobal,
    playState.minTargetsGlobal,
    playState.effectTargetGroups,
    playState.targetsByEffect,
    playState.requiredTargetsByEffect,
    playState.distinctTargetsByEffect,
    playState.minTargetsByEffect,
    playState.globalTargetErrors,
    playState.effectTargetObjectIds,
    playState.effectTargetPlayerIds,
    playState.hasEffectTargets,
    playState.mergedTargetsByEffect,
    playState.searchEntries,
    playState.searchTargetsByEffect,
    playState.searchErrors,
    playState.copySpellConfig,
    playState.copyTargetSelections,
    playState.copyTargetErrorsGlobal,
    playState.copyTargetsByEffectCount,
    playState.copyEffectTargetGroups,
    playState.copyTargetsByEffectList,
    playState.copyRequiredTargetsByEffectList,
    playState.copyDistinctTargetsByEffectList,
    playState.copyMinTargetsByEffectList,
    playState.copyTargetErrors,
    playState.resolvedTargetObjectIds,
    playState.resolvedTargetPlayerIds,
    playState.targetSelectionErrors,
    playState.setSelectedTargetObjectIds,
    playState.setSelectedTargetPlayerIds,
    playState.setCopyTargetSelections,
    playState.clearEffectTargets,
  ]);

  // Derive CastingContext-compatible value
  const castingValue = useMemo<CastingContextValue>(() => ({
    preparedCast: playState.preparedCast,
    manaPool: playState.manaPool,
    manaPayment: playState.manaPayment,
    manaPaymentDetail: playState.manaPaymentDetail,
    manaPaymentStatus: playState.manaPaymentStatus,
    costLabel: playState.costLabel,
    autoPayMana: playState.autoPayMana,
    isComplexCost: playState.isComplexCost,
    handlePrepareCast: playState.handlePrepareCast,
    handleFinalizeCast: playState.handleFinalizeCast,
    setManaPayment: playState.setManaPayment,
    setManaPaymentDetail: playState.setManaPaymentDetail,
    setAutoPayMana: playState.setAutoPayMana,
    buildCastContext: playState.buildCastContext,
    activationCosts: playState.activationCosts,
    activationPayments: playState.activationPayments,
    activationPaymentDetails: playState.activationPaymentDetails,
    activationCostErrors: playState.activationCostErrors,
    hasActivationCostErrors: playState.hasActivationCostErrors,
    activationCostPaymentsPayload: playState.activationCostPaymentsPayload,
    setActivationPayments: playState.setActivationPayments,
    setActivationPaymentDetails: playState.setActivationPaymentDetails,
    additionalCastCosts: playState.additionalCastCosts,
    additionalCastPayments: playState.additionalCastPayments,
    additionalCastPaymentDetails: playState.additionalCastPaymentDetails,
    additionalCastCostErrors: playState.additionalCastCostErrors,
    hasAdditionalCastCostErrors: playState.hasAdditionalCastCostErrors,
    setAdditionalCastPayments: playState.setAdditionalCastPayments,
    setAdditionalCastPaymentDetails: playState.setAdditionalCastPaymentDetails,
    alternativeCostOptions: playState.alternativeCostOptions,
    selectedAlternativeCostTag: playState.selectedAlternativeCostTag,
    alternativeExtraCostEntries: playState.alternativeExtraCostEntries,
    alternativeExtraPayments: playState.alternativeExtraPayments,
    alternativeExtraPaymentDetails: playState.alternativeExtraPaymentDetails,
    alternativeExtraCostErrors: playState.alternativeExtraCostErrors,
    hasAlternativeExtraCostErrors: playState.hasAlternativeExtraCostErrors,
    setSelectedAlternativeCostTag: playState.setSelectedAlternativeCostTag,
    setAlternativeExtraPayments: playState.setAlternativeExtraPayments,
    setAlternativeExtraPaymentDetails: playState.setAlternativeExtraPaymentDetails,
    optionalCostOptions: playState.optionalCostOptions,
    optionalCostSelections: playState.optionalCostSelections,
    optionalCostEntries: playState.optionalCostEntries,
    optionalCostPayments: playState.optionalCostPayments,
    optionalCostPaymentDetails: playState.optionalCostPaymentDetails,
    optionalCostErrors: playState.optionalCostErrors,
    optionalCostPaymentErrors: playState.optionalCostPaymentErrors,
    hasOptionalCostErrors: playState.hasOptionalCostErrors,
    handleToggleOptionalCost: playState.handleToggleOptionalCost,
    handleUpdateOptionalCostCount: playState.handleUpdateOptionalCostCount,
    setOptionalCostPayments: playState.setOptionalCostPayments,
    setOptionalCostPaymentDetails: playState.setOptionalCostPaymentDetails,
    conspireSelected: playState.conspireSelected,
    conspireOptions: playState.conspireOptions,
    conspireTaps: playState.conspireTaps,
    conspireError: playState.conspireError,
    handleToggleConspireTap: playState.handleToggleConspireTap,
    spliceOptions: playState.spliceOptions,
    spliceSelections: playState.spliceSelections,
    spliceCosts: playState.spliceCosts,
    splicePayments: playState.splicePayments,
    splicePaymentDetails: playState.splicePaymentDetails,
    spliceCostErrors: playState.spliceCostErrors,
    handleToggleSpliceCard: playState.handleToggleSpliceCard,
    setSplicePayments: playState.setSplicePayments,
    setSplicePaymentDetails: playState.setSplicePaymentDetails,
  }), [
    playState.preparedCast,
    playState.manaPool,
    playState.manaPayment,
    playState.manaPaymentDetail,
    playState.manaPaymentStatus,
    playState.costLabel,
    playState.autoPayMana,
    playState.isComplexCost,
    playState.handlePrepareCast,
    playState.handleFinalizeCast,
    playState.setManaPayment,
    playState.setManaPaymentDetail,
    playState.setAutoPayMana,
    playState.buildCastContext,
    playState.activationCosts,
    playState.activationPayments,
    playState.activationPaymentDetails,
    playState.activationCostErrors,
    playState.hasActivationCostErrors,
    playState.activationCostPaymentsPayload,
    playState.setActivationPayments,
    playState.setActivationPaymentDetails,
    playState.additionalCastCosts,
    playState.additionalCastPayments,
    playState.additionalCastPaymentDetails,
    playState.additionalCastCostErrors,
    playState.hasAdditionalCastCostErrors,
    playState.setAdditionalCastPayments,
    playState.setAdditionalCastPaymentDetails,
    playState.alternativeCostOptions,
    playState.selectedAlternativeCostTag,
    playState.alternativeExtraCostEntries,
    playState.alternativeExtraPayments,
    playState.alternativeExtraPaymentDetails,
    playState.alternativeExtraCostErrors,
    playState.hasAlternativeExtraCostErrors,
    playState.setSelectedAlternativeCostTag,
    playState.setAlternativeExtraPayments,
    playState.setAlternativeExtraPaymentDetails,
    playState.optionalCostOptions,
    playState.optionalCostSelections,
    playState.optionalCostEntries,
    playState.optionalCostPayments,
    playState.optionalCostPaymentDetails,
    playState.optionalCostErrors,
    playState.optionalCostPaymentErrors,
    playState.hasOptionalCostErrors,
    playState.handleToggleOptionalCost,
    playState.handleUpdateOptionalCostCount,
    playState.setOptionalCostPayments,
    playState.setOptionalCostPaymentDetails,
    playState.conspireSelected,
    playState.conspireOptions,
    playState.conspireTaps,
    playState.conspireError,
    playState.handleToggleConspireTap,
    playState.spliceOptions,
    playState.spliceSelections,
    playState.spliceCosts,
    playState.splicePayments,
    playState.splicePaymentDetails,
    playState.spliceCostErrors,
    playState.handleToggleSpliceCard,
    playState.setSplicePayments,
    playState.setSplicePaymentDetails,
  ]);

  // Derive SetupContext-compatible value
  const setupValue = useMemo<SetupContextValue>(() => ({
    deckList: playState.deckList,
    selectedDeckIds: playState.selectedDeckIds,
    setupLoading: playState.setupLoading,
    canStart: playState.canStart,
    handleSelectDeck: playState.handleSelectDeck,
    startGame: playState.startGame,
  }), [
    playState.deckList,
    playState.selectedDeckIds,
    playState.setupLoading,
    playState.canStart,
    playState.handleSelectDeck,
    playState.startGame,
  ]);

  return (
    <PlayGameContext.Provider value={gameValue}>
      <PlayCombatContext.Provider value={combatValue}>
        <PlayChoicesContext.Provider value={choicesValue}>
          <PlaySelectionContext.Provider value={selectionValue}>
            <PlayTurnContext.Provider value={turnValue}>
              <PlayTargetingContext.Provider value={targetingValue}>
                <PlayCastingContext.Provider value={castingValue}>
                  <PlaySetupContext.Provider value={setupValue}>
                    {children}
                  </PlaySetupContext.Provider>
                </PlayCastingContext.Provider>
              </PlayTargetingContext.Provider>
            </PlayTurnContext.Provider>
          </PlaySelectionContext.Provider>
        </PlayChoicesContext.Provider>
      </PlayCombatContext.Provider>
    </PlayGameContext.Provider>
  );
}
