'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { EngineGameStateSnapshot, EngineCardMap } from '@/lib/engine';
import { useReplacementConflicts, ReplacementConflictEntry } from '@/hooks/useReplacementConflicts';
import { useWardPayments } from '@/hooks/useWardPayments';
import {
  buildEnterChoiceConfig,
  buildEnterChoiceDefaults,
  buildEnterChoiceErrors,
  buildEnterChoiceTargetOptions,
  EnterChoiceConfig,
} from '@/lib/enterChoices';
import { buildModalChoiceErrors, deriveModalConfig, ModalChoiceConfig } from '@/lib/modalChoices';
import { ManaPaymentDetail } from '@/lib/manaPayment';

/**
 * ChoicesContext - Modal, enter, replacement, and ward choices
 * 
 * Responsible for:
 * - Modal choices (choose modes for spells)
 * - Enter choices (ETB choices like choosing colors)
 * - Replacement conflict resolution
 * - Ward payment tracking
 */

export interface ChoicesContextValue {
  // Modal choices
  modalChoiceConfig: ModalChoiceConfig | null;
  selectedModalModes: string[];
  modalChoiceErrors: string[];
  modalChoicesForCast: string[];
  entwineSelected: boolean;
  handleToggleModalMode: (modeId: string) => void;
  setSelectedModalModes: (modes: string[]) => void;
  
  // Enter choices
  enterChoiceConfig: EnterChoiceConfig[];
  enterChoices: Record<string, string>;
  enterChoiceErrors: string[];
  enterChoiceTargetOptions: Array<{ value: string; label: string }>;
  setEnterChoices: (choices: Record<string, string>) => void;
  onEnterChoiceChange: (type: string, value: string) => void;
  
  // Replacement conflicts
  replacementChoices: Record<string, string>;
  replacementConflicts: ReplacementConflictEntry[];
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: ReplacementConflictEntry[];
  highlightedReplacementKey: string | null;
  setReplacementChoices: (choices: Record<string, string>) => void;
  setHighlightedReplacementKey: (key: string | null) => void;
  
  // Ward payments
  wardTargets: any[];
  wardPayments: Record<string, any>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  wardPaymentsPayload: Record<string, any>;
  hasWardPaymentErrors: boolean;
  autoPayWard: boolean;
  setWardPayments: (payments: Record<string, any>) => void;
  setWardPaymentDetails: (details: Record<string, ManaPaymentDetail>) => void;
  setAutoPayWard: (auto: boolean) => void;
}

interface ChoicesProviderProps {
  children: React.ReactNode;
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedGraph: any;
  activeGraph: any;
  resolvedTargetObjectIds: string[];
  optionalCostSelections: Record<string, number>;
  optionalCostOptions: any[];
}

const ChoicesContext = createContext<ChoicesContextValue | null>(null);

export function ChoicesProvider({
  children,
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedGraph,
  activeGraph,
  resolvedTargetObjectIds,
  optionalCostSelections,
  optionalCostOptions,
}: ChoicesProviderProps) {
  const value = useChoicesInternal({
    gameState,
    cardMap,
    priorityPlayer,
    selectedHandId,
    selectedGraph,
    activeGraph,
    resolvedTargetObjectIds,
    optionalCostSelections,
    optionalCostOptions,
  });
  return <ChoicesContext.Provider value={value}>{children}</ChoicesContext.Provider>;
}

export function useChoices() {
  const context = useContext(ChoicesContext);
  if (!context) {
    throw new Error('useChoices must be used within ChoicesProvider');
  }
  return context;
}

interface UseChoicesInternalArgs {
  gameState: EngineGameStateSnapshot | null;
  cardMap: EngineCardMap;
  priorityPlayer: number | null;
  selectedHandId: string | null;
  selectedGraph: any;
  activeGraph: any;
  resolvedTargetObjectIds: string[];
  optionalCostSelections: Record<string, number>;
  optionalCostOptions: any[];
}

