"use client";

import { useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, EngineActionRequest } from '@/lib/engine';
import { Card } from '@/components/ui/Card';
import { DeckSetupPanel } from '@/components/engine/DeckSetupPanel';
import { PlayerZone } from '@/components/engine/PlayerZone';
import { StackView } from '@/components/engine/StackView';
import { TurnStatusCard } from '@/components/engine/TurnStatusCard';
import { ActionsPanel } from '@/components/engine/ActionsPanel';
import { CombatDamagePanel } from '@/components/engine/CombatDamagePanel';
import { ReplacementChoicePanel } from '@/components/engine/ReplacementChoicePanel';
import { useAbilityGraphs } from '@/hooks/useAbilityGraphs';
import { useTargeting } from '@/hooks/useTargeting';
import { useEffectTargeting } from '@/hooks/useEffectTargeting';
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

export default function PlayPage() {
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
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    return gameState.turn.combat_state.attackers.some((attackerId) => {
      const attacker = objectMap.get(attackerId);
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
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const errors: string[] = [];
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;
    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = objectMap.get(attackerId);
      if (!attacker) return;
      if (attacker.keywords?.includes('Menace') && blockerSet.size === 1) {
        const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
        errors.push(`${attackerLabel} has menace and needs 2+ blockers.`);
      }
      blockerSet.forEach((blockerId) => {
        const blocker = objectMap.get(blockerId);
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
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const map: Record<string, string[]> = {};
    const usedBlockers = new Set<string>();
    const defendingId = combatState.defending_player_id;
    Object.entries(selectedBlockers).forEach(([attackerId, blockerSet]) => {
      const attacker = objectMap.get(attackerId);
      if (!attacker) return;
      blockerSet.forEach((blockerId) => {
        const blocker = objectMap.get(blockerId);
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
  const hasEffectTargets = effectTargetGroups.length > 0;
  const resolvedTargetObjectIds = hasEffectTargets ? effectTargetObjectIds : selectedTargetObjectIds;
  const resolvedTargetPlayerIds = hasEffectTargets ? effectTargetPlayerIds : selectedTargetPlayerIds;
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
      });
      if (globalTargetErrors.length > 0) {
        errors.push(...globalTargetErrors);
      }
      return errors;
    }
    const min = minTargetsGlobal?.target ?? 0;
    const count = resolvedTargetObjectIds.length + resolvedTargetPlayerIds.length;
    if (min > 0 && count < min) {
      return [`Select at least ${min} target${min === 1 ? '' : 's'}.`];
    }
    return [];
  }, [
    effectTargetGroups,
    globalTargetErrors,
    hasEffectTargets,
    minTargetsGlobal,
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
  const objectMap = useMemo(
    () => new Map((gameState?.objects ?? []).map((obj) => [obj.id, obj])),
    [gameState]
  );
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
  const alternativeExtraCosts = useMemo(
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
    costEntries: alternativeExtraCosts,
    payments: alternativeExtraPayments,
    setPayments: setAlternativeExtraPayments,
    paymentDetails: alternativeExtraPaymentDetails,
    setPaymentDetails: setAlternativeExtraPaymentDetails,
    paymentErrors: alternativeExtraCostErrors,
    paymentsPayload: alternativeExtraPaymentsPayload,
  } = useActivationCosts({
    costs: alternativeExtraCosts,
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
  const hasOptionalCostErrors =
    optionalCostPaymentErrors.length > 0 ||
    spliceCostErrors.length > 0 ||
    (conspireSelected && conspireTaps.length !== 2);
  const optionalCostErrors = useMemo(
    () => optionalCostPaymentErrors,
    [optionalCostPaymentErrors]
  );
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
    targetsByEffect: hasEffectTargets ? targetsByEffect : undefined,
    requiredTargetsByEffect: hasEffectTargets ? requiredTargetsByEffect : undefined,
    requiredTargetsGlobal: !hasEffectTargets ? requiredTargetsGlobal : undefined,
    distinctTargetsByEffect: hasEffectTargets ? distinctTargetsByEffect : undefined,
    distinctTargetsGlobal: !hasEffectTargets ? distinctTargetsGlobal : undefined,
    minTargetsByEffect: hasEffectTargets ? minTargetsByEffect : undefined,
    minTargetsGlobal: !hasEffectTargets ? minTargetsGlobal : undefined,
    copyChooseNewTargets: copyTargetsEnabled,
    copyTargetsList: copyTargetSelections.map((entry) => ({
      ...(entry.objectIds.length > 0 ? { target: entry.objectIds[0], targets: entry.objectIds } : {}),
      ...(entry.playerIds.length > 0 ? { target_player: entry.playerIds[0], target_players: entry.playerIds } : {}),
    })),
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
        <DeckSetupPanel
          deckList={deckList}
          selectedDeckIds={selectedDeckIds}
          loading={setupLoading}
          canStart={canStart}
          onSelectDeck={handleSelectDeck}
          onStart={startGame}
        />
      )}

      {gameState && (
        <div className="space-y-6">
          <TurnStatusCard
            turnNumber={gameState.turn.turn_number}
            phase={gameState.turn.phase}
            step={gameState.turn.step}
            activePlayerIndex={gameState.turn.active_player_index}
            currentPriority={currentPriority}
            loading={loading}
            onPassPriority={() => runEngineAction('pass_priority', { player_id: currentPriority })}
            onAdvanceStep={() => runEngineAction('advance_turn')}
          />

          <ActionsPanel
            loading={loading}
            selectedHandId={selectedHandId}
            selectedBattlefieldId={selectedBattlefieldId}
            preparedCast={preparedCast}
            enterChoiceErrors={enterChoiceErrors}
            manaPaymentErrors={manaPaymentStatus.errors}
            hasWardPaymentErrors={hasWardPaymentErrors}
            hasActivationCostErrors={hasActivationCostErrors}
            hasAdditionalCastCostErrors={hasAdditionalCastCostErrors}
            hasAlternativeExtraCostErrors={hasAlternativeExtraCostErrors}
            hasOptionalCastCostErrors={hasOptionalCostErrors}
            hasAlternativeExtraCostErrors={hasAlternativeExtraCostErrors}
            isMainPhase={isMainPhase}
            isPriorityActivePlayer={isPriorityActivePlayer}
            isDeclareAttackers={isDeclareAttackers}
            isDeclareBlockers={isDeclareBlockers}
            isCombatDamage={isCombatDamage}
            isPriorityDefender={isPriorityDefender}
            hasActivatedAbility={!!hasActivatedAbility}
            selectedAttackers={selectedAttackers}
            activeAttackerId={activeAttackerId}
            activeBlockerOrder={activeBlockerOrder}
            selectedDefenderId={selectedDefenderId}
            defenderOptions={defenderOptions}
            combatState={combatState}
            cardMap={cardMap}
            onPlayLand={() =>
              runEngineAction('play_land', { player_id: currentPriority, object_id: selectedHandId ?? undefined })
            }
            onPrepareCast={handlePrepareCast}
            onFinalizeCast={handleFinalizeCast}
            onTapForMana={() =>
              runEngineAction('activate_mana_ability', {
                player_id: currentPriority,
                object_id: selectedBattlefieldId ?? undefined,
              })
            }
            onActivateAbility={() =>
              runEngineAction('activate_ability', {
                player_id: currentPriority,
                object_id: selectedBattlefieldId ?? undefined,
                ability_index: 0,
                context: buildCastContext(selectedBattlefieldId ?? undefined, {
                  wardAutoPay: autoPayWard,
                  wardPayments: wardPaymentsPayload,
                  costPayments: activationCostPaymentsPayload,
                }),
              })
            }
            onDeclareAttackers={() => {
              const payload: any = {
                player_id: currentPriority,
                attackers: Array.from(selectedAttackers),
              };
              if (selectedDefenderId?.startsWith('player:')) {
                const raw = selectedDefenderId.split(':')[1];
                payload.defending_player_id = raw ? Number(raw) : undefined;
              } else if (selectedDefenderId?.startsWith('planeswalker:')) {
                const objId = selectedDefenderId.split(':')[1];
                payload.defending_object_id = objId || undefined;
                const obj = objId ? objectMap.get(objId) : undefined;
                if (obj) {
                  payload.defending_player_id = obj.controller_id;
                }
              }
              runEngineAction('declare_attackers', payload);
            }}
            onDeclareBlockers={() =>
              runEngineAction('declare_blockers', {
                player_id: currentPriority,
                blockers: blockersPayload,
              })
            }
            onAssignCombatDamage={() =>
              runEngineAction('assign_combat_damage', {
                player_id: currentPriority,
                ...(hasManualCombatChoices ? { damage_assignments: combatDamageAssignments } : {}),
                ...(combatDamagePass ? { combat_damage_pass: combatDamagePass } : {}),
              })
            }
            hasUnresolvedDamageReplacements={hasUnresolvedDamageReplacements}
            unresolvedDamageReplacements={unresolvedDamageReplacements}
            blockerErrors={blockerErrors}
            blockerErrorMap={blockerErrorMap}
            onSelectDefender={(value) => setSelectedDefenderId(value)}
            onSelectActiveAttacker={setActiveAttackerId}
            onReorderBlockerUp={(index) =>
              setSelectedBlockerOrder((prev) => {
                if (!activeAttackerId) return prev;
                const order = prev[activeAttackerId] ?? [];
                if (index <= 0) return prev;
                const next = [...order];
                [next[index - 1], next[index]] = [next[index], next[index - 1]];
                return { ...prev, [activeAttackerId]: next };
              })
            }
            onReorderBlockerDown={(index) =>
              setSelectedBlockerOrder((prev) => {
                if (!activeAttackerId) return prev;
                const order = prev[activeAttackerId] ?? [];
                if (index >= order.length - 1) return prev;
                const next = [...order];
                [next[index], next[index + 1]] = [next[index + 1], next[index]];
                return { ...prev, [activeAttackerId]: next };
              })
            }
            enterChoiceConfig={enterChoiceConfig}
            enterChoices={enterChoices}
            enterChoiceTargetOptions={enterChoiceTargetOptions}
            onEnterChoiceChange={(choiceType, value) =>
              setEnterChoices((prev) => ({ ...prev, [choiceType]: value }))
            }
            modalChoiceConfig={modalChoiceConfig}
            selectedModalModes={selectedModalModes}
            modalChoiceErrors={modalChoiceErrors}
            onToggleModalMode={handleToggleModalMode}
            modalChoiceDisabled={entwineSelected}
            isComplexCost={isComplexCost}
            manaPool={manaPool}
            manaPayment={manaPayment}
            manaPaymentDetail={manaPaymentDetail}
            costLabel={costLabel}
            autoPayMana={autoPayMana}
            onToggleAutoPay={setAutoPayMana}
            onUpdatePaymentDetail={setManaPaymentDetail}
            onUpdateManaPayment={setManaPayment}
            activationCosts={activationCosts}
            activationPayments={activationPayments}
            activationPaymentDetails={activationPaymentDetails}
            activationCostErrors={activationCostErrors}
            onUpdateActivationPayment={(index, updater) =>
              setActivationPayments((prev) => {
                const next = [...prev];
                next[index] = updater(next[index] ?? {});
                return next;
              })
            }
            onUpdateActivationPaymentDetail={(index, updater) =>
              setActivationPaymentDetails((prev) => ({
                ...prev,
                [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
              }))
            }
            additionalCastCosts={additionalCastCosts}
            additionalCastPayments={additionalCastPayments}
            additionalCastPaymentDetails={additionalCastPaymentDetails}
            additionalCastCostErrors={additionalCastCostErrors}
            onUpdateAdditionalCastPayment={(index, updater) =>
              setAdditionalCastPayments((prev) => {
                const next = [...prev];
                next[index] = updater(next[index] ?? {});
                return next;
              })
            }
            onUpdateAdditionalCastPaymentDetail={(index, updater) =>
              setAdditionalCastPaymentDetails((prev) => ({
                ...prev,
                [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
              }))
            }
            alternativeExtraCosts={alternativeExtraCosts}
            alternativeExtraPayments={alternativeExtraPayments}
            alternativeExtraPaymentDetails={alternativeExtraPaymentDetails}
            alternativeExtraCostErrors={alternativeExtraCostErrors}
            onUpdateAlternativeExtraPayment={(index, updater) =>
              setAlternativeExtraPayments((prev) => {
                const next = [...prev];
                next[index] = updater(next[index] ?? {});
                return next;
              })
            }
            onUpdateAlternativeExtraPaymentDetail={(index, updater) =>
              setAlternativeExtraPaymentDetails((prev) => ({
                ...prev,
                [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
              }))
            }
            alternativeCostOptions={alternativeCostOptions}
            selectedAlternativeCostTag={selectedAlternativeCostTag}
            onSelectAlternativeCost={setSelectedAlternativeCostTag}
            optionalCostOptions={optionalCostOptions}
            optionalCostSelections={optionalCostSelections}
            optionalCostErrors={optionalCostErrors}
            onToggleOptionalCost={handleToggleOptionalCost}
            onUpdateOptionalCostCount={handleUpdateOptionalCostCount}
            optionalCostEntries={optionalCostEntries}
            optionalCostPayments={optionalCostPayments}
            optionalCostPaymentDetails={optionalCostPaymentDetails}
            optionalCostPaymentErrors={optionalCostPaymentErrors}
            onUpdateOptionalCostPayment={(index, updater) =>
              setOptionalCostPayments((prev) => {
                const next = [...prev];
                next[index] = updater(next[index] ?? {});
                return next;
              })
            }
            onUpdateOptionalCostPaymentDetail={(index, updater) =>
              setOptionalCostPaymentDetails((prev) => ({
                ...prev,
                [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
              }))
            }
            conspireEnabled={conspireSelected}
            conspireOptions={conspireOptions}
            conspireSelections={conspireTaps}
            conspireError={conspireError}
            onToggleConspire={handleToggleConspireTap}
            spliceOptions={spliceOptions}
            spliceSelections={spliceSelections}
            onToggleSpliceCard={handleToggleSpliceCard}
            spliceCosts={spliceCosts}
            splicePayments={splicePayments}
            splicePaymentDetails={splicePaymentDetails}
            spliceCostErrors={spliceCostErrors}
            onUpdateSplicePayment={(index, updater) =>
              setSplicePayments((prev) => {
                const next = [...prev];
                next[index] = updater(next[index] ?? {});
                return next;
              })
            }
            onUpdateSplicePaymentDetail={(index, updater) =>
              setSplicePaymentDetails((prev) => ({
                ...prev,
                [index]: updater(prev[index] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }),
              }))
            }
            autoPayWard={autoPayWard}
            onToggleAutoPayWard={setAutoPayWard}
            wardTargets={wardTargets}
            wardPayments={wardPayments}
            wardPaymentDetails={wardPaymentDetails}
            wardPaymentErrors={wardPaymentErrors}
            onUpdateWardPayment={(objectId, index, updater) =>
              setWardPayments((prev) => ({
                ...prev,
                [objectId]: (() => {
                  const next = [...(prev[objectId] ?? [])];
                  next[index] = updater(next[index] ?? {});
                  return next;
                })(),
              }))
            }
            onUpdateWardPaymentDetail={(objectId, updater) =>
              setWardPaymentDetails((prev) => ({
                ...prev,
                [objectId]: updater(
                  prev[objectId] ?? { hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] }
                ),
              }))
            }
            targetObjects={shouldUseStackTargets ? stackSpellObjects : filteredTargetableObjects}
            targetPlayers={shouldUseStackTargets ? [] : filteredTargetPlayers}
            selectedTargetObjectIds={resolvedTargetObjectIds}
            selectedTargetPlayerIds={resolvedTargetPlayerIds}
            objectLabel={shouldUseStackTargets ? 'Spells on Stack' : 'Objects'}
            maxObjectTargets={targetHints.maxObjectTargets ?? undefined}
            maxPlayerTargets={targetHints.maxPlayerTargets ?? undefined}
            objectTargetStatus={objectTargetStatus}
            playerTargetStatus={playerTargetStatus}
            onChangeTargetObjects={setSelectedTargetObjectIds}
            onChangeTargetPlayers={setSelectedTargetPlayerIds}
            onClearTargets={() => {
              setSelectedTargetObjectIds([]);
              setSelectedTargetPlayerIds([]);
            }}
            effectTargetGroups={hasEffectTargets ? effectTargetGroups : undefined}
            targetSelectionErrors={targetSelectionErrors}
            copyTargetSelections={copyTargetsEnabled ? copyTargetSelections : undefined}
            onChangeCopyTarget={(index, objectIds, playerIds) =>
              setCopyTargetSelections((prev) => {
                const next = [...prev];
                next[index] = { objectIds, playerIds };
                return next;
              })
            }
          />

          <CombatDamagePanel
            active={isCombatDamage}
            combatState={combatState}
            objects={gameState.objects}
            cardMap={cardMap}
            defendingPlayerId={defendingPlayerId ?? null}
            defendingObjectId={defendingObjectId}
            assignments={combatDamageAssignments}
            damagePass={combatDamagePass}
            onUpdateAssignment={(attackerId, targetId, value) =>
              setCombatDamageAssignments((prev) => ({
                ...prev,
                [attackerId]: { ...(prev[attackerId] ?? {}), [targetId]: value },
              }))
            }
          />

          <ReplacementChoicePanel
            conflicts={replacementConflicts}
            replacementChoices={replacementChoices}
            highlightKey={highlightedReplacementKey}
            onNextHighlight={() => {
              if (unresolvedDamageReplacements.length === 0) return;
              const keys = unresolvedDamageReplacements.map((entry) => entry.key);
              const currentIndex = highlightedReplacementKey ? keys.indexOf(highlightedReplacementKey) : -1;
              const nextIndex = (currentIndex + 1) % keys.length;
              setHighlightedReplacementKey(keys[nextIndex]);
            }}
            onSelectChoice={(key, value) =>
              {
                setReplacementChoices((prev) => ({
                  ...prev,
                  [key]: value,
                }));
                const remaining = unresolvedDamageReplacements
                  .map((entry) => entry.key)
                  .filter((entryKey) => entryKey !== key);
                setHighlightedReplacementKey(remaining[0] ?? null);
              }
            }
          />

          <StackView
            stack={gameState.stack}
            objects={gameState.objects}
            cardMap={cardMap}
            targetChecks={stackTargetChecks}
          />

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {gameState.players.map((player, index) => (
              <PlayerZone
                key={`player-zone-${player.id}`}
                player={player}
                objects={gameState.objects}
                cardMap={cardMap}
                isActive={gameState.turn.active_player_index === index}
                selectedHandId={player.id === currentPriority ? selectedHandId : null}
                onSelectHand={
                  player.id === currentPriority
                    ? (objectId) => {
                        setSelectedHandId(objectId);
                        loadAbilityGraphForObject(objectId);
                      }
                    : undefined
                }
                selectedBattlefieldIds={
                  isDeclareAttackers && player.id === activePlayerIndex
                    ? selectedAttackers
                    : isDeclareBlockers && player.id === defendingPlayerId
                      ? selectedBlockers[activeAttackerId ?? ''] ?? new Set()
                      : undefined
                }
                onToggleBattlefield={
                  isDeclareAttackers && player.id === activePlayerIndex
                    ? toggleAttacker
                    : isDeclareBlockers && player.id === defendingPlayerId
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
                        loadAbilityGraphForObject(objectId);
                      }
                    : undefined
                }
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
