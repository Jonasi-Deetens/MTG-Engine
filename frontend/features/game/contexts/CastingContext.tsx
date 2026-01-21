'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap, EngineActionRequest } from '@/lib/engine';
import {
  buildDefaultManaPayment,
  buildDefaultPaymentDetail,
  buildPaymentFromDetail,
  getManaPaymentErrors,
  hasComplexManaCost,
  ManaPaymentDetail,
} from '@/lib/manaPayment';
import {
  deriveAdditionalCostsFromGraph,
  deriveAlternativeCastCostsFromGraph,
  deriveAlternativeExtraCostsFromGraph,
  deriveOptionalCastCostsFromGraph,
  deriveSpliceCardsFromHand,
  AlternativeCostOption,
  OptionalCastCostOption,
} from '@/lib/graphCosts';
import { useActivationCosts, ActivationCostEntry } from '@/hooks/useActivationCosts';

/**
 * CastingContext - Spell casting flow management
 * 
 * Responsible for:
 * - Spell preparation and finalization
 * - Mana payment (including complex costs)
 * - Additional/alternative/optional costs
 * - Activation costs for abilities
 * - Conspire, splice, and other special costs
 */

export interface CastingContextValue {
  // Core casting state
  preparedCast: { objectId: string; cost: any } | null;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  autoPayMana: boolean;
  isComplexCost: boolean;
  costLabel: string;
  manaPaymentErrors: string[];
  
  // Alternative/optional costs
  selectedAlternativeCostTag: string | null;
  alternativeCostOptions: AlternativeCostOption[];
  alternativeExtraCostOptions: any[];
  alternativeExtraCostEntries: ActivationCostEntry[];
  alternativeExtraPayments: any[];
  alternativeExtraPaymentDetails: Record<number, ManaPaymentDetail>;
  alternativeExtraCostErrors: string[];
  hasAlternativeExtraCostErrors: boolean;
  
  // Optional costs (kicker, buyback, etc.)
  optionalCostOptions: OptionalCastCostOption[];
  optionalCostSelections: Record<string, number>;
  optionalCostEntries: ActivationCostEntry[];
  optionalCostPayments: any[];
  optionalCostPaymentDetails: Record<number, ManaPaymentDetail>;
  optionalCostErrors: string[];
  hasOptionalCostErrors: boolean;
  optionalCopyCount: number;
  
  // Conspire
  conspireSelected: boolean;
  conspireOptions: Array<{ value: string; label: string }>;
  conspireTaps: string[];
  conspireError: string | null;
  
  // Splice
  isArcaneSpell: boolean;
  spliceOptions: Array<{ cardId: string; costs: any[]; label: string }>;
  spliceSelections: string[];
  spliceCosts: ActivationCostEntry[];
  splicePayments: any[];
  splicePaymentDetails: Record<number, ManaPaymentDetail>;
  spliceCostErrors: string[];
  
  // Additional costs
  additionalCastCosts: ActivationCostEntry[];
  additionalCastPayments: any[];
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  hasAdditionalCastCostErrors: boolean;
  
  // Activation costs (for activated abilities)
  activationCosts: ActivationCostEntry[];
  activationPayments: any[];
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  hasActivationCostErrors: boolean;
  
  // Copy spell
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
  
  // Actions
  setManaPayment: (payment: Record<string, number>) => void;
  setManaPaymentDetail: (detail: ManaPaymentDetail) => void;
  setAutoPayMana: (auto: boolean) => void;
  setSelectedAlternativeCostTag: (tag: string | null) => void;
  handleToggleOptionalCost: (tag: string) => void;
  handleUpdateOptionalCostCount: (tag: string, count: number) => void;
  handleToggleConspireTap: (value: string) => void;
  handleToggleSpliceCard: (cardId: string) => void;
  setOptionalCostPayments: (payments: any[]) => void;
  setOptionalCostPaymentDetails: (details: Record<number, ManaPaymentDetail>) => void;
  setAlternativeExtraPayments: (payments: any[]) => void;
  setAlternativeExtraPaymentDetails: (details: Record<number, ManaPaymentDetail>) => void;
  setAdditionalCastPayments: (payments: any[]) => void;
  setAdditionalCastPaymentDetails: (details: Record<number, ManaPaymentDetail>) => void;
  setActivationPayments: (payments: any[]) => void;
  setActivationPaymentDetails: (details: Record<number, ManaPaymentDetail>) => void;
  setSplicePayments: (payments: any[]) => void;
  setSplicePaymentDetails: (details: Record<number, ManaPaymentDetail>) => void;
  handlePrepareCast: () => Promise<void>;
  handleFinalizeCast: () => Promise<void>;
}

