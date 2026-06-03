import { useEffect, useMemo, useState } from 'react';
import { engineApi, EngineActionRequest, EngineGameStateSnapshot } from '@/lib/engine';
import { deriveTargetHintsForTarget, deriveTargetSpecs } from '@/lib/targeting';
import { isEffectActiveForModes, ModalChoiceConfig } from '@/lib/modalChoices';
import { formatEffect } from '@/lib/effectTypes';
import {
  SelectionState,
  buildSelectionKey,
  buildTargetsByEffect,
  filterObjects,
  filterPlayers,
  sanitizeSelection,
} from '@/lib/targetingHelpers';

export type CopyEffectTargetGroup = {
  copyIndex: number;
  id: string;
  nodeId: string;
  key: string;
  label: string;
  objectLabel?: string;
  playerLabel?: string;
  minTargets?: number | null;
  errors?: string[];
  objects: EngineGameStateSnapshot['objects'];
  players: EngineGameStateSnapshot['players'];
  selectedObjectIds: string[];
  selectedPlayerIds: number[];
  maxObjectTargets?: number | null;
  maxPlayerTargets?: number | null;
  onChangeObjects: (ids: string[]) => void;
  onChangePlayers: (ids: number[]) => void;
  onClear: () => void;
};

export const useCopyEffectTargeting = ({
  gameState,
  selectedGraph,
  currentPriority,
  selectedHandId,
  modalConfig,
  selectedModes = [],
  copies = 0,
}: {
  gameState: EngineGameStateSnapshot | null;
  selectedGraph: any;
  currentPriority: number | null;
  selectedHandId: string | null;
  modalConfig?: ModalChoiceConfig | null;
  selectedModes?: string[];
  copies?: number;
}) => {
  const [copySelections, setCopySelections] = useState<SelectionState[]>([]);
  const [copyErrors, setCopyErrors] = useState<Record<number, Record<string, string[]>>>({});
  const [copyGlobalErrors, setCopyGlobalErrors] = useState<Record<number, string[]>>({});

  const effectSteps = useMemo(() => {
    const steps = selectedGraph?.steps ?? [];
    return steps.filter((step: any) => {
      if (!step?.effect) return false;
      return isEffectActiveForModes(step.effect, modalConfig ?? null, selectedModes);
    });
  }, [modalConfig, selectedGraph, selectedModes]);

  const targetSpecs = useMemo(() => {
    const specs: Array<{ nodeId: string; effect: any; spec: any }> = [];
    effectSteps.forEach((step: any) => {
      const effectBody = step?.effect?.effect;
      if (effectBody?.kind !== 'one_shot') return;
      const action = effectBody?.action ?? {};
      deriveTargetSpecs(action).forEach((spec) => {
        specs.push({ nodeId: step.id, effect: action, spec });
      });
    });
    return specs;
  }, [effectSteps]);

  const battlefieldObjects = useMemo(() => {
    return gameState?.objects.filter((obj) => obj.zone === 'battlefield') ?? [];
  }, [gameState]);

  const stackSpellObjects = useMemo(() => {
    if (!gameState) return [];
    const stackSpellIds = new Set(
      gameState.stack
        .filter((item) => item.kind === 'spell')
        .map((item) => item.payload?.object_id)
        .filter((id): id is string => Boolean(id))
    );
    return gameState.objects.filter((obj) => stackSpellIds.has(obj.id));
  }, [gameState]);

  useEffect(() => {
    if (copies <= 0 || targetSpecs.length === 0) {
      setCopySelections([]);
      return;
    }
    setCopySelections((prev) => {
      if (prev.length === copies) return prev;
      const next = [...prev];
      while (next.length < copies) next.push({});
      return next.slice(0, copies);
    });
  }, [copies, targetSpecs.length]);

  const requiredTargetsByEffect = useMemo(() => {
    const result: Record<string, string[]> = {};
    targetSpecs.forEach(({ nodeId, spec }) => {
      if (!result[nodeId]) {
        result[nodeId] = [];
      }
      if (spec.required && !result[nodeId].includes(spec.key)) {
        result[nodeId].push(spec.key);
      }
    });
    return result;
  }, [targetSpecs]);

  const distinctTargetsByEffect = useMemo(() => {
    const result: Record<string, string[]> = {};
    targetSpecs.forEach(({ nodeId, spec }) => {
      if (!spec.distinct) return;
      if (!result[nodeId]) {
        result[nodeId] = [];
      }
      if (!result[nodeId].includes(spec.key)) {
        result[nodeId].push(spec.key);
      }
    });
    return result;
  }, [targetSpecs]);

  const minTargetsByEffect = useMemo(() => {
    const result: Record<string, Record<string, number>> = {};
    targetSpecs.forEach(({ nodeId, spec }) => {
      if (typeof spec.minTargets !== 'number') return;
      if (!result[nodeId]) {
        result[nodeId] = {};
      }
      const current = result[nodeId][spec.key] ?? 0;
      result[nodeId][spec.key] = Math.max(current, spec.minTargets);
    });
    return result;
  }, [targetSpecs]);

  const copyTargetsByEffectList = useMemo(() => {
    if (!gameState || copySelections.length === 0) return [];
    return copySelections.map((selection) =>
      buildTargetsByEffect(
        targetSpecs,
        selection,
        battlefieldObjects,
        stackSpellObjects,
        gameState.players,
        currentPriority
      )
    );
  }, [battlefieldObjects, copySelections, currentPriority, gameState, stackSpellObjects, targetSpecs]);

  const copyRequiredTargetsByEffectList = useMemo(() => {
    if (copySelections.length === 0) return [];
    return copySelections.map(() => requiredTargetsByEffect);
  }, [copySelections, requiredTargetsByEffect]);

  const copyDistinctTargetsByEffectList = useMemo(() => {
    if (copySelections.length === 0) return [];
    return copySelections.map(() => distinctTargetsByEffect);
  }, [copySelections, distinctTargetsByEffect]);

  const copyMinTargetsByEffectList = useMemo(() => {
    if (copySelections.length === 0) return [];
    return copySelections.map(() => minTargetsByEffect);
  }, [copySelections, minTargetsByEffect]);

  const copyTargetGroups = useMemo<CopyEffectTargetGroup[]>(() => {
    if (!gameState || copySelections.length === 0 || targetSpecs.length === 0) return [];
    const groups: CopyEffectTargetGroup[] = [];
    copySelections.forEach((selectionState, copyIndex) => {
      targetSpecs.forEach(({ nodeId, effect, spec }) => {
        const selectionKey = buildSelectionKey(nodeId, spec.key);
        const baseSelection = selectionState[selectionKey] ?? { objectIds: [], playerIds: [] };
        const targetHints = deriveTargetHintsForTarget(spec.target, spec.maxTargets ?? null, {
          allowPlayers: spec.allowPlayers,
          allowObjects: spec.allowObjects,
        });
        const objects = targetHints.allowObjects
          ? filterObjects(spec.useStackObjects ? stackSpellObjects : battlefieldObjects, targetHints, currentPriority)
          : [];
        const players = targetHints.allowPlayers ? filterPlayers(gameState.players, targetHints, currentPriority) : [];
        const sanitized = sanitizeSelection(baseSelection, objects, players);
        const labelBase = formatEffect(effect);
        const label =
          targetSpecs.filter((entry) => entry.nodeId === nodeId).length > 1
            ? `${labelBase} · ${spec.label}`
            : labelBase;
        groups.push({
          copyIndex,
          id: `${copyIndex}:${selectionKey}`,
          nodeId,
          key: spec.key,
          label,
          objectLabel: spec.useStackObjects ? 'Spells on Stack' : 'Objects',
          playerLabel: 'Players',
          minTargets: typeof spec.minTargets === 'number' ? spec.minTargets : null,
          errors: copyErrors[copyIndex]?.[nodeId] ?? [],
          objects,
          players,
          selectedObjectIds: sanitized.objectIds,
          selectedPlayerIds: sanitized.playerIds,
          maxObjectTargets: targetHints.maxObjectTargets ?? null,
          maxPlayerTargets: targetHints.maxPlayerTargets ?? null,
          onChangeObjects: (ids: string[]) =>
            setCopySelections((prev) => {
              const next = [...prev];
              const current = next[copyIndex] ?? {};
              next[copyIndex] = { ...current, [selectionKey]: { objectIds: ids, playerIds: sanitized.playerIds } };
              return next;
            }),
          onChangePlayers: (ids: number[]) =>
            setCopySelections((prev) => {
              const next = [...prev];
              const current = next[copyIndex] ?? {};
              next[copyIndex] = { ...current, [selectionKey]: { objectIds: sanitized.objectIds, playerIds: ids } };
              return next;
            }),
          onClear: () =>
            setCopySelections((prev) => {
              const next = [...prev];
              const current = next[copyIndex] ?? {};
              next[copyIndex] = { ...current, [selectionKey]: { objectIds: [], playerIds: [] } };
              return next;
            }),
        });
      });
    });
    return groups;
  }, [battlefieldObjects, copyErrors, copySelections, currentPriority, gameState, stackSpellObjects, targetSpecs]);

  useEffect(() => {
    if (!gameState || copySelections.length === 0 || targetSpecs.length === 0) {
      setCopyErrors({});
      setCopyGlobalErrors({});
      return;
    }
    const contexts: Array<{ copyIndex: number; context: EngineActionRequest['context'] }> = [];
    copySelections.forEach((selection, copyIndex) => {
      contexts.push({
        copyIndex,
        context: {
          controller_id: currentPriority,
          source_id: selectedHandId ?? undefined,
          targets: {},
          targets_by_effect: buildTargetsByEffect(
            targetSpecs,
            selection,
            battlefieldObjects,
            stackSpellObjects,
            gameState.players,
            currentPriority
          ),
          required_targets_by_effect: requiredTargetsByEffect,
          distinct_targets_by_effect: distinctTargetsByEffect,
          min_targets_by_effect: minTargetsByEffect,
        },
      });
    });
    const checkTargets = async () => {
      try {
        const response = await engineApi.execute({
          action: 'check_targets',
          game_state: gameState,
          contexts: contexts.map((entry) => entry.context),
        });
        const checks = (response.result?.checks as Array<{ issues?: string[] }> | undefined) ?? [];
        const nextErrors: Record<number, Record<string, string[]>> = {};
        const nextGlobals: Record<number, string[]> = {};
        checks.forEach((check, idx) => {
          const copyIndex = contexts[idx]?.copyIndex;
          if (copyIndex === undefined) return;
          const issues = check.issues ?? [];
          const perNode: Record<string, string[]> = {};
          const globals: string[] = [];
          issues.forEach((issue) => {
            const matchId = targetSpecs.find((entry) => issue.startsWith(`${entry.nodeId}:`))?.nodeId;
            if (matchId) {
              const message = issue.slice(matchId.length + 1).trim();
              perNode[matchId] = [...(perNode[matchId] ?? []), message];
            } else {
              globals.push(issue);
            }
          });
          nextErrors[copyIndex] = perNode;
          nextGlobals[copyIndex] = globals;
        });
        setCopyErrors(nextErrors);
        setCopyGlobalErrors(nextGlobals);
      } catch {
        setCopyErrors({});
        setCopyGlobalErrors({});
      }
    };
    checkTargets();
  }, [
    battlefieldObjects,
    copySelections,
    currentPriority,
    distinctTargetsByEffect,
    gameState,
    minTargetsByEffect,
    requiredTargetsByEffect,
    selectedHandId,
    stackSpellObjects,
    targetSpecs,
  ]);

  const copyTargetErrors = useMemo(() => {
    const errors: string[] = [];
    if (!copySelections.length) return errors;
    copySelections.forEach((_selection, index) => {
      const perNode = copyErrors[index] ?? {};
      Object.entries(perNode).forEach(([nodeId, messages]) => {
        messages.forEach((message) => {
          errors.push(`Copy ${index + 1}: ${nodeId} ${message}`);
        });
      });
      const globals = copyGlobalErrors[index] ?? [];
      globals.forEach((message) => {
        errors.push(`Copy ${index + 1}: ${message}`);
      });
    });
    return errors;
  }, [copyErrors, copyGlobalErrors, copySelections]);

  return {
    copyTargetGroups,
    copyTargetsByEffectList,
    copyRequiredTargetsByEffectList,
    copyDistinctTargetsByEffectList,
    copyMinTargetsByEffectList,
    copyTargetErrors,
  };
};

