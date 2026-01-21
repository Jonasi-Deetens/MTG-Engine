'use client';

import { createContext, useContext, useMemo } from 'react';
import { usePlayState } from './hooks';
import type {
  GameContextValue,
  SetupContextValue,
  SelectionContextValue,
  TurnContextValue,
  CastingContextValue,
  PlayCombatContextValue,
  PlayChoicesContextValue,
  PlayTargetingContextValue,
} from './hooks';

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
// Consumer Hooks
// ============================================================================

export function usePlayGame(): GameContextValue {
  const context = useContext(PlayGameContext);
  if (!context) throw new Error('usePlayGame must be used within PlayProviders');
  return context;
}

export function usePlayCombat(): PlayCombatContextValue {
  const context = useContext(PlayCombatContext);
  if (!context) throw new Error('usePlayCombat must be used within PlayProviders');
  return context;
}

export function usePlayChoices(): PlayChoicesContextValue {
  const context = useContext(PlayChoicesContext);
  if (!context) throw new Error('usePlayChoices must be used within PlayProviders');
  return context;
}

export function usePlaySelection(): SelectionContextValue {
  const context = useContext(PlaySelectionContext);
  if (!context) throw new Error('usePlaySelection must be used within PlayProviders');
  return context;
}

export function usePlayTurn(): TurnContextValue {
  const context = useContext(PlayTurnContext);
  if (!context) throw new Error('usePlayTurn must be used within PlayProviders');
  return context;
}

export function usePlayTargeting(): PlayTargetingContextValue {
  const context = useContext(PlayTargetingContext);
  if (!context) throw new Error('usePlayTargeting must be used within PlayProviders');
  return context;
}

export function usePlayCasting(): CastingContextValue {
  const context = useContext(PlayCastingContext);
  if (!context) throw new Error('usePlayCasting must be used within PlayProviders');
  return context;
}

export function usePlaySetup(): SetupContextValue {
  const context = useContext(PlaySetupContext);
  if (!context) throw new Error('usePlaySetup must be used within PlayProviders');
  return context;
}

// ============================================================================
// Provider Component
// ============================================================================