function useChoicesInternal({
  gameState,
  cardMap,
  priorityPlayer,
  selectedHandId,
  selectedGraph,
  activeGraph,
  resolvedTargetObjectIds,
  optionalCostSelections,
  optionalCostOptions,
}: UseChoicesInternalArgs): ChoicesContextValue {
  const manaPool = gameState?.players.find((p) => p.id === priorityPlayer)?.mana_pool ?? {};

  // Modal choices state
  const [selectedModalModes, setSelectedModalModes] = useState<string[]>([]);
  const [enterChoices, setEnterChoices] = useState<Record<string, string>>({});
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});
  const [highlightedReplacementKey, setHighlightedReplacementKey] = useState<string | null>(null);
  const [autoPayWard, setAutoPayWard] = useState(true);

  // Modal choice config
  const modalChoiceConfig = useMemo(() => deriveModalConfig(activeGraph), [activeGraph]);
  
  const modalChoiceErrors = useMemo(
    () => buildModalChoiceErrors(modalChoiceConfig, selectedModalModes),
    [modalChoiceConfig, selectedModalModes]
  );

  // Reset modal modes on graph change
  useEffect(() => {
    setSelectedModalModes([]);
  }, [selectedGraph, selectedHandId]);

  // Entwine handling
  const entwineSelected = useMemo(
    () => optionalCostOptions.some((option) => option.kind === 'entwine' && (optionalCostSelections[option.tag] ?? 0) > 0),
    [optionalCostOptions, optionalCostSelections]
  );

  const modalChoicesForCast = useMemo(() => {
    if (!entwineSelected || !modalChoiceConfig) return selectedModalModes;
    return modalChoiceConfig.modes.map((mode) => mode.id);
  }, [entwineSelected, modalChoiceConfig, selectedModalModes]);

  // Auto-select all modes when entwine is selected
  useEffect(() => {
    if (!entwineSelected || !modalChoiceConfig) return;
    setSelectedModalModes(modalChoiceConfig.modes.map((mode) => mode.id));
  }, [entwineSelected, modalChoiceConfig]);

  const handleToggleModalMode = useCallback((modeId: string) => {
    if (entwineSelected) return;
    setSelectedModalModes((prev) => {
      if (!modalChoiceConfig) return prev;
      if (modalChoiceConfig.max === 1) {
        return prev.includes(modeId) ? [] : [modeId];
      }
      const exists = prev.includes(modeId);
      const next = exists ? prev.filter((entry) => entry !== modeId) : [...prev, modeId];
      if (modalChoiceConfig.max !== null && next.length > modalChoiceConfig.max) {
        return next.slice(0, modalChoiceConfig.max);
      }
      return next;
    });
  }, [entwineSelected, modalChoiceConfig]);

  // Enter choice config
  const enterChoiceConfig = useMemo(() => buildEnterChoiceConfig(selectedGraph), [selectedGraph]);
  
  const enterChoiceTargetOptions = useMemo(
    () => buildEnterChoiceTargetOptions(gameState, cardMap),
    [gameState, cardMap]
  );
  
  const enterChoiceErrors = useMemo(
    () => buildEnterChoiceErrors(enterChoiceConfig, enterChoices),
    [enterChoiceConfig, enterChoices]
  );

  // Initialize enter choices
  useEffect(() => {
    if (enterChoiceConfig.length === 0) {
      setEnterChoices({});
      return;
    }
    setEnterChoices((prev) => buildEnterChoiceDefaults(enterChoiceConfig, prev));
  }, [selectedHandId, enterChoiceConfig]);

  const onEnterChoiceChange = useCallback((type: string, value: string) => {
    setEnterChoices((prev) => ({ ...prev, [type]: value }));
  }, []);

  // Replacement conflicts
  const replacementConflicts = useReplacementConflicts(gameState);

  const hasUnresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.some(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );

  const unresolvedDamageReplacements = useMemo(
    () =>
      replacementConflicts.filter(
        (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
      ),
    [replacementConflicts, replacementChoices]
  );

  // Auto-highlight unresolved damage replacements
  useEffect(() => {
    if (unresolvedDamageReplacements.length === 0) {
      setHighlightedReplacementKey(null);
      return;
    }
    if (!highlightedReplacementKey || !unresolvedDamageReplacements.some((entry) => entry.key === highlightedReplacementKey)) {
      setHighlightedReplacementKey(unresolvedDamageReplacements[0].key);
    }
  }, [highlightedReplacementKey, unresolvedDamageReplacements]);

  // Sync replacement choices from game state
  useEffect(() => {
    if (!gameState) return;
    if (gameState.replacement_choices) {
      setReplacementChoices(gameState.replacement_choices);
    }
  }, [gameState?.turn.step, gameState?.turn.turn_number]);

  // Ward payments
  const {
    wardTargets,
    wardPayments,
    setWardPayments,
    wardPaymentDetails,
    setWardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
  } = useWardPayments({
    objects: gameState?.objects ?? [],
    players: gameState?.players ?? [],
    cardMap,
    currentPlayerId: priorityPlayer,
    selectedTargetObjectIds: resolvedTargetObjectIds,
    manaPool,
    autoPayWard,
  });

  const hasWardPaymentErrors = useMemo(
    () => Object.values(wardPaymentErrors).some((entries) => entries.length > 0),
    [wardPaymentErrors]
  );

  return {
    modalChoiceConfig,
    selectedModalModes,
    modalChoiceErrors,
    modalChoicesForCast,
    entwineSelected,
    handleToggleModalMode,
    setSelectedModalModes,
    enterChoiceConfig,
    enterChoices,
    enterChoiceErrors,
    enterChoiceTargetOptions,
    setEnterChoices,
    onEnterChoiceChange,
    replacementChoices,
    replacementConflicts,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    highlightedReplacementKey,
    setReplacementChoices,
    setHighlightedReplacementKey,
    wardTargets,
    wardPayments,
    wardPaymentDetails,
    wardPaymentErrors,
    wardPaymentsPayload,
    hasWardPaymentErrors,
    autoPayWard,
    setWardPayments,
    setWardPaymentDetails,
    setAutoPayWard,
  };
}