interface CastingProviderProps {
  children: React.ReactNode;
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  selectedGraph: any;
  abilityGraphs: Record<string, any>;
  buildCastContext: (
    sourceIdOverride?: string | null,
    wardOptions?: {
      wardAutoPay?: boolean;
      wardPayments?: Record<string, any>;
      additionalCostPayments?: any;
      alternativeCostTag?: string | null;
      alternativeCostPayments?: any;
    }
  ) => EngineActionRequest['context'];
  wardPaymentsPayload: Record<string, any>;
  autoPayWard: boolean;
  runEngineAction: (action: string, payload?: Record<string, any>) => Promise<any>;
  loadAbilityGraphForObject: (objectId: string) => void;
}

const CastingContext = createContext<CastingContextValue | null>(null);

export function CastingProvider({
  children,
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedCommandId,
  selectedBattlefieldId,
  selectedGraph,
  abilityGraphs,
  buildCastContext,
  wardPaymentsPayload,
  autoPayWard,
  runEngineAction,
  loadAbilityGraphForObject,
}: CastingProviderProps) {
  const value = useCastingInternal({
    gameState,
    cardMap,
    priorityPlayer,
    selectedHandId,
    selectedCommandId,
    selectedBattlefieldId,
    selectedGraph,
    abilityGraphs,
    buildCastContext,
    wardPaymentsPayload,
    autoPayWard,
    runEngineAction,
    loadAbilityGraphForObject,
  });
  return <CastingContext.Provider value={value}>{children}</CastingContext.Provider>;
}

export function useCasting() {
  const context = useContext(CastingContext);
  if (!context) {
    throw new Error('useCasting must be used within CastingProvider');
  }
  return context;
}

interface UseCastingInternalArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  selectedGraph: any;
  abilityGraphs: Record<string, any>;
  buildCastContext: (
    sourceIdOverride?: string | null,
    wardOptions?: any
  ) => EngineActionRequest['context'];
  wardPaymentsPayload: Record<string, any>;
  autoPayWard: boolean;
  runEngineAction: (action: string, payload?: Record<string, any>) => Promise<any>;
  loadAbilityGraphForObject: (objectId: string) => void;
}

