'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';

// Feature hooks
import { useEffectGraphs } from '@/features/game/hooks/useEffectGraphs';
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

// Cost derivation utilities
import {
  deriveAdditionalCostsFromGraph,
  deriveAlternativeCastCostsFromGraph,
  deriveAlternativeExtraCostsFromGraph,
  deriveOptionalCastCostsFromGraph,
} from '@/lib/graphCosts';
import {
  buildEnterChoiceConfig,
  buildEnterChoiceDefaults,
  buildEnterChoiceErrors,
  buildEnterChoiceTargetOptions,
} from '@/lib/enterChoices';

// Local hooks
import { useGameSessionPersistence } from './useGameSessionPersistence';
import { useCombatValidation } from './useCombatValidation';
import { useCombatDamageState } from './useCombatDamageState';
import { useDefenderOptions } from './useDefenderOptions';
import { useReplacementState } from './useReplacementState';
import { useModalChoicesState } from './useModalChoicesState';
import { useOptionalCostsState } from './useOptionalCostsState';
import { useCopySpellState } from './useCopySpellState';
import { useCopyTargetValidation } from './useCopyTargetValidation';
import { useTargetSelectionErrors } from './useTargetSelectionErrors';

/**
 * Main play state hook that composes all focused state hooks.
 * Each domain is handled by a dedicated hook for maintainability.
 */
