'use client';

import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, engineApi } from '@/lib/engine';
import { useAbilityGraphs } from '@/hooks/useAbilityGraphs';
import { useTargeting } from '@/hooks/useTargeting';
import { useEffectTargeting } from '@/hooks/useEffectTargeting';
import { useCopyEffectTargeting } from '@/hooks/useCopyEffectTargeting';
import { useSearchChoices } from '@/hooks/useSearchChoices';
import { useCasting } from '@/hooks/useCasting';
import { useCombatSelection } from '@/hooks/useCombatSelection';
import { useEngineActions } from '@/hooks/useEngineActions';
import { useGameSetup } from '@/hooks/useGameSetup';
import { useTurnReset } from '@/hooks/useTurnReset';
import { useReplacementConflicts } from '@/hooks/useReplacementConflicts';
import { useCastContext } from '@/hooks/useCastContext';
import { useTurnState } from '@/hooks/useTurnState';
import { useWardPayments } from '@/hooks/useWardPayments';
import { useActivationCosts } from '@/hooks/useActivationCosts';
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

const PlayStateContext = createContext<ReturnType<typeof usePlayStateInternal> | null>(null);

export function PlayStateProvider({ children }: { children: React.ReactNode }) {
  const value = usePlayStateInternal();
  return <PlayStateContext.Provider value={value}>{children}</PlayStateContext.Provider>;
}

export function usePlayState() {
  const context = useContext(PlayStateContext);
  if (!context) {
    throw new Error('usePlayState must be used within PlayStateProvider');
  }
  return context;
}

function usePlayStateInternal() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);
  const [selectedHandId, setSelectedHandId] = useState<string | null>(null);
  const [selectedBattlefieldId, setSelectedBattlefieldId] = useState<string | null>(null);
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});
  const [enterChoices, setEnterChoices] = useState<Record<string, string>>({});
  const [highlightedReplacementKey, setHighlightedReplacementKey] = useState<string | null>(null);
  const [combatDamageAssignments, setCombatDamageAssignments] = useState<Record<string, Record<string, number>>>({});
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
    setError,
  });

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
  const modalChoiceConfig = useMemo(() => deriveModalConfig(selectedGraph), [selectedGraph]);
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
    selectedGraph,
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
    selectedGraph,
    currentPriority,
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
    selectedGraph,
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
    return modalChoiceConfig.modes.map((mode) => mode.id);
  }, [entwineSelected, modalChoiceConfig, selectedModalModes]);
  useEffect(() => {
    if (!entwineSelected || !modalChoiceConfig) return;
    setSelectedModalModes(modalChoiceConfig.modes.map((mode) => mode.id));
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
