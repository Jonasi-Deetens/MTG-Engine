"use client";

import { useEffect, useMemo, useRef, useState } from 'react';
import { decks, DeckDetailResponse, DeckResponse } from '@/lib/decks';
import { abilities } from '@/lib/abilities';
import {
  engineApi,
  buildGameSnapshot,
  EngineGameStateSnapshot,
  EngineCardMap,
  EngineActionRequest,
} from '@/lib/engine';
import { deriveTargetHints } from '@/lib/targeting';
import { buildStackTargetHash } from '@/lib/stackTargets';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { PlayerZone } from '@/components/engine/PlayerZone';
import { StackView } from '@/components/engine/StackView';
import { TargetSelector } from '@/components/engine/TargetSelector';

const PLAYER_COUNT = 4;

export default function PlayPage() {
  const [deckList, setDeckList] = useState<DeckResponse[]>([]);
  const [selectedDeckIds, setSelectedDeckIds] = useState<Array<number | null>>(
    Array.from({ length: PLAYER_COUNT }, () => null)
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gameState, setGameState] = useState<EngineGameStateSnapshot | null>(null);
  const [cardMap, setCardMap] = useState<EngineCardMap>({});
  const [priorityPlayer, setPriorityPlayer] = useState<number | null>(null);
  const [selectedHandId, setSelectedHandId] = useState<string | null>(null);
  const [selectedAttackers, setSelectedAttackers] = useState<Set<string>>(new Set());
  const [selectedBlockers, setSelectedBlockers] = useState<Record<string, Set<string>>>({});
  const [activeAttackerId, setActiveAttackerId] = useState<string | null>(null);
  const [selectedDefenderId, setSelectedDefenderId] = useState<number | null>(null);
  const [selectedBattlefieldId, setSelectedBattlefieldId] = useState<string | null>(null);
  const [selectedTargetObjectIds, setSelectedTargetObjectIds] = useState<string[]>([]);
  const [selectedTargetPlayerIds, setSelectedTargetPlayerIds] = useState<number[]>([]);
  const [abilityGraphs, setAbilityGraphs] = useState<Record<string, any>>({});
  const [preparedCast, setPreparedCast] = useState<{ objectId: string; cost: any } | null>(null);
  const [manaPayment, setManaPayment] = useState<Record<string, number>>({});
  const [manaPaymentDetail, setManaPaymentDetail] = useState<{
    hybrid_choices: string[];
    two_brid_choices: boolean[];
    phyrexian_choices: boolean[];
  }>({ hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] });
  const [autoPayMana, setAutoPayMana] = useState(true);
  const [stackTargetChecks, setStackTargetChecks] = useState<Record<number, { legal: boolean; issues: string[] }>>({});
  const stackTargetHashesRef = useRef<Record<number, string>>({});
  const [objectTargetStatus, setObjectTargetStatus] = useState<Record<string, boolean | null>>({});
  const [playerTargetStatus, setPlayerTargetStatus] = useState<Record<number, boolean | null>>({});
  const selectionTargetHashRef = useRef<string>('');
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});

  useEffect(() => {
    const loadDecks = async () => {
      try {
        const response = await decks.getDecks('Commander');
        setDeckList(response);
      } catch (err: any) {
        setError(err?.data?.detail || err?.message || 'Failed to load decks');
      }
    };
    loadDecks();
  }, []);

  useEffect(() => {
    if (!gameState) return;
    if (gameState.replacement_choices) {
      setReplacementChoices(gameState.replacement_choices);
    }
    setSelectedHandId(null);
    setSelectedAttackers(new Set());
    setSelectedBlockers({});
    setActiveAttackerId(null);
    setSelectedBattlefieldId(null);
    setSelectedTargetObjectIds([]);
    setSelectedTargetPlayerIds([]);
    if (gameState.turn.step === 'declare_attackers') {
      const activeIndex = gameState.turn.active_player_index;
      const defenderIndex = (activeIndex + 1) % gameState.players.length;
      setSelectedDefenderId(gameState.players[defenderIndex]?.id ?? null);
    }
    if (gameState.turn.step === 'declare_blockers') {
      setActiveAttackerId(gameState.turn.combat_state?.attackers[0] ?? null);
    }
  }, [gameState?.turn.step, gameState?.turn.turn_number]);

  useEffect(() => {
    setPreparedCast(null);
    setManaPayment({});
    setManaPaymentDetail({ hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] });
    setAutoPayMana(true);
  }, [selectedHandId]);

  useEffect(() => {
    checkStackTargets();
  }, [gameState?.stack]);

  const replacementConflicts = useMemo(() => {
    if (!gameState) return [];
    const globalEffects = (gameState.replacement_effects ?? []).filter(
      (effect) => effect?.type === 'replace_zone_change'
    );
    const zoneLabels: Record<string, string> = {
      battlefield: 'Battlefield',
      graveyard: 'Graveyard',
      hand: 'Hand',
      library: 'Library',
      exile: 'Exile',
      command: 'Command',
      stack: 'Stack',
    };
    const getZoneLabel = (zone?: string) => (zone ? zoneLabels[zone] ?? zone : 'Any');
    return gameState.objects
      .map((obj) => {
        const localEffects = (obj as any).temporary_effects || [];
        const all = [...localEffects, ...globalEffects].filter((effect) => {
          if (effect?.type !== 'replace_zone_change') return false;
          if (effect.object_id && effect.object_id !== obj.id) return false;
          if (!effect.from_zone || !effect.to_zone) return false;
          return true;
        });
        if (all.length < 2) return null;
        const byKey = new Map<string, { key: string; fromZone: string; toZone: string; options: any[] }>();
        all.forEach((effect) => {
          const fromZone = effect.from_zone;
          const toZone = effect.to_zone;
          const key = `${obj.id}:${fromZone}:${toZone}`;
          const entry = byKey.get(key) || { key, fromZone, toZone, options: [] };
          entry.options.push(effect);
          byKey.set(key, entry);
        });
        return Array.from(byKey.values()).map((entry) => ({
          obj,
          key: entry.key,
          fromZone: entry.fromZone,
          toZone: entry.toZone,
          fromLabel: getZoneLabel(entry.fromZone),
          toLabel: getZoneLabel(entry.toZone),
          options: entry.options,
        }));
      })
      .flat()
      .filter(Boolean) as Array<{
        obj: any;
        key: string;
        fromZone: string;
        toZone: string;
        fromLabel: string;
        toLabel: string;
        options: Array<Record<string, any>>;
      }>;
  }, [gameState]);

  useEffect(() => {
    if (!gameState) return;
    const cardIdsToFetch = Array.from(
      new Set(
        gameState.objects
          .filter((obj) => obj.zone === 'battlefield' || obj.zone === 'command')
          .map((obj) => cardMap[obj.id]?.card_id)
          .filter((cardId): cardId is string => Boolean(cardId))
      )
    ).filter((cardId) => !abilityGraphs[cardId]);

    if (cardIdsToFetch.length === 0) return;

    const loadGraphs = async () => {
      try {
        const response = await abilities.getCardGraphs(cardIdsToFetch);
        const graphsByCardId = response.graphs.reduce<Record<string, any>>((acc, graph) => {
          acc[graph.card_id] = graph.ability_graph;
          return acc;
        }, {});
        applyAbilityGraphsToState(graphsByCardId);
      } catch (err: any) {
        if (err?.status !== 404) {
          console.error('Failed to bulk load ability graphs:', err);
        }
      }
    };

    loadGraphs();
  }, [gameState, abilityGraphs, cardMap]);

  const canStart = useMemo(() => {
    if (selectedDeckIds.some((id) => id === null)) {
      return false;
    }
    return selectedDeckIds.every((id) => {
      const deck = deckList.find((entry) => entry.id === id);
      return deck?.format === 'Commander' && deck.commander_count > 0;
    });
  }, [selectedDeckIds, deckList]);

  const handleSelectDeck = (index: number, value: string) => {
    const next = [...selectedDeckIds];
    next[index] = value ? parseInt(value, 10) : null;
    setSelectedDeckIds(next);
  };

  const startGame = async () => {
    setLoading(true);
    setError(null);
    try {
      const deckDetails: DeckDetailResponse[] = [];
      for (const deckId of selectedDeckIds) {
        if (deckId === null) {
          throw new Error('Please select a deck for each player.');
        }
        const detail = await decks.getDeck(deckId);
        if (detail.format !== 'Commander' || detail.commander_count < 1) {
          throw new Error(`Deck "${detail.name}" is not a valid Commander deck.`);
        }
        deckDetails.push(detail);
      }

      const { snapshot, cardMap: newCardMap } = buildGameSnapshot(deckDetails);
      setCardMap(newCardMap);
      const response = await engineApi.execute({
        action: 'advance_turn',
        game_state: snapshot,
      });
      setGameState(response.game_state);
      if (typeof response.result?.current_priority === 'number') {
        setPriorityPlayer(response.result.current_priority);
      } else if (typeof response.game_state.turn.priority_current_index === 'number') {
        setPriorityPlayer(response.game_state.turn.priority_current_index);
      } else {
        setPriorityPlayer(response.game_state.turn.active_player_index);
      }
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Failed to start game');
    } finally {
      setLoading(false);
    }
  };

  const runEngineAction = async (
    action: EngineActionRequest['action'],
    payload: Partial<EngineActionRequest> = {}
  ) => {
    if (!gameState) return;
    setLoading(true);
    setError(null);
    try {
      const response = await engineApi.execute({
        action,
        game_state: { ...gameState, replacement_choices: replacementChoices },
        ...payload,
      });
      setGameState(response.game_state);
      if (typeof response.result?.current_priority === 'number') {
        setPriorityPlayer(response.result.current_priority);
      } else if (typeof response.game_state.turn.priority_current_index === 'number') {
        setPriorityPlayer(response.game_state.turn.priority_current_index);
      }
      return response;
    } catch (err: any) {
      setError(err?.data?.detail || err?.message || 'Engine action failed');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const checkStackTargets = async () => {
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
  };

  const buildTargetContext = (targets: Record<string, any>) => ({
    controller_id: currentPriority,
    source_id: selectedHandId ?? undefined,
    targets,
  });

  const checkSelectionTargets = async () => {
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
  };

  const currentPriority =
    gameState?.turn.priority_current_index ??
    priorityPlayer ??
    gameState?.turn.active_player_index ??
    0;
  const activePlayerIndex = gameState?.turn.active_player_index ?? 0;
  const currentStep = gameState?.turn.step ?? '';
  const isMainPhase = currentStep === 'precombat_main' || currentStep === 'postcombat_main';
  const isDeclareAttackers = currentStep === 'declare_attackers';
  const isDeclareBlockers = currentStep === 'declare_blockers';
  const isCombatDamage = currentStep === 'combat_damage';
  const combatState = gameState?.turn.combat_state;
  const defendingPlayerId = combatState?.defending_player_id ?? selectedDefenderId;
  const isPriorityActivePlayer = currentPriority === activePlayerIndex;
  const isPriorityDefender = defendingPlayerId !== null && currentPriority === defendingPlayerId;

  const applyAbilityGraphsToState = (graphsByCardId: Record<string, any>) => {
    if (Object.keys(graphsByCardId).length === 0) return;
    setAbilityGraphs((prev) => ({ ...prev, ...graphsByCardId }));
        setGameState((prevState) => {
          if (!prevState) return prevState;
          const updatedObjects = prevState.objects.map((obj) => {
            const objCardId = cardMap[obj.id]?.card_id;
        const graph = objCardId ? graphsByCardId[objCardId] : undefined;
        if (!graph) return obj;
        if (obj.ability_graphs && obj.ability_graphs.length > 0) return obj;
              return {
                ...obj,
          ability_graphs: [graph],
              };
          });
          return { ...prevState, objects: updatedObjects };
        });
  };

  const loadAbilityGraphForObject = async (objectId: string) => {
    const card = cardMap[objectId];
    const cardId = card?.card_id;
    if (!cardId || abilityGraphs[cardId]) return;
    try {
      const response = await abilities.getCardGraph(cardId);
      if (response?.ability_graph) {
        applyAbilityGraphsToState({ [cardId]: response.ability_graph });
      }
    } catch (err: any) {
      if (err?.status !== 404) {
        console.error('Failed to load ability graph:', err);
      }
    }
  };

  const toggleAttacker = (objectId: string) => {
    setSelectedAttackers((prev) => {
      const next = new Set(prev);
      if (next.has(objectId)) {
        next.delete(objectId);
      } else {
        next.add(objectId);
      }
      return next;
    });
  };

  const toggleBlocker = (objectId: string) => {
    if (!activeAttackerId) return;
    setSelectedBlockers((prev) => {
      const next: Record<string, Set<string>> = { ...prev };
      const existing = next[activeAttackerId] ?? new Set<string>();
      const updated = new Set(existing);
      if (updated.has(objectId)) {
        updated.delete(objectId);
      } else {
        updated.add(objectId);
      }
      next[activeAttackerId] = updated;
      return next;
    });
  };

  const blockersPayload = Object.fromEntries(
    Object.entries(selectedBlockers).map(([attackerId, blockerSet]) => [attackerId, Array.from(blockerSet)])
  );
  const priorityPlayerState = gameState?.players.find((player) => player.id === currentPriority);
  const manaPool = priorityPlayerState?.mana_pool ?? {};
  const selectedGraph = selectedHandId ? abilityGraphs[cardMap[selectedHandId]?.card_id ?? ''] : undefined;
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

  useEffect(() => {
    checkSelectionTargets();
  }, [gameState, selectedHandId, selectedGraph, shouldUseStackTargets, filteredTargetableObjects, filteredTargetPlayers]);
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
  const hasActivatedAbility =
    selectedBattlefieldObject?.ability_graphs && selectedBattlefieldObject.ability_graphs.length > 0;

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

  const buildDefaultManaPayment = (cost: any, pool: Record<string, number>) => {
    if (!cost) return {};
    if ((cost.hybrids && cost.hybrids.length) || (cost.two_brids && cost.two_brids.length) || (cost.phyrexian && cost.phyrexian.length)) {
      return {};
    }
    const payment: Record<string, number> = {};
    const remainingPool: Record<string, number> = { ...pool };

    Object.entries(cost.colored ?? {}).forEach(([color, amount]) => {
      const available = remainingPool[color] ?? 0;
      const spend = Math.min(available, Number(amount) || 0);
      if (spend > 0) {
        payment[color] = spend;
        remainingPool[color] = available - spend;
      }
    });

    if (cost.colorless) {
      const available = remainingPool.C ?? 0;
      const spend = Math.min(available, Number(cost.colorless) || 0);
      if (spend > 0) {
        payment.C = (payment.C ?? 0) + spend;
        remainingPool.C = available - spend;
      }
    }

    let genericRemaining = Number(cost.generic) || 0;
    Object.entries(remainingPool).forEach(([color, amount]) => {
      if (genericRemaining <= 0) return;
      const spend = Math.min(amount, genericRemaining);
      if (spend > 0) {
        payment[color] = (payment[color] ?? 0) + spend;
        genericRemaining -= spend;
      }
    });

    return payment;
  };

  const buildDefaultPaymentDetail = (cost: any, pool: Record<string, number>) => {
    const hybrid_choices =
      cost?.hybrids?.map(([colorA, colorB]: [string, string]) =>
        (pool[colorA] ?? 0) > 0 ? colorA : colorB
      ) ?? [];
    const two_brid_choices =
      cost?.two_brids?.map(([_genericValue, color]: [number, string]) => (pool[color] ?? 0) > 0) ?? [];
    const phyrexian_choices =
      cost?.phyrexian?.map((color: string) => (pool[color] ?? 0) === 0) ?? [];
    return { hybrid_choices, two_brid_choices, phyrexian_choices };
  };

  const buildPaymentFromDetail = (
    cost: any,
    pool: Record<string, number>,
    detail: { hybrid_choices: string[]; two_brid_choices: boolean[]; phyrexian_choices: boolean[] }
  ) => {
    if (!cost) return { payment: {}, errors: [] as string[] };
    const errors: string[] = [];
    const payment: Record<string, number> = {};
    const remainingPool: Record<string, number> = { ...pool };

    const colored = cost.colored ?? {};
    Object.entries(colored).forEach(([color, amount]) => {
      const available = remainingPool[color] ?? 0;
      const required = Number(amount) || 0;
      if (available < required) {
        errors.push(`Missing required ${color} mana.`);
        return;
      }
      if (required > 0) {
        payment[color] = (payment[color] ?? 0) + required;
        remainingPool[color] = available - required;
      }
    });

    (cost.hybrids ?? []).forEach(([colorA, colorB]: [string, string], index: number) => {
      const choice = detail.hybrid_choices[index];
      if (choice !== colorA && choice !== colorB) {
        errors.push('Invalid hybrid choice.');
        return;
      }
      const available = remainingPool[choice] ?? 0;
      if (available <= 0) {
        errors.push(`Not enough ${choice} mana for hybrid cost.`);
        return;
      }
      payment[choice] = (payment[choice] ?? 0) + 1;
      remainingPool[choice] = available - 1;
    });

    let genericRequired = Number(cost.generic) || 0;

    (cost.two_brids ?? []).forEach(([genericValue, color]: [number, string], index: number) => {
      const payColor = detail.two_brid_choices[index];
      if (payColor) {
        const available = remainingPool[color] ?? 0;
        if (available <= 0) {
          errors.push(`Not enough ${color} mana for two-brid cost.`);
          return;
        }
        payment[color] = (payment[color] ?? 0) + 1;
        remainingPool[color] = available - 1;
      } else {
        genericRequired += Number(genericValue) || 0;
      }
    });

    (cost.phyrexian ?? []).forEach((color: string, index: number) => {
      const payLife = detail.phyrexian_choices[index];
      if (payLife) {
        return;
      }
      const available = remainingPool[color] ?? 0;
      if (available <= 0) {
        errors.push(`Not enough ${color} mana for phyrexian cost.`);
        return;
      }
      payment[color] = (payment[color] ?? 0) + 1;
      remainingPool[color] = available - 1;
    });

    const colorlessRequired = Number(cost.colorless) || 0;
    const availableColorless = remainingPool.C ?? 0;
    if (availableColorless < colorlessRequired) {
      errors.push('Missing required colorless mana.');
    } else if (colorlessRequired > 0) {
      payment.C = (payment.C ?? 0) + colorlessRequired;
      remainingPool.C = availableColorless - colorlessRequired;
    }

    Object.entries(remainingPool).forEach(([color, amount]) => {
      if (genericRequired <= 0) return;
      const spend = Math.min(amount, genericRequired);
      if (spend > 0) {
        payment[color] = (payment[color] ?? 0) + spend;
        genericRequired -= spend;
      }
    });

    if (genericRequired > 0) {
      errors.push('Not enough mana selected to cover the cost.');
    }

    return { payment, errors };
  };

  const buildCastContext = () => ({
    controller_id: currentPriority,
    source_id: selectedHandId ?? undefined,
    targets: {
      ...(selectedTargetObjectIds.length > 0 ? { target: selectedTargetObjectIds[0] } : {}),
      ...(selectedTargetObjectIds.length > 0
        ? { targets: selectedTargetObjectIds.slice(0, targetHints.maxObjectTargets ?? selectedTargetObjectIds.length) }
        : {}),
      ...(selectedTargetPlayerIds.length > 0 ? { target_player: selectedTargetPlayerIds[0] } : {}),
      ...(selectedTargetPlayerIds.length > 0
        ? { target_players: selectedTargetPlayerIds.slice(0, targetHints.maxPlayerTargets ?? selectedTargetPlayerIds.length) }
        : {}),
      ...(selectedTargetObjectIds.length > 0 ? { spell_target: selectedTargetObjectIds[0] } : {}),
      ...(selectedTargetObjectIds.length > 0
        ? { spell_targets: selectedTargetObjectIds.slice(0, targetHints.maxObjectTargets ?? selectedTargetObjectIds.length) }
        : {}),
    },
  });

  const handlePrepareCast = async () => {
    if (!selectedHandId) return;
    const response = await runEngineAction('prepare_cast', {
      player_id: currentPriority,
      object_id: selectedHandId,
      ability_graph: abilityGraphs[cardMap[selectedHandId]?.card_id ?? ''],
      context: buildCastContext(),
    });
    const cost = response?.result?.cost;
    if (cost) {
      setPreparedCast({ objectId: selectedHandId, cost });
      const detail = buildDefaultPaymentDetail(cost, manaPool);
      setManaPaymentDetail(detail);
      if ((cost.hybrids && cost.hybrids.length) || (cost.two_brids && cost.two_brids.length) || (cost.phyrexian && cost.phyrexian.length)) {
        const { payment } = buildPaymentFromDetail(cost, manaPool, detail);
        setManaPayment(payment);
      } else {
        setManaPayment(buildDefaultManaPayment(cost, manaPool));
      }
      setAutoPayMana(true);
    }
  };

  const handleFinalizeCast = async () => {
    if (!selectedHandId || !preparedCast || preparedCast.objectId !== selectedHandId) return;
    const response = await runEngineAction('finalize_cast', {
      player_id: currentPriority,
      object_id: selectedHandId,
      ability_graph: abilityGraphs[cardMap[selectedHandId]?.card_id ?? ''],
      context: buildCastContext(),
      mana_payment: Object.keys(manaPayment).length > 0 ? manaPayment : undefined,
      mana_payment_detail: isComplexCost ? manaPaymentDetail : undefined,
    });
    if (response?.result?.status === 'spell_cast') {
      setPreparedCast(null);
      setManaPayment({});
      setAutoPayMana(true);
    }
  };

  const getManaPaymentErrors = (cost: any, payment: Record<string, number>, pool: Record<string, number>) => {
    if (!cost) return { errors: [] as string[], totalRequired: 0 };
    if ((cost.hybrids && cost.hybrids.length) || (cost.two_brids && cost.two_brids.length) || (cost.phyrexian && cost.phyrexian.length)) {
      return { errors: ['Hybrid/phyrexian costs require auto-pay.'], totalRequired: 0 };
    }
    const errors: string[] = [];
    const totalRequired =
      (Number(cost.generic) || 0) + (Number(cost.colorless) || 0) + Object.values(cost.colored ?? {}).reduce((sum: number, amount: any) => sum + Number(amount || 0), 0);
    const totalPaid = Object.values(payment).reduce((sum, amount) => sum + (Number(amount) || 0), 0);
    if (totalPaid < totalRequired) {
      errors.push('Not enough mana selected to cover the cost.');
    }
    Object.entries(cost.colored ?? {}).forEach(([color, amount]) => {
      if ((payment[color] ?? 0) < Number(amount || 0)) {
        errors.push(`Missing required ${color} mana.`);
      }
    });
    if ((payment.C ?? 0) < Number(cost.colorless || 0)) {
      errors.push('Missing required colorless mana.');
    }
    Object.entries(payment).forEach(([color, amount]) => {
      if ((pool[color] ?? 0) < Number(amount || 0)) {
        errors.push(`Overpaid ${color} mana (exceeds pool).`);
      }
    });
    return { errors, totalRequired };
  };

  const isComplexCost = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedHandId) return false;
    const cost = preparedCast.cost;
    return Boolean(
      (cost.hybrids && cost.hybrids.length) ||
        (cost.two_brids && cost.two_brids.length) ||
        (cost.phyrexian && cost.phyrexian.length)
    );
  }, [preparedCast, selectedHandId]);

  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedHandId) return;
    if (!autoPayMana) return;
    if (isComplexCost) {
      const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      setManaPayment(payment);
      return;
    }
    setManaPayment(buildDefaultManaPayment(preparedCast.cost, manaPool));
  }, [autoPayMana, isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedHandId]);

  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedHandId) return;
    if (!isComplexCost) return;
    const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
    setManaPayment(payment);
  }, [isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedHandId]);

  const manaPaymentStatus = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedHandId) {
      return { errors: [] as string[], totalRequired: 0 };
    }
    if (isComplexCost) {
      const { errors } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      return { errors, totalRequired: 0 };
    }
    return getManaPaymentErrors(preparedCast.cost, manaPayment, manaPool);
  }, [preparedCast, selectedHandId, manaPayment, manaPool, isComplexCost, manaPaymentDetail]);

  const costLabel = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedHandId) return '';
    const cost = preparedCast.cost;
    const parts: string[] = [];
    if (cost.colored) {
      Object.entries(cost.colored).forEach(([color, amount]) => {
        const count = Number(amount || 0);
        if (count > 0) parts.push(`${count}${color}`);
      });
    }
    if (cost.colorless) parts.push(`${cost.colorless}C`);
    if (cost.generic) parts.push(`${cost.generic}`);
    if ((cost.hybrids && cost.hybrids.length) || (cost.two_brids && cost.two_brids.length) || (cost.phyrexian && cost.phyrexian.length)) {
      parts.push('hybrid/phyrexian');
    }
    return parts.join(' + ') || '0';
  }, [preparedCast, selectedHandId]);

  useEffect(() => {
    if (!isComplexCost) return;
    setAutoPayMana(true);
  }, [isComplexCost]);

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
        <Card variant="bordered" className="p-4 space-y-4">
          <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
            Select decks for each player
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {selectedDeckIds.map((deckId, index) => (
              <div key={`player-${index}`} className="space-y-2">
                <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">
                  Player {index + 1}
                </div>
                <select
                  value={deckId ?? ''}
                  onChange={(e) => handleSelectDeck(index, e.target.value)}
                  className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                  <option value="">Select Commander deck...</option>
                  {deckList.map((deck) => (
                    <option key={deck.id} value={deck.id}>
                      {deck.name}
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
          <div className="flex justify-end">
            <Button variant="primary" onClick={startGame} disabled={!canStart || loading}>
              {loading ? 'Starting...' : 'Start Game'}
            </Button>
          </div>
        </Card>
      )}

      {gameState && (
        <div className="space-y-6">
          <Card variant="bordered" className="p-4 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="text-sm text-[color:var(--theme-text-secondary)]">Turn</div>
              <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
                {gameState.turn.turn_number} · {gameState.turn.phase} / {gameState.turn.step}
              </div>
              <div className="text-xs text-[color:var(--theme-text-secondary)]">
                Active Player: {gameState.turn.active_player_index + 1}
                {typeof currentPriority === 'number' && ` · Priority: ${currentPriority + 1}`}
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => runEngineAction('pass_priority', { player_id: currentPriority })}
                disabled={loading}
              >
                Pass Priority
              </Button>
              <Button variant="primary" onClick={() => runEngineAction('advance_turn')} disabled={loading}>
                Advance Step
              </Button>
            </div>
          </Card>

          <Card variant="bordered" className="p-4 space-y-4">
            <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Actions</div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                onClick={() =>
                  runEngineAction('play_land', { player_id: currentPriority, object_id: selectedHandId ?? undefined })
                }
                disabled={!selectedHandId || !isMainPhase || !isPriorityActivePlayer || loading}
              >
                Play Land
              </Button>
              <Button
                variant="outline"
                onClick={handlePrepareCast}
                disabled={!selectedHandId || loading}
              >
                Prepare Cast
              </Button>
              <Button
                variant="outline"
                onClick={handleFinalizeCast}
                disabled={
                  !preparedCast ||
                  preparedCast.objectId !== selectedHandId ||
                  manaPaymentStatus.errors.length > 0 ||
                  loading
                }
              >
                Finalize Cast
              </Button>
              <Button
                variant="outline"
                onClick={() =>
                  runEngineAction('activate_mana_ability', {
                    player_id: currentPriority,
                    object_id: selectedBattlefieldId ?? undefined,
                  })
                }
                disabled={!selectedBattlefieldId || loading}
              >
                Tap for Mana
              </Button>
              <Button
                variant="outline"
                onClick={() =>
                  runEngineAction('activate_ability', {
                    player_id: currentPriority,
                    object_id: selectedBattlefieldId ?? undefined,
                    ability_index: 0,
                  })
                }
                disabled={!selectedBattlefieldId || !hasActivatedAbility || loading}
              >
                Activate Ability
              </Button>
              <Button
                variant="outline"
                onClick={() =>
                  runEngineAction('declare_attackers', {
                    player_id: currentPriority,
                    attackers: Array.from(selectedAttackers),
                    defending_player_id: defendingPlayerId ?? undefined,
                  })
                }
                disabled={!isDeclareAttackers || !isPriorityActivePlayer || selectedAttackers.size === 0 || loading}
              >
                Declare Attackers
              </Button>
              <Button
                variant="outline"
                onClick={() =>
                  runEngineAction('declare_blockers', {
                    player_id: currentPriority,
                    blockers: blockersPayload,
                  })
                }
                disabled={!isDeclareBlockers || !isPriorityDefender || !activeAttackerId || loading}
              >
                Declare Blockers
              </Button>
              <Button
                variant="outline"
                onClick={() => runEngineAction('assign_combat_damage', { player_id: currentPriority })}
                disabled={!isCombatDamage || !isPriorityActivePlayer || loading}
              >
                Assign Combat Damage
              </Button>
            </div>

            {isDeclareAttackers && (
              <div className="flex flex-wrap gap-3">
                <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Defender</div>
                <select
                  value={defendingPlayerId ?? ''}
                  onChange={(e) => setSelectedDefenderId(e.target.value ? parseInt(e.target.value, 10) : null)}
                  className="px-3 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none text-sm"
                >
                  {gameState.players
                    .filter((player) => player.id !== activePlayerIndex)
                    .map((player) => (
                      <option key={`defender-${player.id}`} value={player.id}>
                        Player {player.id + 1}
                      </option>
                    ))}
                </select>
              </div>
            )}

            {isDeclareBlockers && combatState && (
              <div className="space-y-2">
                <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Select Attacker</div>
                <div className="flex flex-wrap gap-2">
                  {combatState.attackers.map((attackerId) => (
                    <Button
                      key={`attacker-${attackerId}`}
                      variant={activeAttackerId === attackerId ? 'primary' : 'outline'}
                      size="sm"
                      onClick={() => setActiveAttackerId(attackerId)}
                    >
                      {cardMap[attackerId]?.name || attackerId}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {preparedCast && preparedCast.objectId === selectedHandId && (
              <div className="space-y-2">
                <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Mana Payment</div>
                <label className="flex items-center gap-2 text-xs text-[color:var(--theme-text-secondary)]">
                  <input
                    type="checkbox"
                    checked={autoPayMana}
                    onChange={(e) => setAutoPayMana(e.target.checked)}
                    disabled={isComplexCost}
                  />
                  Auto-pay (use recommended payment)
                </label>
                <div className="text-xs text-[color:var(--theme-text-secondary)]">Cost: {costLabel}</div>
                {isComplexCost && (
                  <div className="text-xs text-[color:var(--theme-text-secondary)]">
                    Choose how to pay hybrid/phyrexian/two-brid symbols.
                  </div>
                )}
                {isComplexCost && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                    {(preparedCast.cost.hybrids ?? []).map(([colorA, colorB]: [string, string], index: number) => (
                      <label key={`hybrid-${index}`} className="flex items-center gap-2">
                        <span className="text-[color:var(--theme-text-secondary)]">Hybrid</span>
                <select
                          value={manaPaymentDetail.hybrid_choices[index] ?? colorA}
                          onChange={(e) =>
                            setManaPaymentDetail((prev) => {
                              const next = [...prev.hybrid_choices];
                              next[index] = e.target.value;
                              return { ...prev, hybrid_choices: next };
                            })
                          }
                          className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                >
                          <option value={colorA}>{colorA}</option>
                          <option value={colorB}>{colorB}</option>
                        </select>
                      </label>
                    ))}
                    {(preparedCast.cost.two_brids ?? []).map(
                      ([genericValue, color]: [number, string], index: number) => (
                        <label key={`two-brid-${index}`} className="flex items-center gap-2">
                          <span className="text-[color:var(--theme-text-secondary)]">Two-brid</span>
                          <select
                            value={manaPaymentDetail.two_brid_choices[index] ? 'color' : 'generic'}
                            onChange={(e) =>
                              setManaPaymentDetail((prev) => {
                                const next = [...prev.two_brid_choices];
                                next[index] = e.target.value === 'color';
                                return { ...prev, two_brid_choices: next };
                              })
                            }
                            className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                          >
                            <option value="color">{color}</option>
                            <option value="generic">{genericValue} generic</option>
                </select>
                        </label>
                      )
                    )}
                    {(preparedCast.cost.phyrexian ?? []).map((color: string, index: number) => (
                      <label key={`phyrexian-${index}`} className="flex items-center gap-2">
                        <span className="text-[color:var(--theme-text-secondary)]">Phyrexian</span>
                        <select
                          value={manaPaymentDetail.phyrexian_choices[index] ? 'life' : 'mana'}
                          onChange={(e) =>
                            setManaPaymentDetail((prev) => {
                              const next = [...prev.phyrexian_choices];
                              next[index] = e.target.value === 'life';
                              return { ...prev, phyrexian_choices: next };
                            })
                          }
                          className="flex-1 px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                        >
                          <option value="mana">{color} mana</option>
                          <option value="life">2 life</option>
                        </select>
                      </label>
                    ))}
              </div>
                )}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                  {['W', 'U', 'B', 'R', 'G', 'C'].map((color) => (
                    <label key={`mana-${color}`} className="flex items-center gap-2">
                      <span className="w-4 text-[color:var(--theme-text-secondary)]">{color}</span>
                      <input
                        type="number"
                        min={0}
                        max={manaPool[color] ?? 0}
                        value={manaPayment[color] ?? 0}
                        onChange={(e) =>
                          setManaPayment((prev) => ({
                            ...prev,
                            [color]: Math.max(0, parseInt(e.target.value || '0', 10)),
                          }))
                        }
                        disabled={autoPayMana || isComplexCost}
                        className="w-full px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                      />
                      <span className="text-[color:var(--theme-text-secondary)] text-xs">
                        / {manaPool[color] ?? 0}
                      </span>
                    </label>
                  ))}
                </div>
                {manaPaymentStatus.errors.length > 0 && (
                  <div className="text-xs text-[color:var(--theme-status-error)]">
                    {manaPaymentStatus.errors.join(' ')}
                  </div>
                )}
              </div>
            )}

            <TargetSelector
              objects={shouldUseStackTargets ? stackSpellObjects : filteredTargetableObjects}
              players={shouldUseStackTargets ? [] : filteredTargetPlayers}
              cardMap={cardMap}
              selectedObjectIds={selectedTargetObjectIds}
              selectedPlayerIds={selectedTargetPlayerIds}
              objectLabel={shouldUseStackTargets ? 'Spells on Stack' : 'Objects'}
              playerLabel="Players"
              maxObjectTargets={targetHints.maxObjectTargets}
              maxPlayerTargets={targetHints.maxPlayerTargets}
              objectTargetStatus={objectTargetStatus}
              playerTargetStatus={playerTargetStatus}
              onChangeObjects={setSelectedTargetObjectIds}
              onChangePlayers={setSelectedTargetPlayerIds}
              onClear={() => {
                setSelectedTargetObjectIds([]);
                setSelectedTargetPlayerIds([]);
              }}
            />
          </Card>

          {replacementConflicts.some((entry) => !replacementChoices[entry.key]) && (
            <Card variant="bordered" className="p-4 space-y-3">
              <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
                Replacement Choice Needed
              </div>
              <div className="text-xs text-[color:var(--theme-text-secondary)]">
                A zone change has multiple applicable replacements. Choose the one to apply before it happens.
              </div>
              <div className="space-y-2">
                {replacementConflicts.filter((entry) => !replacementChoices[entry.key]).map((entry) => (
                  <div key={entry.key} className="flex flex-wrap items-center gap-2">
                    <div className="text-xs text-[color:var(--theme-text-secondary)]">
                      {cardMap[entry.obj.id]?.name || entry.obj.name || entry.obj.id}
                      <span className="ml-1 text-[color:var(--theme-text-muted)]">
                        ({entry.fromLabel} → {entry.toLabel})
                      </span>
                    </div>
                <select
                      value={replacementChoices[entry.key] || ''}
                      onChange={(e) =>
                        setReplacementChoices((prev) => ({
                          ...prev,
                          [entry.key]: e.target.value,
                        }))
                      }
                      className="px-2 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none text-xs"
                >
                      <option value="">Auto (most recent)</option>
                      {entry.options.map((effect) => (
                        <option key={effect.effect_id} value={effect.effect_id}>
                          {effect.replacement_zone}
                    </option>
                  ))}
                </select>
              </div>
                ))}
            </div>
          </Card>
          )}

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