export function usePlayState() {
  // Core game state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);

  // Selection state
  const [selectedHandId, setSelectedHandId] = useState<string | null>(null);
  const [selectedCommandId, setSelectedCommandId] = useState<string | null>(null);
  const [selectedBattlefieldId, setSelectedBattlefieldId] = useState<string | null>(null);
  const [selectedStackIndex, setSelectedStackIndex] = useState<number | null>(null);
  const [autoPayWard, setAutoPayWard] = useState(true);
  const [selectedAlternativeCostTag, setSelectedAlternativeCostTag] = useState<string | null>(null);
  const [enterChoices, setEnterChoices] = useState<Record<string, string>>({});
  
  // Pending search choices from stack resolution
  const [pendingSearchChoices, setPendingSearchChoices] = useState<import('@/features/game/hooks/useEngineActions').PendingSearchChoice[]>([]);

  // Game session persistence
  useGameSessionPersistence({
    gameId,
    gameState,
    setGameId,
    setGameState,
    setCardMap,
    setPriorityPlayer,
    setError,
  });

  // Ability graphs
  const { effectGraphs, loadEffectGraphForObject } = useEffectGraphs({
    gameState,
    cardMap,
    setGameState,
  });

  // Game setup (deck selection)
  const { deckList, selectedDeckIds, loading: setupLoading, canStart, handleSelectDeck, startGame } = useGameSetup({
    setGameState,
    setCardMap,
    setPriorityPlayer,
    setGameId,
    setError,
  });

  // Combat selection
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

  // Object map
  const objectMap = useMemo(
    () => new Map(gameState?.objects.map((obj) => [obj.id, obj]) ?? []),
    [gameState?.objects]
  );

  // Replacement conflicts
  const replacementConflicts = useReplacementConflicts(gameState);
  const {
    replacementChoices,
    setReplacementChoices,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
  } = useReplacementState({ replacementConflicts });

  // Combat damage state
  const {
    combatDamageAssignments,
    setCombatDamageAssignments,
    hasFirstStrikeCombat,
    combatDamagePass,
    hasManualCombatChoices,
  } = useCombatDamageState({ gameState });

  // Engine actions
  const { runEngineAction } = useEngineActions({
    gameState,
    gameId,
    replacementChoices,
    setGameState,
    setPriorityPlayer,
    setLoading,
    setError,
    setPendingSearchChoices,
  });

  // Turn state
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

  // Blocker validation
  const { blockerErrors, blockerErrorMap } = useCombatValidation({
    gameState,
    combatState,
    isDeclareBlockers,
    selectedBlockers,
    cardMap,
  });

  // Defender options
  const defenderOptions = useDefenderOptions({
    gameState,
    activePlayerIndex,
    cardMap,
  });

  // Selected objects
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
  const selectedHandObject = gameState?.objects.find((obj) => obj.id === selectedHandId);
  const hasActivatedAbility = selectedBattlefieldObject?.effect_graphs && selectedBattlefieldObject.effect_graphs.length > 0;

  // Graphs
  const selectedGraph = selectedHandId ? effectGraphs[cardMap[selectedHandId]?.card_id ?? ''] : undefined;
  const selectedStackGraph = selectedStackIndex !== null 
    ? (gameState?.stack?.[selectedStackIndex]?.payload as any)?.graph 
    : undefined;
  const activeGraph = selectedStackGraph ?? selectedGraph;

  // Optional costs
  const optionalCostOptions = useMemo(
    () => deriveOptionalCastCostsFromGraph(selectedGraph),
    [selectedGraph]
  );

  const {
    optionalCostSelections,
    setOptionalCostSelections,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    optionalCostCosts,
    optionalCopyCount,
    conspireSelected,
    conspireOptions,
    conspireTaps,
    setConspireTaps,
    conspireError,
    handleToggleConspireTap,
    isArcaneSpell,
    spliceOptions,
    spliceSelections,
    setSpliceSelections,
    spliceCostList,
    handleToggleSpliceCard,
    entwineSelected,
  } = useOptionalCostsState({
    gameState,
    selectedHandId,
    selectedHandObject,
    currentPriority,
    optionalCostOptions,
    objectMap,
    cardMap,
    effectGraphs,
    loadEffectGraphForObject,
  });

  // Modal choices
  const {
    modalChoiceConfig,
    selectedModalModes,
    setSelectedModalModes,
    modalChoiceErrors,
    modalChoicesForCast,
    handleToggleModalMode,
  } = useModalChoicesState({
    activeGraph,
    selectedGraph,
    selectedHandId,
    entwineSelected,
  });

  // Copy spell state
  const {
    copySpellConfig,
    copyTargetSelections,
    setCopyTargetSelections,
    copyTargetsEnabled,
    copyTargetsCount,
  } = useCopySpellState({
    selectedGraph,
    optionalCopyCount,
  });

  // Targeting
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

  // Effect targeting
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

  // Search choices
  const {
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
    hasPendingSearchChoices,
  } = useSearchChoices({
    gameState,
    selectedGraph: activeGraph,
    currentPriority,
    context: (() => {
      const stackContext = selectedStackIndex !== null
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
    pendingSearchChoices,
    // For stack items, don't show graph-based search UI - only show when engine returns pendingSearchChoices
    isStackItem: selectedStackIndex !== null,
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

  // Copy effect targeting
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

  // Copy target validation
  const copyTargetErrorsGlobal = useCopyTargetValidation({
    gameState,
    copySpellConfig,
    hasEffectTargets,
    copyTargetSelections,
    targetHints,
    currentPriority,
    selectedHandId,
    requiredTargetsGlobal,
    distinctTargetsGlobal,
    minTargetsGlobal,
  });

  // Target selection errors
  const targetSelectionErrors = useTargetSelectionErrors({
    hasEffectTargets,
    effectTargetGroups,
    globalTargetErrors,
    searchErrors,
    copyTargetErrors,
    copyTargetErrorsGlobal,
    minTargetsGlobal,
    resolvedTargetObjectIds,
    resolvedTargetPlayerIds,
  });

  // Turn reset
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

  // Defender ID derivation
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

  // Stack index management
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

  // Turn step changes
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

  // Mana pool
  const priorityPlayerState = gameState?.players.find((player) => player.id === currentPriority);
  const manaPool = priorityPlayerState?.mana_pool ?? {};

  // Ward payments
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

  // Enter choices
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

  // Selection cleanup on resolve
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
  }, [clearEffectTargets]);

  useResolveCleanup({
    gameState,
    selectedHandId,
    onResolve: clearSelectionsOnResolve,
    onClearSelectedHand: setSelectedHandId,
  });

  // Activation costs
  const activatedCosts = useMemo(() => {
    if (!selectedBattlefieldObject?.effect_graphs?.length) return [];
    const graph = selectedBattlefieldObject.effect_graphs[0];
    const steps = graph?.steps ?? [];
    const activatedStep = steps.find((step: any) => step?.effect?.initiation === 'activated');
    const items = activatedStep?.effect?.cost?.items ?? [];
    return Array.isArray(items) ? items : [];
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

  // Additional costs
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

  // Alternative costs
  const alternativeCostOptions = useMemo(
    () => deriveAlternativeCastCostsFromGraph(selectedGraph),
    [selectedGraph]
  );

  const alternativeExtraCostOptions = useMemo(
    () => deriveAlternativeExtraCostsFromGraph(selectedGraph, selectedAlternativeCostTag),
    [selectedGraph, selectedAlternativeCostTag]
  );

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

  // Optional cost payments
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

  // Splice cost payments
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

  const optionalCostErrors = useMemo(() => optionalCostPaymentErrors, [optionalCostPaymentErrors]);

  // Enter choice defaults
  useEffect(() => {
    if (enterChoiceConfig.length === 0) {
      setEnterChoices({});
      return;
    }
    setEnterChoices((prev) => buildEnterChoiceDefaults(enterChoiceConfig, prev));
  }, [selectedHandId, enterChoiceConfig]);

  // Reset alternative cost on hand change
  useEffect(() => {
    setSelectedAlternativeCostTag(null);
  }, [selectedHandId]);

  // Cast context
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

  // Casting
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
    effectGraphs,
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
    // Core state
    loading,
    error,
    gameState,
    cardMap,
    priorityPlayer,
    setPriorityPlayer,
    // Selection
    selectedHandId,
    setSelectedHandId,
    selectedCommandId,
    setSelectedCommandId,
    selectedBattlefieldId,
    setSelectedBattlefieldId,
    selectedStackIndex,
    setSelectedStackIndex,
    selectedBattlefieldObject,
    hasActivatedAbility,
    selectedHandObject,
    // Setup
    deckList,
    selectedDeckIds,
    setupLoading,
    canStart,
    handleSelectDeck,
    startGame,
    // Effect graphs
    effectGraphs,
    loadEffectGraphForObject,
    selectedGraph,
    // Combat
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
    combatDamageAssignments,
    setCombatDamageAssignments,
    hasFirstStrikeCombat,
    combatDamagePass,
    hasManualCombatChoices,
    blockerErrors,
    blockerErrorMap,
    defenderOptions,
    defendingPlayerId,
    defendingObjectId,
    combatState,
    // Turn state
    currentPriority,
    activePlayerIndex,
    isMainPhase,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    isPriorityActivePlayer,
    isPriorityDefender,
    objectMap,
    // Replacements
    replacementChoices,
    setReplacementChoices,
    replacementConflicts,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    // Modal choices
    modalChoiceConfig,
    selectedModalModes,
    setSelectedModalModes,
    modalChoiceErrors,
    modalChoicesForCast,
    entwineSelected,
    handleToggleModalMode,
    // Enter choices
    enterChoices,
    setEnterChoices,
    enterChoiceConfig,
    enterChoiceTargetOptions,
    enterChoiceErrors,
    // Ward
    autoPayWard,
    setAutoPayWard,
    wardTargets,
    wardPayments,
    setWardPayments,
    wardPaymentDetails,
    setWardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
    hasWardPaymentErrors,
    // Targeting
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
    hasEffectTargets,
    mergedTargetsByEffect,
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
    hasPendingSearchChoices,
    resolvedTargetObjectIds,
    resolvedTargetPlayerIds,
    targetSelectionErrors,
    // Copy spell
    copySpellConfig,
    copyTargetSelections,
    setCopyTargetSelections,
    copyTargetErrorsGlobal,
    copyTargetsByEffectCount,
    copyEffectTargetGroups,
    copyTargetsByEffectList,
    copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList,
    copyTargetErrors,
    copyTargetsEnabled,
    copyTargetsCount,
    // Costs
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
    selectedAlternativeCostTag,
    setSelectedAlternativeCostTag,
    alternativeExtraCostOptions,
    alternativeExtraCostEntries,
    alternativeExtraPayments,
    setAlternativeExtraPayments,
    alternativeExtraPaymentDetails,
    setAlternativeExtraPaymentDetails,
    alternativeExtraCostErrors,
    alternativeExtraPaymentsPayload,
    hasAlternativeExtraCostErrors,
    // Optional costs
    optionalCostOptions,
    optionalCostSelections,
    setOptionalCostSelections,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    optionalCostCosts,
    optionalCopyCount,
    optionalCostEntries,
    optionalCostPayments,
    setOptionalCostPayments,
    optionalCostPaymentDetails,
    setOptionalCostPaymentDetails,
    optionalCostPaymentErrors,
    optionalCostPaymentsPayload,
    hasOptionalCostErrors,
    optionalCostErrors,
    // Conspire
    conspireSelected,
    conspireOptions,
    conspireTaps,
    setConspireTaps,
    conspireError,
    handleToggleConspireTap,
    // Splice
    isArcaneSpell,
    spliceOptions,
    spliceSelections,
    setSpliceSelections,
    spliceCostList,
    handleToggleSpliceCard,
    spliceCosts,
    splicePayments,
    setSplicePayments,
    splicePaymentDetails,
    setSplicePaymentDetails,
    spliceCostErrors,
    splicePaymentsPayload,
    // Casting
    manaPool,
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
    // Engine
    runEngineAction,
  };
}
