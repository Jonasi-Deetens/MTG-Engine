import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { engineApi, EngineActionRequest, EngineGameStateSnapshot } from '@/lib/engine';
import { deriveTargetHints } from '@/lib/targeting';
import { buildStackTargetHash } from '@/lib/stackTargets';

interface UseTargetingArgs {
  gameState: EngineGameStateSnapshot | null;
  selectedHandId: string | null;
  selectedGraph: any;
  currentPriority: number | null;
}

export const useTargeting = ({
  gameState,
  selectedHandId,
  selectedGraph,
  currentPriority,
}: UseTargetingArgs) => {
  const [selectedTargetObjectIds, setSelectedTargetObjectIds] = useState<string[]>([]);
  const [selectedTargetPlayerIds, setSelectedTargetPlayerIds] = useState<number[]>([]);
  const [objectTargetStatus, setObjectTargetStatus] = useState<Record<string, boolean | null>>({});
  const [playerTargetStatus, setPlayerTargetStatus] = useState<Record<number, boolean | null>>({});
  const [stackTargetChecks, setStackTargetChecks] = useState<Record<number, { legal: boolean; issues: string[] }>>({});
  const stackTargetHashesRef = useRef<Record<number, string>>({});
  const selectionTargetHashRef = useRef<string>('');

  const targetHints = useMemo(() => deriveTargetHints(selectedGraph), [selectedGraph]);
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
        if (targetHints.objectTypes.size === 0) return true;
        return obj.types.some((type) => targetHints.objectTypes.has(type));
      })
    : [];
  const filteredTargetPlayers = targetHints.allowPlayers ? gameState?.players ?? [] : [];
  const shouldUseStackTargets = selectedGraph?.nodes?.some(
    (node: any) => node?.type === 'EFFECT' && node?.data?.target === 'spell'
  );

  const buildTargetContext = useCallback(
    (targets: Record<string, any>) => ({
      controller_id: currentPriority,
      source_id: selectedHandId ?? undefined,
      targets,
    }),
    [currentPriority, selectedHandId]
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
    if (!targetHints.allowObjects) {
      setSelectedTargetObjectIds([]);
      return;
    }
    if (shouldUseStackTargets) {
      setSelectedTargetObjectIds((prev) => prev.filter((id) => stackSpellTargets.includes(id)));
      return;
    }
    if (targetHints.objectTypes.size === 0) return;
    setSelectedTargetObjectIds((prev) =>
      prev.filter((id) => {
        const obj = gameState?.objects.find((entry) => entry.id === id);
        return obj ? obj.types.some((type) => targetHints.objectTypes.has(type)) : false;
      })
    );
  }, [gameState, targetHints, shouldUseStackTargets, stackSpellTargets]);

  useEffect(() => {
    if (targetHints.allowPlayers) return;
    if (shouldUseStackTargets) {
      setSelectedTargetPlayerIds([]);
      return;
    }
    setSelectedTargetPlayerIds([]);
  }, [targetHints, shouldUseStackTargets]);

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
  };
};