function useCastingInternal({
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedCommandId,
  selectedBattlefieldId,
  selectedGraph,
  abilityGraphs,
  buildCastContext,
  wardPaymentsPayload,
  autoPayWard,
  runEngineAction,
  loadAbilityGraphForObject,
}: UseCastingInternalArgs): CastingContextValue {
  const selectedCastId = selectedCommandId ?? selectedHandId;
  const manaPool = gameState?.players.find((p) => p.id === priorityPlayer)?.mana_pool ?? {};

  const objectMap = useMemo(
    () => new Map(gameState?.objects.map((obj) => [obj.id, obj]) ?? []),
    [gameState?.objects]
  );

  // Core casting state
  const [preparedCast, setPreparedCast] = useState<{ objectId: string; cost: any } | null>(null);
  const [manaPayment, setManaPayment] = useState<Record<string, number>>({});
  const [manaPaymentDetail, setManaPaymentDetail] = useState<ManaPaymentDetail>({
    hybrid_choices: [],
    two_brid_choices: [],
    phyrexian_choices: [],
  });
  const [autoPayMana, setAutoPayMana] = useState(true);
  const [selectedAlternativeCostTag, setSelectedAlternativeCostTag] = useState<string | null>(null);
  const [optionalCostSelections, setOptionalCostSelections] = useState<Record<string, number>>({});
  const [conspireTaps, setConspireTaps] = useState<string[]>([]);
  const [spliceSelections, setSpliceSelections] = useState<string[]>([]);

  // Reset on selection change
  useEffect(() => {
    setPreparedCast(null);
    setManaPayment({});
    setManaPaymentDetail({ hybrid_choices: [], two_brid_choices: [], phyrexian_choices: [] });
    setAutoPayMana(true);
  }, [selectedCastId]);

  useEffect(() => {
    setSelectedAlternativeCostTag(null);
  }, [selectedHandId]);

  // Derive costs from graph
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

  const additionalCosts = useMemo(
    () => deriveAdditionalCostsFromGraph(selectedGraph),
    [selectedGraph]
  );

  // Reset optional cost selections when options change
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

  // Calculate optional cost costs
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

  // Copy count from optional costs (replicate, conspire)
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

  const copyTargetsEnabled = useMemo(
    () => copySpellConfig.enabled || optionalCopyCount > 0,
    [copySpellConfig.enabled, optionalCopyCount]
  );

  const copyTargetsCount = useMemo(
    () => (copySpellConfig.enabled ? copySpellConfig.amount : 0) + optionalCopyCount,
    [copySpellConfig.amount, copySpellConfig.enabled, optionalCopyCount]
  );

  // Conspire handling
  const conspireSelected = useMemo(
    () => optionalCostOptions.some((option) => option.kind === 'conspire' && (optionalCostSelections[option.tag] ?? 0) > 0),
    [optionalCostOptions, optionalCostSelections]
  );

  const selectedHandObject = gameState?.objects.find((obj) => obj.id === selectedHandId);

  const conspireOptions = useMemo(() => {
    if (!conspireSelected || !selectedHandObject) return [];
    const spellColors = new Set(selectedHandObject.colors ?? []);
    if (spellColors.size === 0) return [];
    const player = gameState?.players.find((entry) => entry.id === priorityPlayer);
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
  }, [cardMap, conspireSelected, priorityPlayer, gameState, objectMap, selectedHandObject]);

  const conspireError = conspireSelected && conspireTaps.length !== 2 ? 'Select exactly two creatures.' : null;

  useEffect(() => {
    if (!conspireSelected) {
      setConspireTaps([]);
    }
  }, [conspireSelected, selectedHandId]);

  const handleToggleConspireTap = useCallback((value: string) => {
    setConspireTaps((prev) => {
      if (prev.includes(value)) {
        return prev.filter((entry) => entry !== value);
      }
      if (prev.length >= 2) {
        return prev;
      }
      return [...prev, value];
    });
  }, []);

  // Splice handling
  const isArcaneSpell = !!selectedHandObject?.types?.includes('Arcane');

  useEffect(() => {
    if (!gameState || !isArcaneSpell) return;
    const player = gameState.players.find((entry) => entry.id === priorityPlayer);
    (player?.hand ?? []).forEach((objectId) => {
      loadAbilityGraphForObject(objectId);
    });
  }, [priorityPlayer, gameState, isArcaneSpell, loadAbilityGraphForObject]);

  const spliceOptions = useMemo(() => {
    if (!isArcaneSpell || !gameState) return [];
    const player = gameState.players.find((entry) => entry.id === priorityPlayer);
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
  }, [abilityGraphs, cardMap, priorityPlayer, gameState, isArcaneSpell, objectMap]);

  useEffect(() => {
    if (!isArcaneSpell) {
      setSpliceSelections([]);
      return;
    }
    setSpliceSelections((prev) => prev.filter((id) => spliceOptions.some((entry) => entry.cardId === id)));
  }, [isArcaneSpell, selectedHandId, spliceOptions]);

  const handleToggleSpliceCard = useCallback((cardId: string) => {
    setSpliceSelections((prev) =>
      prev.includes(cardId) ? prev.filter((entry) => entry !== cardId) : [...prev, cardId]
    );
  }, []);

  const spliceCostList = useMemo(() => {
    if (spliceSelections.length === 0) return [];
    return spliceSelections.flatMap(
      (id) => spliceOptions.find((option) => option.cardId === id)?.costs ?? []
    );
  }, [spliceOptions, spliceSelections]);

  // Activation costs hooks
  const selectedBattlefieldObject = gameState?.objects.find((obj) => obj.id === selectedBattlefieldId);
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
    currentPlayerId: priorityPlayer,
    manaPool,
  });

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
    currentPlayerId: priorityPlayer,
    manaPool,
  });

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
    currentPlayerId: priorityPlayer,
    manaPool,
  });

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
    currentPlayerId: priorityPlayer,
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
    currentPlayerId: priorityPlayer,
    manaPool,
  });

  // Error flags
  const hasActivationCostErrors = activationCostErrors.length > 0;
  const hasAdditionalCastCostErrors = additionalCastCostErrors.length > 0;
  const hasAlternativeExtraCostErrors = alternativeExtraCostErrors.length > 0;
  const hasOptionalCostErrors =
    optionalCostPaymentErrors.length > 0 ||
    spliceCostErrors.length > 0 ||
    (conspireSelected && conspireTaps.length !== 2);

  // Complex cost detection
  const isComplexCost = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return false;
    return hasComplexManaCost(preparedCast.cost);
  }, [preparedCast, selectedCastId]);

  // Auto-pay mana effect
  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (!autoPayMana) return;
    if (isComplexCost) {
      const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      setManaPayment(payment);
      return;
    }
    setManaPayment(buildDefaultManaPayment(preparedCast.cost, manaPool));
  }, [autoPayMana, isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedCastId]);

  // Update payment when detail changes
  useEffect(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (!isComplexCost) return;
    const { payment } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
    setManaPayment(payment);
  }, [isComplexCost, manaPaymentDetail, manaPool, preparedCast, selectedCastId]);

  useEffect(() => {
    if (!isComplexCost) return;
    setAutoPayMana(true);
  }, [isComplexCost]);

  // Mana payment errors
  const manaPaymentStatus = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) {
      return { errors: [] as string[], totalRequired: 0 };
    }
    if (isComplexCost) {
      const { errors } = buildPaymentFromDetail(preparedCast.cost, manaPool, manaPaymentDetail);
      return { errors, totalRequired: 0 };
    }
    return getManaPaymentErrors(preparedCast.cost, manaPayment, manaPool);
  }, [preparedCast, selectedCastId, manaPayment, manaPool, isComplexCost, manaPaymentDetail]);

  // Cost label
  const costLabel = useMemo(() => {
    if (!preparedCast || preparedCast.objectId !== selectedCastId) return '';
    const cost = preparedCast.cost;
    const parts: string[] = [];
    const xCount = Number((cost as any).x_count ?? (cost as any).x ?? 0);
    if (xCount > 0) {
      parts.push(`${xCount}X`);
    }
    if (cost.colored) {
      Object.entries(cost.colored).forEach(([color, amount]) => {
        const count = Number(amount || 0);
        if (count > 0) parts.push(`${count}${color}`);
      });
    }
    if (cost.colorless) parts.push(`${cost.colorless}C`);
    if (cost.generic) parts.push(`${cost.generic}`);
    if (hasComplexManaCost(cost)) {
      parts.push('hybrid/phyrexian');
    }
    return parts.join(' + ') || '0';
  }, [preparedCast, selectedCastId]);

  // Handle optional cost toggle
  const handleToggleOptionalCost = useCallback((tag: string) => {
    setOptionalCostSelections((prev) => {
      const next = { ...prev };
      if ((next[tag] ?? 0) > 0) {
        delete next[tag];
        return next;
      }
      next[tag] = 1;
      return next;
    });
  }, []);

  const handleUpdateOptionalCostCount = useCallback((tag: string, count: number) => {
    setOptionalCostSelections((prev) => ({
      ...prev,
      [tag]: Math.max(0, count),
    }));
  }, []);

  // Prepare cast
  const handlePrepareCast = useCallback(async () => {
    if (!selectedCastId || priorityPlayer === null) return;
    const response = await runEngineAction('prepare_cast', {
      player_id: priorityPlayer,
      object_id: selectedCastId,
      ability_graph: abilityGraphs[cardMap[selectedCastId]?.card_id ?? ''],
      context: buildCastContext(selectedCastId, {
        wardAutoPay: autoPayWard,
        wardPayments: wardPaymentsPayload,
        additionalCostPayments: additionalCastPaymentsPayload,
        alternativeCostTag: selectedAlternativeCostTag,
        alternativeCostPayments: alternativeExtraPaymentsPayload,
      }),
    });
    const cost = response?.result?.cost;
    if (cost) {
      setPreparedCast({ objectId: selectedCastId, cost });
      const detail = buildDefaultPaymentDetail(cost, manaPool);
      setManaPaymentDetail(detail);
      if (hasComplexManaCost(cost)) {
        const { payment } = buildPaymentFromDetail(cost, manaPool, detail);
        setManaPayment(payment);
      } else {
        setManaPayment(buildDefaultManaPayment(cost, manaPool));
      }
      setAutoPayMana(true);
    }
  }, [
    selectedCastId,
    priorityPlayer,
    abilityGraphs,
    cardMap,
    manaPool,
    buildCastContext,
    autoPayWard,
    wardPaymentsPayload,
    additionalCastPaymentsPayload,
    selectedAlternativeCostTag,
    alternativeExtraPaymentsPayload,
    runEngineAction,
  ]);

  // Finalize cast
  const handleFinalizeCast = useCallback(async () => {
    if (!selectedCastId || !preparedCast || preparedCast.objectId !== selectedCastId) return;
    if (priorityPlayer === null) return;
    const response = await runEngineAction('finalize_cast', {
      player_id: priorityPlayer,
      object_id: selectedCastId,
      ability_graph: abilityGraphs[cardMap[selectedCastId]?.card_id ?? ''],
      context: buildCastContext(selectedCastId, {
        wardAutoPay: autoPayWard,
        wardPayments: wardPaymentsPayload,
        additionalCostPayments: additionalCastPaymentsPayload,
        alternativeCostTag: selectedAlternativeCostTag,
        alternativeCostPayments: alternativeExtraPaymentsPayload,
      }),
      mana_payment: Object.keys(manaPayment).length > 0 ? manaPayment : undefined,
      mana_payment_detail: isComplexCost ? manaPaymentDetail : undefined,
    });
    if (response?.result?.status === 'spell_cast') {
      setPreparedCast(null);
      setManaPayment({});
      setAutoPayMana(true);
    }
  }, [
    selectedCastId,
    preparedCast,
    priorityPlayer,
    abilityGraphs,
    cardMap,
    manaPayment,
    isComplexCost,
    manaPaymentDetail,
    buildCastContext,
    autoPayWard,
    wardPaymentsPayload,
    additionalCastPaymentsPayload,
    selectedAlternativeCostTag,
    alternativeExtraPaymentsPayload,
    runEngineAction,
  ]);

  return {
    preparedCast,
    manaPayment,
    manaPaymentDetail,
    autoPayMana,
    isComplexCost,
    costLabel,
    manaPaymentErrors: manaPaymentStatus.errors,
    selectedAlternativeCostTag,
    alternativeCostOptions,
    alternativeExtraCostOptions,
    alternativeExtraCostEntries,
    alternativeExtraPayments,
    alternativeExtraPaymentDetails,
    alternativeExtraCostErrors,
    hasAlternativeExtraCostErrors,
    optionalCostOptions,
    optionalCostSelections,
    optionalCostEntries,
    optionalCostPayments,
    optionalCostPaymentDetails,
    optionalCostErrors: optionalCostPaymentErrors,
    hasOptionalCostErrors,
    optionalCopyCount,
    conspireSelected,
    conspireOptions,
    conspireTaps,
    conspireError,
    isArcaneSpell,
    spliceOptions,
    spliceSelections,
    spliceCosts,
    splicePayments,
    splicePaymentDetails,
    spliceCostErrors,
    additionalCastCosts,
    additionalCastPayments,
    additionalCastPaymentDetails,
    additionalCastCostErrors,
    hasAdditionalCastCostErrors,
    activationCosts,
    activationPayments,
    activationPaymentDetails,
    activationCostErrors,
    hasActivationCostErrors,
    copyTargetsEnabled,
    copyTargetsCount,
    setManaPayment,
    setManaPaymentDetail,
    setAutoPayMana,
    setSelectedAlternativeCostTag,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    handleToggleConspireTap,
    handleToggleSpliceCard,
    setOptionalCostPayments,
    setOptionalCostPaymentDetails,
    setAlternativeExtraPayments,
    setAlternativeExtraPaymentDetails,
    setAdditionalCastPayments,
    setAdditionalCastPaymentDetails,
    setActivationPayments,
    setActivationPaymentDetails,
    setSplicePayments,
    setSplicePaymentDetails,
    handlePrepareCast,
    handleFinalizeCast,
  };
}
