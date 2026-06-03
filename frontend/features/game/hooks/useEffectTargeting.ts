import { useEffect, useMemo, useState } from 'react';
import {
  engineApi,
  EngineActionRequest,
  EngineGameObjectSnapshot,
  EngineGameStateSnapshot,
  EnginePlayerSnapshot,
} from '@/lib/engine';
import { deriveTargetHintsForTarget, deriveTargetSpecs, EffectTargetSpec, TargetHints } from '@/lib/targeting';
import { isEffectActiveForModes, ModalChoiceConfig } from '@/lib/modalChoices';
import { formatEffect } from '@/lib/effectTypes';
import {
  SelectionState,
  buildSelectionKey,
  buildTargetsByEffect,
  buildTargetsForSpec,
  filterObjects,
  filterPlayers,
  sanitizeSelection,
} from '@/lib/targetingHelpers';

export type EffectTargetGroup = {
  id: string;
  nodeId: string;
  key: string;
  label: string;
  objectLabel?: string;
  playerLabel?: string;
  minTargets?: number | null;
  errors?: string[];
  objectTargetStatus?: Record<string, boolean | null>;
  playerTargetStatus?: Record<number, boolean | null>;
  objects: EngineGameObjectSnapshot[];
  players: EnginePlayerSnapshot[];
  selectedObjectIds: string[];
  selectedPlayerIds: number[];
  maxObjectTargets?: number | null;
  maxPlayerTargets?: number | null;
  objectTargetStatus?: Record<string, boolean | null>;
  playerTargetStatus?: Record<number, boolean | null>;
  onChangeObjects: (ids: string[]) => void;
  onChangePlayers: (ids: number[]) => void;
  onClear: () => void;
};