export function PlayProviders({ children }: { children: React.ReactNode }) {
  const state = usePlayState();

  const gameValue = useMemo<GameContextValue>(() => ({
    gameId: null,
    gameState: state.gameState,
    cardMap: state.cardMap,
    loading: state.loading,
    error: state.error,
    priorityPlayer: state.priorityPlayer,
    setGameId: () => {},
    setGameState: () => {},
    setCardMap: () => {},
    setPriorityPlayer: state.setPriorityPlayer,
    setLoading: () => {},
    setError: () => {},
    runEngineAction: state.runEngineAction as unknown as GameContextValue['runEngineAction'],
  }), [state.gameState, state.cardMap, state.loading, state.error, state.priorityPlayer, state.setPriorityPlayer, state.runEngineAction]);

  const setupValue = useMemo<SetupContextValue>(() => ({
    deckList: state.deckList,
    selectedDeckIds: state.selectedDeckIds,
    setupLoading: state.setupLoading,
    canStart: state.canStart,
    handleSelectDeck: state.handleSelectDeck,
    startGame: state.startGame,
  }), [state.deckList, state.selectedDeckIds, state.setupLoading, state.canStart, state.handleSelectDeck, state.startGame]);

  const selectionValue = useMemo<SelectionContextValue>(() => ({
    selectedHandId: state.selectedHandId,
    selectedCommandId: state.selectedCommandId,
    selectedBattlefieldId: state.selectedBattlefieldId,
    selectedStackIndex: state.selectedStackIndex,
    setSelectedHandId: state.setSelectedHandId,
    setSelectedCommandId: state.setSelectedCommandId,
    setSelectedBattlefieldId: state.setSelectedBattlefieldId,
    setSelectedStackIndex: state.setSelectedStackIndex,
    loadAbilityGraphForObject: state.loadAbilityGraphForObject,
    abilityGraphs: state.abilityGraphs,
    selectedGraph: state.selectedGraph,
  }), [
    state.selectedHandId, state.selectedCommandId, state.selectedBattlefieldId, state.selectedStackIndex,
    state.setSelectedHandId, state.setSelectedCommandId, state.setSelectedBattlefieldId, state.setSelectedStackIndex,
    state.loadAbilityGraphForObject, state.abilityGraphs, state.selectedGraph,
  ]);

  const turnValue = useMemo<TurnContextValue>(() => ({
    currentPriority: state.currentPriority,
    activePlayerIndex: state.activePlayerIndex,
    isMainPhase: state.isMainPhase,
    isDeclareAttackers: state.isDeclareAttackers,
    isDeclareBlockers: state.isDeclareBlockers,
    isCombatDamage: state.isCombatDamage,
    isPriorityActivePlayer: state.isPriorityActivePlayer,
    isPriorityDefender: state.isPriorityDefender,
    objectMap: state.objectMap,
  }), [
    state.currentPriority, state.activePlayerIndex, state.isMainPhase, state.isDeclareAttackers,
    state.isDeclareBlockers, state.isCombatDamage, state.isPriorityActivePlayer, state.isPriorityDefender, state.objectMap,
  ]);

  const combatValue = useMemo<PlayCombatContextValue>(() => ({
    selectedAttackers: state.selectedAttackers,
    selectedBlockers: state.selectedBlockers,
    selectedBlockerOrder: state.selectedBlockerOrder,
    activeAttackerId: state.activeAttackerId,
    selectedDefenderId: state.selectedDefenderId,
    combatDamageAssignments: state.combatDamageAssignments,
    combatState: state.combatState,
    defenderOptions: state.defenderOptions,
    defendingPlayerId: state.defendingPlayerId,
    defendingObjectId: state.defendingObjectId,
    hasFirstStrikeCombat: state.hasFirstStrikeCombat,
    combatDamagePass: state.combatDamagePass as 'first_strike' | 'regular' | null,
    hasManualCombatChoices: state.hasManualCombatChoices,
    blockerErrors: state.blockerErrors,
    blockerErrorMap: state.blockerErrorMap,
    activeBlockerOrder: state.activeBlockerOrder,
    blockersPayload: state.blockersPayload,
    setActiveAttackerId: state.setActiveAttackerId,
    setSelectedDefenderId: state.setSelectedDefenderId,
    toggleAttacker: state.toggleAttacker,
    toggleBlocker: state.toggleBlocker,
    setSelectedBlockerOrder: state.setSelectedBlockerOrder,
    setCombatDamageAssignments: state.setCombatDamageAssignments,
  }), [
    state.selectedAttackers, state.selectedBlockers, state.selectedBlockerOrder, state.activeAttackerId,
    state.selectedDefenderId, state.combatDamageAssignments, state.combatState, state.defenderOptions,
    state.defendingPlayerId, state.defendingObjectId, state.hasFirstStrikeCombat, state.combatDamagePass,
    state.hasManualCombatChoices, state.blockerErrors, state.blockerErrorMap, state.activeBlockerOrder,
    state.blockersPayload, state.setActiveAttackerId, state.setSelectedDefenderId, state.toggleAttacker,
    state.toggleBlocker, state.setSelectedBlockerOrder, state.setCombatDamageAssignments,
  ]);

  const choicesValue = useMemo<PlayChoicesContextValue>(() => ({
    modalChoiceConfig: state.modalChoiceConfig,
    selectedModalModes: state.selectedModalModes,
    modalChoiceErrors: state.modalChoiceErrors,
    modalChoicesForCast: state.modalChoicesForCast,
    entwineSelected: state.entwineSelected,
    handleToggleModalMode: state.handleToggleModalMode,
    setSelectedModalModes: state.setSelectedModalModes,
    enterChoiceConfig: state.enterChoiceConfig,
    enterChoices: state.enterChoices,
    enterChoiceErrors: state.enterChoiceErrors,
    enterChoiceTargetOptions: state.enterChoiceTargetOptions,
    setEnterChoices: state.setEnterChoices,
    onEnterChoiceChange: (type: string, value: string) => {
      state.setEnterChoices((prev: Record<string, string>) => ({ ...prev, [type]: value }));
    },
    replacementChoices: state.replacementChoices,
    replacementConflicts: state.replacementConflicts,
    hasUnresolvedDamageReplacements: state.hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements: state.unresolvedDamageReplacements,
    highlightedReplacementKey: state.highlightedReplacementKey,
    setReplacementChoices: state.setReplacementChoices,
    setHighlightedReplacementKey: state.setHighlightedReplacementKey,
    wardTargets: state.wardTargets,
    wardPayments: state.wardPayments,
    wardPaymentDetails: state.wardPaymentDetails,
    wardPaymentErrors: state.wardPaymentErrors,
    wardPaymentsPayload: state.wardPaymentsPayload ?? {},
    hasWardPaymentErrors: state.hasWardPaymentErrors,
    autoPayWard: state.autoPayWard,
    setWardPayments: state.setWardPayments,
    setWardPaymentDetails: state.setWardPaymentDetails,
    setAutoPayWard: state.setAutoPayWard,
  }), [
    state.modalChoiceConfig, state.selectedModalModes, state.modalChoiceErrors, state.modalChoicesForCast,
    state.entwineSelected, state.handleToggleModalMode, state.setSelectedModalModes, state.enterChoiceConfig,
    state.enterChoices, state.enterChoiceErrors, state.enterChoiceTargetOptions, state.setEnterChoices,
    state.replacementChoices, state.replacementConflicts, state.hasUnresolvedDamageReplacements,
    state.unresolvedDamageReplacements, state.highlightedReplacementKey, state.setReplacementChoices,
    state.setHighlightedReplacementKey, state.wardTargets, state.wardPayments, state.wardPaymentDetails,
    state.wardPaymentErrors, state.wardPaymentsPayload, state.hasWardPaymentErrors, state.autoPayWard,
    state.setWardPayments, state.setWardPaymentDetails, state.setAutoPayWard,
  ]);

  const targetingValue = useMemo<PlayTargetingContextValue>(() => ({
    targetHints: state.targetHints,
    selectedTargetObjectIds: state.selectedTargetObjectIds ?? [],
    selectedTargetPlayerIds: state.selectedTargetPlayerIds ?? [],
    objectTargetStatus: state.objectTargetStatus,
    playerTargetStatus: state.playerTargetStatus,
    stackTargetChecks: Object.values(state.stackTargetChecks ?? {}),
    stackSpellObjects: state.stackSpellObjects,
    filteredTargetableObjects: state.filteredTargetableObjects,
    filteredTargetPlayers: state.filteredTargetPlayers,
    shouldUseStackTargets: state.shouldUseStackTargets,
    requiredTargetsGlobal: state.requiredTargetsGlobal,
    distinctTargetsGlobal: state.distinctTargetsGlobal,
    minTargetsGlobal: state.minTargetsGlobal,
    effectTargetGroups: state.effectTargetGroups,
    targetsByEffect: state.targetsByEffect,
    requiredTargetsByEffect: state.requiredTargetsByEffect,
    distinctTargetsByEffect: state.distinctTargetsByEffect,
    minTargetsByEffect: state.minTargetsByEffect,
    globalTargetErrors: state.globalTargetErrors,
    effectTargetObjectIds: state.effectTargetObjectIds,
    effectTargetPlayerIds: state.effectTargetPlayerIds,
    hasEffectTargets: state.hasEffectTargets,
    mergedTargetsByEffect: state.mergedTargetsByEffect,
    searchEntries: state.searchEntries,
    searchTargetsByEffect: state.searchTargetsByEffect,
    searchErrors: state.searchErrors,
    copySpellConfig: state.copySpellConfig,
    copyTargetSelections: state.copyTargetSelections,
    copyTargetErrorsGlobal: state.copyTargetErrorsGlobal,
    copyTargetsByEffectCount: state.copyTargetsByEffectCount,
    copyEffectTargetGroups: state.copyEffectTargetGroups,
    copyTargetsByEffectList: state.copyTargetsByEffectList,
    copyRequiredTargetsByEffectList: state.copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList: state.copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList: state.copyMinTargetsByEffectList,
    copyTargetErrors: state.copyTargetErrors,
    resolvedTargetObjectIds: state.resolvedTargetObjectIds,
    resolvedTargetPlayerIds: state.resolvedTargetPlayerIds,
    targetSelectionErrors: state.targetSelectionErrors,
    setSelectedTargetObjectIds: state.setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds: state.setSelectedTargetPlayerIds,
    setCopyTargetSelections: state.setCopyTargetSelections,
    clearEffectTargets: state.clearEffectTargets,
  }), [
    state.targetHints, state.selectedTargetObjectIds, state.selectedTargetPlayerIds, state.objectTargetStatus,
    state.playerTargetStatus, state.stackTargetChecks, state.stackSpellObjects, state.filteredTargetableObjects,
    state.filteredTargetPlayers, state.shouldUseStackTargets, state.requiredTargetsGlobal, state.distinctTargetsGlobal,
    state.minTargetsGlobal, state.effectTargetGroups, state.targetsByEffect, state.requiredTargetsByEffect,
    state.distinctTargetsByEffect, state.minTargetsByEffect, state.globalTargetErrors, state.effectTargetObjectIds,
    state.effectTargetPlayerIds, state.hasEffectTargets, state.mergedTargetsByEffect, state.searchEntries,
    state.searchTargetsByEffect, state.searchErrors, state.copySpellConfig, state.copyTargetSelections,
    state.copyTargetErrorsGlobal, state.copyTargetsByEffectCount, state.copyEffectTargetGroups,
    state.copyTargetsByEffectList, state.copyRequiredTargetsByEffectList, state.copyDistinctTargetsByEffectList,
    state.copyMinTargetsByEffectList, state.copyTargetErrors, state.resolvedTargetObjectIds,
    state.resolvedTargetPlayerIds, state.targetSelectionErrors, state.setSelectedTargetObjectIds,
    state.setSelectedTargetPlayerIds, state.setCopyTargetSelections, state.clearEffectTargets,
  ]);

  const castingValue = useMemo<CastingContextValue>(() => ({
    preparedCast: state.preparedCast,
    manaPool: state.manaPool,
    manaPayment: state.manaPayment,
    manaPaymentDetail: state.manaPaymentDetail,
    manaPaymentStatus: state.manaPaymentStatus,
    costLabel: state.costLabel,
    autoPayMana: state.autoPayMana,
    isComplexCost: state.isComplexCost,
    handlePrepareCast: state.handlePrepareCast,
    handleFinalizeCast: state.handleFinalizeCast,
    setManaPayment: state.setManaPayment,
    setManaPaymentDetail: state.setManaPaymentDetail,
    setAutoPayMana: state.setAutoPayMana,
    buildCastContext: state.buildCastContext,
    activationCosts: state.activationCosts,
    activationPayments: state.activationPayments,
    activationPaymentDetails: state.activationPaymentDetails,
    activationCostErrors: state.activationCostErrors,
    hasActivationCostErrors: state.hasActivationCostErrors,
    activationCostPaymentsPayload: state.activationCostPaymentsPayload,
    setActivationPayments: state.setActivationPayments,
    setActivationPaymentDetails: state.setActivationPaymentDetails,
    additionalCastCosts: state.additionalCastCosts,
    additionalCastPayments: state.additionalCastPayments,
    additionalCastPaymentDetails: state.additionalCastPaymentDetails,
    additionalCastCostErrors: state.additionalCastCostErrors,
    hasAdditionalCastCostErrors: state.hasAdditionalCastCostErrors,
    setAdditionalCastPayments: state.setAdditionalCastPayments,
    setAdditionalCastPaymentDetails: state.setAdditionalCastPaymentDetails,
    alternativeCostOptions: state.alternativeCostOptions,
    selectedAlternativeCostTag: state.selectedAlternativeCostTag,
    alternativeExtraCostEntries: state.alternativeExtraCostEntries,
    alternativeExtraPayments: state.alternativeExtraPayments,
    alternativeExtraPaymentDetails: state.alternativeExtraPaymentDetails,
    alternativeExtraCostErrors: state.alternativeExtraCostErrors,
    hasAlternativeExtraCostErrors: state.hasAlternativeExtraCostErrors,
    setSelectedAlternativeCostTag: state.setSelectedAlternativeCostTag,
    setAlternativeExtraPayments: state.setAlternativeExtraPayments,
    setAlternativeExtraPaymentDetails: state.setAlternativeExtraPaymentDetails,
    optionalCostOptions: state.optionalCostOptions,
    optionalCostSelections: state.optionalCostSelections,
    optionalCostEntries: state.optionalCostEntries,
    optionalCostPayments: state.optionalCostPayments,
    optionalCostPaymentDetails: state.optionalCostPaymentDetails,
    optionalCostErrors: state.optionalCostErrors,
    optionalCostPaymentErrors: state.optionalCostPaymentErrors,
    hasOptionalCostErrors: state.hasOptionalCostErrors,
    handleToggleOptionalCost: state.handleToggleOptionalCost,
    handleUpdateOptionalCostCount: state.handleUpdateOptionalCostCount,
    setOptionalCostPayments: state.setOptionalCostPayments,
    setOptionalCostPaymentDetails: state.setOptionalCostPaymentDetails,
    conspireSelected: state.conspireSelected,
    conspireOptions: state.conspireOptions,
    conspireTaps: state.conspireTaps,
    conspireError: state.conspireError,
    handleToggleConspireTap: state.handleToggleConspireTap,
    spliceOptions: state.spliceOptions,
    spliceSelections: state.spliceSelections,
    spliceCosts: state.spliceCosts,
    splicePayments: state.splicePayments,
    splicePaymentDetails: state.splicePaymentDetails,
    spliceCostErrors: state.spliceCostErrors,
    handleToggleSpliceCard: state.handleToggleSpliceCard,
    setSplicePayments: state.setSplicePayments,
    setSplicePaymentDetails: state.setSplicePaymentDetails,
  }), [
    state.preparedCast, state.manaPool, state.manaPayment, state.manaPaymentDetail, state.manaPaymentStatus,
    state.costLabel, state.autoPayMana, state.isComplexCost, state.handlePrepareCast, state.handleFinalizeCast,
    state.setManaPayment, state.setManaPaymentDetail, state.setAutoPayMana, state.buildCastContext,
    state.activationCosts, state.activationPayments, state.activationPaymentDetails, state.activationCostErrors,
    state.hasActivationCostErrors, state.activationCostPaymentsPayload, state.setActivationPayments,
    state.setActivationPaymentDetails, state.additionalCastCosts, state.additionalCastPayments,
    state.additionalCastPaymentDetails, state.additionalCastCostErrors, state.hasAdditionalCastCostErrors,
    state.setAdditionalCastPayments, state.setAdditionalCastPaymentDetails, state.alternativeCostOptions,
    state.selectedAlternativeCostTag, state.alternativeExtraCostEntries, state.alternativeExtraPayments,
    state.alternativeExtraPaymentDetails, state.alternativeExtraCostErrors, state.hasAlternativeExtraCostErrors,
    state.setSelectedAlternativeCostTag, state.setAlternativeExtraPayments, state.setAlternativeExtraPaymentDetails,
    state.optionalCostOptions, state.optionalCostSelections, state.optionalCostEntries, state.optionalCostPayments,
    state.optionalCostPaymentDetails, state.optionalCostErrors, state.optionalCostPaymentErrors,
    state.hasOptionalCostErrors, state.handleToggleOptionalCost, state.handleUpdateOptionalCostCount,
    state.setOptionalCostPayments, state.setOptionalCostPaymentDetails, state.conspireSelected, state.conspireOptions,
    state.conspireTaps, state.conspireError, state.handleToggleConspireTap, state.spliceOptions, state.spliceSelections,
    state.spliceCosts, state.splicePayments, state.splicePaymentDetails, state.spliceCostErrors,
    state.handleToggleSpliceCard, state.setSplicePayments, state.setSplicePaymentDetails,
  ]);

  return (
    <PlayGameContext.Provider value={gameValue}>
      <PlaySetupContext.Provider value={setupValue}>
        <PlaySelectionContext.Provider value={selectionValue}>
          <PlayTurnContext.Provider value={turnValue}>
            <PlayCombatContext.Provider value={combatValue}>
              <PlayChoicesContext.Provider value={choicesValue}>
                <PlayTargetingContext.Provider value={targetingValue}>
                  <PlayCastingContext.Provider value={castingValue}>
                    {children}
                  </PlayCastingContext.Provider>
                </PlayTargetingContext.Provider>
              </PlayChoicesContext.Provider>
            </PlayCombatContext.Provider>
          </PlayTurnContext.Provider>
        </PlaySelectionContext.Provider>
      </PlaySetupContext.Provider>
    </PlayGameContext.Provider>
  );
}
