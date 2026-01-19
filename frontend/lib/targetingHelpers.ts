import { EngineGameObjectSnapshot, EnginePlayerSnapshot } from '@/lib/engine';
import { EffectTargetSpec, TargetHints, deriveTargetHintsForTarget } from '@/lib/targeting';

export type SelectionState = Record<string, { objectIds: string[]; playerIds: number[] }>;

export const buildSelectionKey = (nodeId: string, key: string) => `${nodeId}:${key}`;

export const sanitizeSelection = (
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

export const filterObjects = (
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

export const filterPlayers = (
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

export const buildTargetsForSpec = (
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

export const buildTargetsByEffect = (
  specs: Array<{ nodeId: string; spec: EffectTargetSpec }>,
  selections: SelectionState,
  battlefieldObjects: EngineGameObjectSnapshot[],
  stackSpellObjects: EngineGameObjectSnapshot[],
  players: EnginePlayerSnapshot[],
  currentPriority: number | null
) => {
  const result: Record<string, Record<string, any>> = {};
  specs.forEach(({ nodeId, spec }) => {
    const selectionKey = buildSelectionKey(nodeId, spec.key);
    const baseSelection = selections[selectionKey] ?? { objectIds: [], playerIds: [] };
    const hints = deriveTargetHintsForTarget(spec.target, spec.maxTargets ?? null, {
      allowPlayers: spec.allowPlayers,
      allowObjects: spec.allowObjects,
    });
    const objectPool = spec.useStackObjects ? stackSpellObjects : battlefieldObjects;
    const filteredObjects = hints.allowObjects ? filterObjects(objectPool, hints, currentPriority) : [];
    const filteredPlayers = hints.allowPlayers ? filterPlayers(players, hints, currentPriority) : [];
    const sanitized = sanitizeSelection(baseSelection, filteredObjects, filteredPlayers);
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

