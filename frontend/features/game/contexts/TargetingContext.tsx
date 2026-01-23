'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, engineApi } from '@/lib/engine';
import { useTargeting } from '../hooks/useTargeting';
import { useEffectTargeting, EffectTargetGroup } from '../hooks/useEffectTargeting';
import { useCopyEffectTargeting } from '../hooks/useCopyEffectTargeting';
import { useSearchChoices } from '../hooks/useSearchChoices';
import { ModalChoiceConfig } from '@/lib/modalChoices';

/**
 * TargetingContext - Target selection and validation
 * 
 * Responsible for:
 * - Object/player target selection
 * - Effect-based targeting (per-effect targets)
 * - Search choices (library/graveyard search)
 * - Copy spell targets
 * - Target validation via engine
 */

export interface TargetingContextValue {
  // Global targeting (for simple spells)
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
  
  // Effect targeting (for complex spells)
  effectTargetGroups: EffectTargetGroup[];
  targetsByEffect: Record<string, Record<string, any>>;
  requiredTargetsByEffect: Record<string, string[]>;
  distinctTargetsByEffect: Record<string, string[]>;
  minTargetsByEffect: Record<string, Record<string, number>>;
  globalTargetErrors: string[];
  effectTargetObjectIds: string[];
  effectTargetPlayerIds: number[];
  hasEffectTargets: boolean;
  mergedTargetsByEffect: Record<string, Record<string, any>>;
  
  // Search choices
  searchEntries: any[];
  searchTargetsByEffect: Record<string, Record<string, any>>;
  searchErrors: string[];
  
  // Copy spell targets
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
  
  // Resolved targets (unified)
  resolvedTargetObjectIds: string[];
  resolvedTargetPlayerIds: number[];
  targetSelectionErrors: string[];
  
  // Actions
  setSelectedTargetObjectIds: (ids: string[]) => void;
  setSelectedTargetPlayerIds: (ids: number[]) => void;
  setCopyTargetSelections: (selections: Array<{ objectIds: string[]; playerIds: number[] }>) => void;
  clearEffectTargets: () => void;
}

interface TargetingProviderProps {
  children: React.ReactNode;
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedBattlefieldId: string | null;
  selectedStackIndex: number | null;
  selectedGraph: any;
  modalChoiceConfig: ModalChoiceConfig | null;
  selectedModalModes: string[];
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
}

const TargetingContext = createContext<TargetingContextValue | null>(null);

export function TargetingProvider({
  children,
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedBattlefieldId,
  selectedStackIndex,
  selectedGraph,
  modalChoiceConfig,
  selectedModalModes,
  copyTargetsEnabled,
  copyTargetsCount,
}: TargetingProviderProps) {
  const value = useTargetingInternal({
    gameState,
    cardMap,
    priorityPlayer,
    selectedHandId,
    selectedBattlefieldId,
    selectedStackIndex,
    selectedGraph,
    modalChoiceConfig,
    selectedModalModes,
    copyTargetsEnabled,
    copyTargetsCount,
  });
  return <TargetingContext.Provider value={value}>{children}</TargetingContext.Provider>;
}

export function useTargetingContext() {
  const context = useContext(TargetingContext);
  if (!context) {
    throw new Error('useTargetingContext must be used within TargetingProvider');
  }
  return context;
}

interface UseTargetingInternalArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedBattlefieldId: string | null;
  selectedStackIndex: number | null;
  selectedGraph: any;
  modalChoiceConfig: ModalChoiceConfig | null;
  selectedModalModes: string[];
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
}

function useTargetingInternal({
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedBattlefieldId,
  selectedStackIndex,
  selectedGraph,
  modalChoiceConfig,
  selectedModalModes,
  copyTargetsEnabled,
  copyTargetsCount,
}: UseTargetingInternalArgs): TargetingContextValue {
  // Copy spell config
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

  // Stack graph for resolution
  const selectedStackGraph =
    selectedStackIndex !== null ? (gameState?.stack?.[selectedStackIndex]?.payload as any)?.graph : undefined;
  const activeGraph = selectedStackGraph ?? selectedGraph;

  // Global targeting hook
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
    currentPriority: priorityPlayer,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
  });

  // Effect targeting hook
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
    currentPriority: priorityPlayer,
    selectedHandId,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
  });

  // Search choices hook
  const {
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
  } = useSearchChoices({
    gameState,
    selectedGraph: activeGraph,
    currentPriority: priorityPlayer,
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
    // For stack items, don't show graph-based search UI
    isStackItem: selectedStackIndex !== null,
  });

  const hasEffectTargets = effectTargetGroups.length > 0 || searchEntries.length > 0;

  // Merge targets by effect
  const mergedTargetsByEffect = useMemo(() => {
    const result: Record<string, Record<string, any>> = { ...(targetsByEffect || {}) };
    Object.entries(searchTargetsByEffect).forEach(([nodeId, extra]) => {
      result[nodeId] = { ...(result[nodeId] || {}), ...(extra || {}) };
    });
    return result;
  }, [searchTargetsByEffect, targetsByEffect]);

  // Copy effect targeting
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
    currentPriority: priorityPlayer,
    selectedHandId,
    modalConfig: modalChoiceConfig,
    selectedModes: selectedModalModes,
    copies: copyTargetsByEffectCount,
  });

  // Resolved targets
  const resolvedTargetObjectIds = hasEffectTargets ? effectTargetObjectIds : selectedTargetObjectIds;
  const resolvedTargetPlayerIds = hasEffectTargets ? effectTargetPlayerIds : selectedTargetPlayerIds;

  // Initialize copy target selections
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

  // Clear copy errors when disabled
  useEffect(() => {
    if (!copySpellConfig.enabled) {
      setCopyTargetErrorsGlobal([]);
    }
  }, [copySpellConfig.enabled]);

  // Validate copy targets
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
        controller_id: priorityPlayer,
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
    priorityPlayer,
    distinctTargetsGlobal,
    gameState,
    hasEffectTargets,
    minTargetsGlobal,
    requiredTargetsGlobal,
    selectedHandId,
    targetHints,
  ]);

  // Target selection errors
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

  return {
    targetHints,
    selectedTargetObjectIds,
    selectedTargetPlayerIds,
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
    hasEffectTargets,
    mergedTargetsByEffect,
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
    copySpellConfig,
    copyTargetSelections,
    copyTargetErrorsGlobal,
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
    setSelectedTargetObjectIds,
    setSelectedTargetPlayerIds,
    setCopyTargetSelections,
    clearEffectTargets,
  };
}