export const useEffectTargeting = ({
  gameState,
  selectedGraph,
  currentPriority,
  selectedHandId,
  modalConfig,
  selectedModes = [],
}: {
  gameState: EngineGameStateSnapshot | null;
  selectedGraph: any;
  currentPriority: number | null;
  selectedHandId: string | null;
  modalConfig?: ModalChoiceConfig | null;
  selectedModes?: string[];
}) => {
  const [selections, setSelections] = useState<SelectionState>({});
  const [effectErrors, setEffectErrors] = useState<Record<string, string[]>>({});
  const [globalErrors, setGlobalErrors] = useState<string[]>([]);
  const [targetStatus, setTargetStatus] = useState<
    Record<string, { objects: Record<string, boolean | null>; players: Record<number, boolean | null> }>
  >({});
  const effectSteps = useMemo(() => {
    const steps = selectedGraph?.steps ?? [];
    return steps.filter((step: any) => {
      if (!step?.effect) return false;
      return isEffectActiveForModes(step.effect, modalConfig ?? null, selectedModes);
    });
  }, [modalConfig, selectedGraph, selectedModes]);
  const targetSpecs = useMemo(() => {
    const specs: Array<{ nodeId: string; effect: any; spec: EffectTargetSpec }> = [];
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

  const battlefieldObjects = useMemo(() => {
    return gameState?.objects.filter((obj) => obj.zone === 'battlefield') ?? [];
  }, [gameState]);

  useEffect(() => {
    setSelections({});
  }, [selectedGraph, selectedHandId, selectedModes.join('|')]);

  const targetGroups: EffectTargetGroup[] = useMemo(() => {
    if (!gameState || targetSpecs.length === 0) return [];
    return targetSpecs.map(({ nodeId, effect, spec }) => {
      const selectionKey = buildSelectionKey(nodeId, spec.key);
      const baseSelection = selections[selectionKey] ?? { objectIds: [], playerIds: [] };
      const hints = deriveTargetHintsForTarget(spec.target, spec.maxTargets ?? null, {
        allowPlayers: spec.allowPlayers,
        allowObjects: spec.allowObjects,
      });
      const objects = hints.allowObjects
        ? filterObjects(spec.useStackObjects ? stackSpellObjects : battlefieldObjects, hints, currentPriority)
        : [];
      const players = hints.allowPlayers ? filterPlayers(gameState.players, hints, currentPriority) : [];
      const sanitized = sanitizeSelection(baseSelection, objects, players);
      const labelBase = formatEffect(effect);
      const label =
        targetSpecs.filter((entry) => entry.nodeId === nodeId).length > 1
          ? `${labelBase} · ${spec.label}`
          : labelBase;
      return {
        id: selectionKey,
        nodeId,
        key: spec.key,
        label,
        objectLabel: spec.useStackObjects ? 'Spells on Stack' : 'Objects',
        playerLabel: 'Players',
        minTargets: typeof spec.minTargets === 'number' ? spec.minTargets : null,
        errors: effectErrors[nodeId] ?? [],
        objectTargetStatus: targetStatus[selectionKey]?.objects ?? {},
        playerTargetStatus: targetStatus[selectionKey]?.players ?? {},
        objects,
        players,
        selectedObjectIds: sanitized.objectIds,
        selectedPlayerIds: sanitized.playerIds,
        maxObjectTargets: hints.maxObjectTargets ?? null,
        maxPlayerTargets: hints.maxPlayerTargets ?? null,
        onChangeObjects: (ids: string[]) =>
          setSelections((prev) => ({
            ...prev,
            [selectionKey]: { ...(prev[selectionKey] ?? baseSelection), objectIds: ids },
          })),
        onChangePlayers: (ids: number[]) =>
          setSelections((prev) => ({
            ...prev,
            [selectionKey]: { ...(prev[selectionKey] ?? baseSelection), playerIds: ids },
          })),
        onClear: () =>
          setSelections((prev) => ({
            ...prev,
            [selectionKey]: { objectIds: [], playerIds: [] },
          })),
      };
    });
  }, [battlefieldObjects, currentPriority, effectErrors, gameState, selections, stackSpellObjects, targetSpecs]);

  const targetsByEffect = useMemo(() => {
    return buildTargetsByEffect(
      targetSpecs,
      selections,
      battlefieldObjects,
      stackSpellObjects,
      gameState?.players ?? [],
      currentPriority
    );
  }, [battlefieldObjects, currentPriority, gameState?.players, selections, stackSpellObjects, targetSpecs]);

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

  const nodeIds = useMemo(() => Array.from(new Set(targetSpecs.map((entry) => entry.nodeId))), [targetSpecs]);

  useEffect(() => {
    if (!gameState || nodeIds.length === 0) {
      setEffectErrors({});
      setGlobalErrors([]);
      return;
    }
    const context = {
      controller_id: currentPriority,
      source_id: selectedHandId ?? undefined,
      targets: {},
      targets_by_effect: targetsByEffect,
      required_targets_by_effect: requiredTargetsByEffect,
      distinct_targets_by_effect: distinctTargetsByEffect,
      min_targets_by_effect: minTargetsByEffect,
    };
    const checkTargets = async () => {
      try {
        const response = await engineApi.execute({
          action: 'check_targets',
          game_state: gameState,
          contexts: [context],
        });
        const issues = (response.result?.checks?.[0]?.issues as string[]) || [];
        const nextErrors: Record<string, string[]> = {};
        const nextGlobal: string[] = [];
        issues.forEach((issue) => {
          const matchId = nodeIds.find((nodeId) => issue.startsWith(`${nodeId}:`));
          if (matchId) {
            const message = issue.slice(matchId.length + 1).trim();
            nextErrors[matchId] = [...(nextErrors[matchId] ?? []), message];
          } else {
            nextGlobal.push(issue);
          }
        });
        setEffectErrors(nextErrors);
        setGlobalErrors(nextGlobal);
      } catch {
        setEffectErrors({});
        setGlobalErrors([]);
      }
    };
    checkTargets();
  }, [
    currentPriority,
    distinctTargetsByEffect,
    gameState,
    minTargetsByEffect,
    nodeIds,
    requiredTargetsByEffect,
    selectedHandId,
    targetsByEffect,
  ]);

  useEffect(() => {
    if (!gameState || targetSpecs.length === 0) {
      setTargetStatus({});
      return;
    }
    let cancelled = false;
    let timeoutId: number | undefined;
    const contexts: Array<{
      groupId: string;
      kind: 'object' | 'player';
      id: string | number;
      context: EngineActionRequest['context'];
    }> = [];

    const buildTargetsByEffectWithOverride = (
      overrideKey: string,
      overrideSelection: { objectIds: string[]; playerIds: number[] }
    ) => {
      const result: Record<string, Record<string, any>> = {};
      targetSpecs.forEach(({ nodeId, spec }) => {
        const selectionKey = buildSelectionKey(nodeId, spec.key);
        const baseSelection =
          selectionKey === overrideKey ? overrideSelection : selections[selectionKey] ?? { objectIds: [], playerIds: [] };
        const hints = deriveTargetHintsForTarget(spec.target, spec.maxTargets ?? null, {
          allowPlayers: spec.allowPlayers,
          allowObjects: spec.allowObjects,
        });
        const objects = hints.allowObjects
          ? filterObjects(spec.useStackObjects ? stackSpellObjects : battlefieldObjects, hints, currentPriority)
          : [];
        const players = hints.allowPlayers ? filterPlayers(gameState.players, hints, currentPriority) : [];
        const sanitized = sanitizeSelection(baseSelection, objects, players);
        const targets = buildTargetsForSpec(spec, sanitized);
        if (hints.objectTypes.size > 0) {
          targets.target_object_types = Array.from(hints.objectTypes);
        }
        if (hints.objectFilter !== 'any') {
          targets.target_object_scope = hints.objectFilter === 'controller' ? 'you_control' : 'opponent_control';
        }
        if (hints.playerFilter !== 'any') {
          targets.target_scope = hints.playerFilter;
        }
        if (!result[nodeId]) {
          result[nodeId] = {};
        }
        Object.assign(result[nodeId], targets);
      });
      return result;
    };

    targetSpecs.forEach(({ nodeId, spec }) => {
      const selectionKey = buildSelectionKey(nodeId, spec.key);
      const baseSelection = selections[selectionKey] ?? { objectIds: [], playerIds: [] };
      const hints = deriveTargetHintsForTarget(spec.target, spec.maxTargets ?? null, {
        allowPlayers: spec.allowPlayers,
        allowObjects: spec.allowObjects,
      });
      const objects = hints.allowObjects
        ? filterObjects(spec.useStackObjects ? stackSpellObjects : battlefieldObjects, hints, currentPriority)
        : [];
      const players = hints.allowPlayers ? filterPlayers(gameState.players, hints, currentPriority) : [];
      objects.forEach((obj) => {
        let next = baseSelection.objectIds.includes(obj.id)
          ? baseSelection.objectIds
          : [...baseSelection.objectIds, obj.id];
        if (hints.maxObjectTargets && next.length > hints.maxObjectTargets) {
          return;
        }
        const override = { objectIds: next, playerIds: baseSelection.playerIds };
        contexts.push({
          groupId: selectionKey,
          kind: 'object',
          id: obj.id,
          context: {
            controller_id: currentPriority,
            source_id: selectedHandId ?? undefined,
            targets: {},
            targets_by_effect: buildTargetsByEffectWithOverride(selectionKey, override),
            required_targets_by_effect: requiredTargetsByEffect,
            distinct_targets_by_effect: distinctTargetsByEffect,
            min_targets_by_effect: minTargetsByEffect,
          },
        });
      });
      players.forEach((player) => {
        let next = baseSelection.playerIds.includes(player.id)
          ? baseSelection.playerIds
          : [...baseSelection.playerIds, player.id];
        if (hints.maxPlayerTargets && next.length > hints.maxPlayerTargets) {
          return;
        }
        const override = { objectIds: baseSelection.objectIds, playerIds: next };
        contexts.push({
          groupId: selectionKey,
          kind: 'player',
          id: player.id,
          context: {
            controller_id: currentPriority,
            source_id: selectedHandId ?? undefined,
            targets: {},
            targets_by_effect: buildTargetsByEffectWithOverride(selectionKey, override),
            required_targets_by_effect: requiredTargetsByEffect,
            distinct_targets_by_effect: distinctTargetsByEffect,
            min_targets_by_effect: minTargetsByEffect,
          },
        });
      });
    });

    if (contexts.length === 0) {
      setTargetStatus({});
      return;
    }
    const checkTargets = async () => {
      try {
        const chunkSize = 80;
        const checks: Array<{ legal: boolean }> = [];
        for (let i = 0; i < contexts.length; i += chunkSize) {
          const response = await engineApi.execute({
            action: 'check_targets',
            game_state: gameState,
            contexts: contexts.slice(i, i + chunkSize).map((entry) => entry.context),
          });
          const chunkChecks = response.result?.checks as Array<{ legal: boolean }> | undefined;
          if (chunkChecks) {
            checks.push(...chunkChecks);
          }
        }
        if (checks.length === 0 || cancelled) return;
        const next: Record<string, { objects: Record<string, boolean | null>; players: Record<number, boolean | null> }> = {};
        contexts.forEach((entry, idx) => {
          if (!next[entry.groupId]) {
            next[entry.groupId] = { objects: {}, players: {} };
          }
          const isLegal = checks[idx]?.legal ?? null;
          if (entry.kind === 'object' && typeof entry.id === 'string') {
            next[entry.groupId].objects[entry.id] = isLegal;
          }
          if (entry.kind === 'player' && typeof entry.id === 'number') {
            next[entry.groupId].players[entry.id] = isLegal;
          }
        });
        if (!cancelled) {
          setTargetStatus(next);
        }
      } catch {
        if (!cancelled) {
          setTargetStatus({});
        }
      }
    };
    timeoutId = window.setTimeout(() => {
      if (!cancelled) {
        checkTargets();
      }
    }, 150);
    return () => {
      cancelled = true;
      if (timeoutId) {
        window.clearTimeout(timeoutId);
      }
    };
  }, [
    battlefieldObjects,
    currentPriority,
    distinctTargetsByEffect,
    gameState,
    minTargetsByEffect,
    requiredTargetsByEffect,
    selections,
    selectedHandId,
    stackSpellObjects,
    targetSpecs,
  ]);

  const allSelectedObjectIds = useMemo(() => {
    const ids = new Set<string>();
    targetGroups.forEach((group) => group.selectedObjectIds.forEach((id) => ids.add(id)));
    return Array.from(ids);
  }, [targetGroups]);

  const allSelectedPlayerIds = useMemo(() => {
    const ids = new Set<number>();
    targetGroups.forEach((group) => group.selectedPlayerIds.forEach((id) => ids.add(id)));
    return Array.from(ids);
  }, [targetGroups]);

  const clearAllTargets = () => setSelections({});

  return {
    targetGroups,
    targetsByEffect,
    requiredTargetsByEffect,
    distinctTargetsByEffect,
    minTargetsByEffect,
    globalTargetErrors: globalErrors,
    allSelectedObjectIds,
    allSelectedPlayerIds,
    clearAllTargets,
  };
};

