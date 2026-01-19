import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { engineApi, EngineActionRequest, EngineGameStateSnapshot } from '@/lib/engine';
import { deriveGlobalDistinctTargets, deriveGlobalMinTargets, deriveGlobalRequiredTargets, deriveTargetHints } from '@/lib/targeting';
import { ModalChoiceConfig } from '@/lib/modalChoices';
import { buildStackTargetHash } from '@/lib/stackTargets';

interface UseTargetingArgs {
  gameState: EngineGameStateSnapshot | null;
  selectedHandId: string | null;
  selectedGraph: any;
  currentPriority: number | null;
  modalConfig?: ModalChoiceConfig | null;
  selectedModes?: string[];
}

export const useTargeting = ({
  gameState,
  selectedHandId,
  selectedGraph,
  currentPriority,
  modalConfig,
  selectedModes = [],
}: UseTargetingArgs) => {
  const [selectedTargetObjectIds, setSelectedTargetObjectIds] = useState<string[]>([]);
  const [selectedTargetPlayerIds, setSelectedTargetPlayerIds] = useState<number[]>([]);
  useEffect(() => {
    setSelectedTargetObjectIds((prev) => (prev.length === 0 ? prev : []));
    setSelectedTargetPlayerIds((prev) => (prev.length === 0 ? prev : []));
  }, [selectedGraph, selectedHandId, selectedModes.join('|')]);
  const [objectTargetStatus, setObjectTargetStatus] = useState<Record<string, boolean | null>>({});
  const [playerTargetStatus, setPlayerTargetStatus] = useState<Record<number, boolean | null>>({});
  const [stackTargetChecks, setStackTargetChecks] = useState<Record<number, { legal: boolean; issues: string[] }>>({});
  const stackTargetHashesRef = useRef<Record<number, string>>({});
  const selectionTargetHashRef = useRef<string>('');

  const targetHints = useMemo(
    () => deriveTargetHints(selectedGraph, modalConfig, selectedModes),
    [modalConfig, selectedGraph, selectedModes]
  );
  const requiredTargets = useMemo(
    () => deriveGlobalRequiredTargets(selectedGraph, modalConfig, selectedModes),
    [modalConfig, selectedGraph, selectedModes]
  );
  const distinctTargets = useMemo(
    () => deriveGlobalDistinctTargets(selectedGraph, modalConfig, selectedModes),
    [modalConfig, selectedGraph, selectedModes]
  );
  const minTargets = useMemo(
    () => deriveGlobalMinTargets(selectedGraph, modalConfig, selectedModes),
    [modalConfig, selectedGraph, selectedModes]
  );
  const targetableObjects = gameState
    ? gameState.objects.filter((obj) => obj.zone === 'battlefield')
    : [];
  const stackSpellTargets = gameState
    ? gameState.stack
        .filter((item) => item.kind === 'spell')
        .map((item) => item.payload?.object_id)
        .filter((id): id is string => Boolean(id))
    : [];
  const stackSpellObjects = gameState
    ? gameState.objects.filter((obj) => stackSpellTargets.includes(obj.id))
    : [];
  const filteredTargetableObjects = targetHints.allowObjects
    ? targetableObjects.filter((obj) => {
        if (targetHints.objectFilter === 'opponent') {
          if (currentPriority !== null && obj.controller_id === currentPriority) return false;
        }
        if (targetHints.objectFilter === 'controller') {
          if (currentPriority !== null && obj.controller_id !== currentPriority) return false;
        }
        if (targetHints.objectTypes.size === 0) return true;
        return obj.types.some((type) => targetHints.objectTypes.has(type));
      })
    : [];
  const filteredTargetPlayers = targetHints.allowPlayers
    ? (gameState?.players ?? []).filter((player) => {
        if (targetHints.playerFilter === 'opponent') {
          return currentPriority === null ? true : player.id !== currentPriority;
        }
        if (targetHints.playerFilter === 'controller') {
          return currentPriority === null ? true : player.id === currentPriority;
        }
        return true;
      })
    : [];
  const shouldUseStackTargets = selectedGraph?.nodes?.some(
    (node: any) => node?.type === 'EFFECT' && node?.data?.target === 'spell'
  );

  const buildTargetContext = useCallback(
    (targets: Record<string, any>) => ({
      controller_id: currentPriority,
      source_id: selectedHandId ?? undefined,
      targets: {
        ...targets,
        ...(targetHints.playerFilter !== 'any' ? { target_scope: targetHints.playerFilter } : {}),
        ...(targetHints.objectFilter !== 'any'
          ? { target_object_scope: targetHints.objectFilter === 'controller' ? 'you_control' : 'opponent_control' }
          : {}),
        ...(targetHints.objectTypes.size > 0 ? { target_object_types: Array.from(targetHints.objectTypes) } : {}),
      },
      ...(requiredTargets.length > 0 ? { required_targets_by_effect: { _global: requiredTargets } } : {}),
      ...(distinctTargets.length > 0 ? { distinct_targets_by_effect: { _global: distinctTargets } } : {}),
      ...(Object.keys(minTargets).length > 0 ? { min_targets_by_effect: { _global: minTargets } } : {}),
    }),
    [currentPriority, distinctTargets, minTargets, requiredTargets, selectedHandId, targetHints]
  );

  const checkStackTargets = useCallback(async () => {
    if (!gameState) return;
    const contexts: Array<{ index: number; context: EngineActionRequest['context'] }> = [];
    const nextHashes: Record<number, string> = {};
    const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    gameState.stack.forEach((item, index) => {
      if (!item.payload?.context) return;
      const hash = buildStackTargetHash(item, objectMap, gameState.stack);
      nextHashes[index] = hash;
      if (stackTargetHashesRef.current[index] !== hash) {
        contexts.push({ index, context: item.payload.context as EngineActionRequest['context'] });
      }
    });
    const cleanupChecks = (updates: Record<number, { legal: boolean; issues: string[] }> = {}) => {
      setStackTargetChecks((prev) => {
        const next: Record<number, { legal: boolean; issues: string[] }> = {};
        Object.entries(prev).forEach(([key, value]) => {
          const index = Number(key);
          if (!Number.isNaN(index) && nextHashes[index]) {
            next[index] = value;
          }
        });
        Object.entries(updates).forEach(([key, value]) => {
          const index = Number(key);
          if (!Number.isNaN(index)) {
            next[index] = value;
          }
        });
        return next;
      });
    };
    if (contexts.length === 0) {
      stackTargetHashesRef.current = nextHashes;
      cleanupChecks();
      return;
    }
    try {
      const response = await engineApi.execute({
        action: 'check_targets',
        game_state: gameState,
        contexts: contexts.map((entry) => entry.context) as any,
      });
      const checks = response.result?.checks as Array<{ legal: boolean; issues?: string[] }> | undefined;
      if (!checks) return;
      const next: Record<number, { legal: boolean; issues: string[] }> = {};
      checks.forEach((check, idx) => {
        const index = contexts[idx]?.index;
        if (typeof index === 'number') {
          next[index] = { legal: !!check.legal, issues: check.issues ?? [] };
        }
      });
      stackTargetHashesRef.current = nextHashes;
      cleanupChecks(next);
    } catch {
      setStackTargetChecks({});
    }
  }, [gameState]);

  const checkSelectionTargets = useCallback(async () => {
    if (!gameState) return;
    if (!targetHints.allowObjects && !targetHints.allowPlayers) {
      setObjectTargetStatus({});
      setPlayerTargetStatus({});
      return;
    }
    const targetContexts: Array<{ key: string; context: EngineActionRequest['context'] }> = [];
    const playerContexts: Array<{ key: number; context: EngineActionRequest['context'] }> = [];

    const objectTargets = shouldUseStackTargets ? stackSpellObjects : filteredTargetableObjects;
    objectTargets.forEach((obj) => {
      const targets = shouldUseStackTargets ? { spell_target: obj.id } : { target: obj.id };
      targetContexts.push({ key: obj.id, context: buildTargetContext(targets) });
    });

    filteredTargetPlayers.forEach((player) => {
      playerContexts.push({ key: player.id, context: buildTargetContext({ target_player: player.id }) });
    });

    const hashPayload = {
      objectKeys: targetContexts.map((entry) => entry.key).sort(),
      playerKeys: playerContexts.map((entry) => entry.key).sort(),
      sourceId: selectedHandId ?? null,
      mode: shouldUseStackTargets ? 'spell' : 'object',
    };
    const hash = JSON.stringify(hashPayload);
    if (selectionTargetHashRef.current === hash) {
      return;
    }

    if (targetContexts.length === 0 && playerContexts.length === 0) {
      setObjectTargetStatus({});
      setPlayerTargetStatus({});
      selectionTargetHashRef.current = '';
      return;
    }

    try {
      const response = await engineApi.execute({
        action: 'check_targets',
        game_state: gameState,
        contexts: [...targetContexts, ...playerContexts].map((entry) => entry.context) as any,
      });
      const checks = response.result?.checks as Array<{ legal: boolean }> | undefined;
      if (!checks) return;

      const nextObjectStatus: Record<string, boolean | null> = {};
      const nextPlayerStatus: Record<number, boolean | null> = {};

      targetContexts.forEach((entry, idx) => {
        nextObjectStatus[entry.key] = checks[idx]?.legal ?? null;
      });
      playerContexts.forEach((entry, idx) => {
        nextPlayerStatus[entry.key] = checks[targetContexts.length + idx]?.legal ?? null;
      });

      setObjectTargetStatus(nextObjectStatus);
      setPlayerTargetStatus(nextPlayerStatus);
      selectionTargetHashRef.current = hash;
    } catch {
      setObjectTargetStatus({});
      setPlayerTargetStatus({});
      selectionTargetHashRef.current = '';
    }
  }, [
    buildTargetContext,
    filteredTargetPlayers,
    filteredTargetableObjects,
    gameState,
    selectedHandId,
    shouldUseStackTargets,
    stackSpellObjects,
    targetHints,
  ]);

  useEffect(() => {
    checkStackTargets();
  }, [checkStackTargets, gameState?.stack]);

  useEffect(() => {
    checkSelectionTargets();
  }, [checkSelectionTargets]);

  useEffect(() => {
    const isSameSelection = (next: string[]) =>
      next.length === selectedTargetObjectIds.length &&
      next.every((id, index) => id === selectedTargetObjectIds[index]);
    if (!targetHints.allowObjects) {
      if (selectedTargetObjectIds.length > 0) {
        setSelectedTargetObjectIds([]);
      }
      return;
    }
    if (shouldUseStackTargets) {
      const next = selectedTargetObjectIds.filter((id) => stackSpellTargets.includes(id));
      if (!isSameSelection(next)) {
        setSelectedTargetObjectIds(next);
      }
      return;
    }
    const next = selectedTargetObjectIds.filter((id) => {
      const obj = gameState?.objects.find((entry) => entry.id === id);
      if (!obj) return false;
      if (targetHints.objectFilter === 'opponent') {
        if (currentPriority !== null && obj.controller_id === currentPriority) return false;
      }
      if (targetHints.objectFilter === 'controller') {
        if (currentPriority !== null && obj.controller_id !== currentPriority) return false;
      }
      if (targetHints.objectTypes.size === 0) return true;
      return obj.types.some((type) => targetHints.objectTypes.has(type));
    });
    if (!isSameSelection(next)) {
      setSelectedTargetObjectIds(next);
    }
  }, [currentPriority, gameState, selectedTargetObjectIds, shouldUseStackTargets, stackSpellTargets, targetHints]);

  useEffect(() => {
    if (targetHints.allowPlayers) return;
    if (shouldUseStackTargets) {
      setSelectedTargetPlayerIds((prev) => (prev.length === 0 ? prev : []));
      return;
    }
    setSelectedTargetPlayerIds((prev) => (prev.length === 0 ? prev : []));
  }, [targetHints, shouldUseStackTargets]);

  useEffect(() => {
    if (!targetHints.allowPlayers) return;
    if (targetHints.playerFilter === 'any' || currentPriority === null) return;
    setSelectedTargetPlayerIds((prev) => {
      const next = prev.filter((playerId) =>
        targetHints.playerFilter === 'opponent' ? playerId !== currentPriority : playerId === currentPriority
      );
      if (next.length === prev.length && next.every((id, index) => id === prev[index])) return prev;
      return next;
    });
  }, [currentPriority, targetHints]);

  return {
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
    requiredTargets,
    distinctTargets,
    minTargets,
  };
};

