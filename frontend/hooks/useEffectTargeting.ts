import { useEffect, useMemo, useState } from 'react';
import {
  engineApi,
  EngineActionRequest,
  EngineGameObjectSnapshot,
  EngineGameStateSnapshot,
  EnginePlayerSnapshot,
} from '@/lib/engine';
import { deriveTargetHintsForTarget, deriveTargetSpecs, EffectTargetSpec, TargetHints } from '@/lib/targeting';
import { formatEffect } from '@/lib/effectTypes';

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

type SelectionState = Record<string, { objectIds: string[]; playerIds: number[] }>;

const buildSelectionKey = (nodeId: string, key: string) => `${nodeId}:${key}`;

const sanitizeSelection = (
  selection: { objectIds: string[]; playerIds: number[] },
  objects: EngineGameObjectSnapshot[],
  players: EnginePlayerSnapshot[]
) => {
  const objectSet = new Set(objects.map((obj) => obj.id));
  const playerSet = new Set(players.map((player) => player.id));
  return {
    objectIds: selection.objectIds.filter((id) => objectSet.has(id)),
    playerIds: selection.playerIds.filter((id) => playerSet.has(id)),
  };
};

const filterObjects = (
  objects: EngineGameObjectSnapshot[],
  hints: TargetHints,
  currentPriority: number | null
) => {
  return objects.filter((obj) => {
    if (hints.objectFilter === 'opponent') {
      if (currentPriority !== null && obj.controller_id === currentPriority) return false;
    }
    if (hints.objectFilter === 'controller') {
      if (currentPriority !== null && obj.controller_id !== currentPriority) return false;
    }
    if (hints.objectTypes.size === 0) return true;
    return obj.types.some((type) => hints.objectTypes.has(type));
  });
};

const filterPlayers = (
  players: EnginePlayerSnapshot[],
  hints: TargetHints,
  currentPriority: number | null
) => {
  return players.filter((player) => {
    if (hints.playerFilter === 'opponent') {
      if (currentPriority !== null && player.id === currentPriority) return false;
    }
    if (hints.playerFilter === 'controller') {
      if (currentPriority !== null && player.id !== currentPriority) return false;
    }
    return true;
  });
};

const buildTargetsForSpec = (
  spec: EffectTargetSpec,
  selection: { objectIds: string[]; playerIds: number[] }
) => {
  const targets: Record<string, any> = {};
  if (spec.key === 'target') {
    if (selection.objectIds.length > 0) {
      targets.target = selection.objectIds[0];
      targets.targets = selection.objectIds;
      if (spec.target === 'spell') {
        targets.spell_target = selection.objectIds[0];
        targets.spell_targets = selection.objectIds;
      }
    }
    if (selection.playerIds.length > 0) {
      targets.target_player = selection.playerIds[0];
      targets.target_players = selection.playerIds;
    }
    return targets;
  }
  if (spec.key === 'redirectTarget') {
    if (selection.objectIds.length > 0) {
      targets.redirectTarget = selection.objectIds[0];
    } else if (selection.playerIds.length > 0) {
      targets.target_player = selection.playerIds[0];
      targets.target_players = selection.playerIds;
    }
    return targets;
  }
  if (selection.objectIds.length > 0) {
    targets[spec.key] = selection.objectIds[0];
  }
  return targets;
};

export const useEffectTargeting = ({
  gameState,
  selectedGraph,
  currentPriority,
  selectedHandId,
}: {
  gameState: EngineGameStateSnapshot | null;
  selectedGraph: any;
  currentPriority: number | null;
  selectedHandId: string | null;
}) => {
  const [selections, setSelections] = useState<SelectionState>({});
  const [effectErrors, setEffectErrors] = useState<Record<string, string[]>>({});
  const [globalErrors, setGlobalErrors] = useState<string[]>([]);
  const [targetStatus, setTargetStatus] = useState<
    Record<string, { objects: Record<string, boolean | null>; players: Record<number, boolean | null> }>
  >({});
  const effectNodes = useMemo(
    () => (selectedGraph?.nodes ?? []).filter((node: any) => node?.type === 'EFFECT'),
    [selectedGraph]
  );
  const targetSpecs = useMemo(() => {
    const specs: Array<{ nodeId: string; effect: any; spec: EffectTargetSpec }> = [];
    effectNodes.forEach((node: any) => {
      deriveTargetSpecs(node?.data ?? {}).forEach((spec) => {
        specs.push({ nodeId: node.id, effect: node.data, spec });
      });
    });
    return specs;
  }, [effectNodes]);

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
  }, [selectedGraph, selectedHandId]);

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
    const result: Record<string, Record<string, any>> = {};
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
      const players = hints.allowPlayers ? filterPlayers(gameState?.players ?? [], hints, currentPriority) : [];
      const sanitized = sanitizeSelection(baseSelection, objects, players);
      const targets = buildTargetsForSpec(spec, sanitized);
      if (spec.distinct) {
        if (!result[nodeId]) {
          result[nodeId] = {};
        }
      }
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

