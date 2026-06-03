import { useCallback, useEffect, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import type { EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';
import { deriveSpliceCardsFromHand } from '@/lib/graphCosts';

interface OptionalCostOption {
  tag: string;
  kind: string;
  costs: any[];
  repeatable?: boolean;
}

interface UseOptionalCostsStateProps {
  gameState: EngineGameStateSnapshot | null;
  selectedHandId: string | null;
  selectedHandObject: any;
  currentPriority: number | null;
  optionalCostOptions: OptionalCostOption[];
  objectMap: Map<string, any>;
  cardMap: EngineCardMap;
  effectGraphs: Record<string, any>;
  loadEffectGraphForObject: (objectId: string) => void;
}

interface UseOptionalCostsStateResult {
  optionalCostSelections: Record<string, number>;
  setOptionalCostSelections: Dispatch<SetStateAction<Record<string, number>>>;
  handleToggleOptionalCost: (tag: string) => void;
  handleUpdateOptionalCostCount: (tag: string, count: number) => void;
  optionalCostCosts: any[];
  optionalCopyCount: number;
  // Conspire
  conspireSelected: boolean;
  conspireOptions: Array<{ value: string; label: string }>;
  conspireTaps: string[];
  setConspireTaps: Dispatch<SetStateAction<string[]>>;
  conspireError: string | null;
  handleToggleConspireTap: (value: string) => void;
  // Splice
  isArcaneSpell: boolean;
  spliceOptions: Array<{ cardId: string; costs: any[]; label: string }>;
  spliceSelections: string[];
  setSpliceSelections: Dispatch<SetStateAction<string[]>>;
  spliceCostList: any[];
  handleToggleSpliceCard: (cardId: string) => void;
  // Entwine
  entwineSelected: boolean;
}

/**
 * Manages optional cost selections including replicate, conspire, splice, and entwine.
 */
export function useOptionalCostsState({
  gameState,
  selectedHandId,
  selectedHandObject,
  currentPriority,
  optionalCostOptions,
  objectMap,
  cardMap,
  effectGraphs,
  loadEffectGraphForObject,
}: UseOptionalCostsStateProps): UseOptionalCostsStateResult {
  const [optionalCostSelections, setOptionalCostSelections] = useState<Record<string, number>>({});
  const [conspireTaps, setConspireTaps] = useState<string[]>([]);
  const [spliceSelections, setSpliceSelections] = useState<string[]>([]);

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

  // Compute optional cost costs based on selections
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

  // Count optional copies (replicate + conspire)
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

  // Conspire handling
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
        return colors.some((color: string) => spellColors.has(color));
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
    const player = gameState.players.find((entry) => entry.id === currentPriority);
    (player?.hand ?? []).forEach((objectId) => {
      loadEffectGraphForObject(objectId);
    });
  }, [currentPriority, gameState, isArcaneSpell, loadEffectGraphForObject]);

  const spliceOptions = useMemo(() => {
    if (!isArcaneSpell || !gameState) return [];
    const player = gameState.players.find((entry) => entry.id === currentPriority);
    const handIds = player?.hand ?? [];
    const graphMap: Record<string, any> = {};
    
    handIds.forEach((objectId) => {
      const cardId = cardMap[objectId]?.card_id;
      if (!cardId) return;
      const graph = effectGraphs[cardId];
      if (graph) {
        graphMap[objectId] = graph;
      }
    });
    
    return deriveSpliceCardsFromHand(handIds, graphMap).map((entry) => ({
      cardId: entry.cardId,
      costs: entry.costs,
      label: cardMap[entry.cardId]?.name || objectMap.get(entry.cardId)?.name || entry.cardId,
    }));
  }, [cardMap, currentPriority, effectGraphs, gameState, isArcaneSpell, objectMap]);

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

  // Entwine handling
  const entwineSelected = useMemo(
    () => optionalCostOptions.some((option) => option.kind === 'entwine' && (optionalCostSelections[option.tag] ?? 0) > 0),
    [optionalCostOptions, optionalCostSelections]
  );

  return {
    optionalCostSelections,
    setOptionalCostSelections,
    handleToggleOptionalCost,
    handleUpdateOptionalCostCount,
    optionalCostCosts,
    optionalCopyCount,
    conspireSelected,
    conspireOptions,
    conspireTaps,
    setConspireTaps,
    conspireError,
    handleToggleConspireTap,
    isArcaneSpell,
    spliceOptions,
    spliceSelections,
    setSpliceSelections,
    spliceCostList,
    handleToggleSpliceCard,
    entwineSelected,
  };
}
