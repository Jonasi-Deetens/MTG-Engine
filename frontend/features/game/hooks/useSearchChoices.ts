import { useMemo, useState } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';
import { isEffectActiveForModes, ModalChoiceConfig } from '@/lib/modalChoices';
import { formatEffect } from '@/lib/effectTypes';
import { filterSearchCandidates, resolvePlayerIdsForEffect } from '@/lib/searchFilters';
import type { PendingSearchChoice } from './useEngineActions';

type SearchChoiceEntry = {
  id: string;
  nodeId: string;
  label: string;
  playerId: number;
  zone: string;
  candidates: Array<{ id: string; label: string }>;
  selectedIds: string[];
  maxSelections?: number | null;
  onChange: (ids: string[]) => void;
};

export const useSearchChoices = ({
  gameState,
  selectedGraph,
  currentPriority,
  context,
  modalConfig,
  selectedModes = [],
  pendingSearchChoices = [],
  isStackItem = false,
}: {
  gameState: EngineGameStateSnapshot | null;
  selectedGraph: any;
  currentPriority: number | null;
  context?: {
    sourceId?: string | null;
    triggeringSourceId?: string | null;
    triggeringAuraId?: string | null;
    triggeringSpellId?: string | null;
    targetId?: string | null;
  };
  modalConfig?: ModalChoiceConfig | null;
  selectedModes?: string[];
  pendingSearchChoices?: PendingSearchChoice[];
  isStackItem?: boolean;  // True when viewing a stack item (not casting)
}) => {
  const [selections, setSelections] = useState<Record<string, string[]>>({});

  const searchNodes = useMemo(() => {
    const nodes = selectedGraph?.nodes ?? [];
    return nodes.filter((node: any) => {
      if (node?.type !== 'EFFECT') return false;
      if (node?.data?.type !== 'search') return false;
      return isEffectActiveForModes(node?.data ?? {}, modalConfig ?? null, selectedModes);
    });
  }, [modalConfig, selectedGraph, selectedModes]);

  // Build entries from selectedGraph (for spell casting)
  const graphEntries = useMemo<SearchChoiceEntry[]>(() => {
    if (!gameState || searchNodes.length === 0) return [];
    const entries: SearchChoiceEntry[] = [];
    searchNodes.forEach((node: any) => {
      const effect = node.data ?? {};
      const targetPlayers = resolvePlayerIdsForEffect(effect.target, gameState, currentPriority);
      const zone = effect.zone || 'library';
      const maxSelections = typeof effect.amount === 'number' && effect.amount > 0 ? effect.amount : null;
      targetPlayers.forEach((playerId) => {
        const player = gameState.players.find((entry) => entry.id === playerId);
        if (!player) return;
        const pool = (player as any)[zone] as string[] | undefined;
        if (!Array.isArray(pool)) return;
        const filtered = filterSearchCandidates(gameState, effect, playerId, pool, context);
        const candidates = filtered.map((id) => {
          const obj = gameState.objects.find((entry) => entry.id === id);
          return { id, label: obj?.name || id };
        });
        const key = `${node.id}:${playerId}`;
        const selected = selections[key] ?? [];
        const labelBase = formatEffect(effect);
        entries.push({
          id: key,
          nodeId: node.id,
          label: `${labelBase} (Player ${playerId + 1})`,
          playerId,
          zone,
          candidates,
          selectedIds: selected.filter((id) => filtered.includes(id)),
          maxSelections,
          onChange: (ids) =>
            setSelections((prev) => ({
              ...prev,
              [key]: ids,
            })),
        });
      });
    });
    return entries;
  }, [context, currentPriority, gameState, searchNodes, selections]);

  // Build entries from pending search choices (for stack resolution)
  const pendingEntries = useMemo<SearchChoiceEntry[]>(() => {
    console.log('[useSearchChoices] pendingSearchChoices:', pendingSearchChoices, 'currentPriority:', currentPriority);
    if (!gameState || pendingSearchChoices.length === 0) return [];
    return pendingSearchChoices.map((choice) => {
      const key = `pending:${choice.node_id}:${choice.player_id}`;
      const selected = selections[key] ?? [];
      const source = choice.source_id ? gameState.objects.find((o) => o.id === choice.source_id) : null;
      const label = source?.name 
        ? `Search for ${source.name}'s ability` 
        : `Search ${choice.zone}`;
      return {
        id: key,
        nodeId: choice.node_id,
        label: `${label} (Player ${choice.player_id + 1})`,
        playerId: choice.player_id,
        zone: choice.zone,
        candidates: choice.options.map((opt) => ({ id: opt.id, label: opt.name })),
        selectedIds: selected,
        maxSelections: choice.max_selections,
        onChange: (ids: string[]) =>
          setSelections((prev) => ({
            ...prev,
            [key]: ids,
          })),
      };
    });
  }, [gameState, pendingSearchChoices, selections]);

  // Combine entries - pending choices take priority
  // For pending choices, only show entries for the current player (they're the only one who can choose)
  // For stack items, don't show graph-based entries - only show when engine returns pendingSearchChoices
  const searchEntries = useMemo(() => {
    console.log('[useSearchChoices] computing searchEntries: pendingEntries.length=', pendingEntries.length, 'currentPriority=', currentPriority, 'isStackItem=', isStackItem);
    if (pendingEntries.length > 0) {
      // Only show pending choices that belong to the current priority player
      const filtered = pendingEntries.filter((entry) => entry.playerId === currentPriority);
      console.log('[useSearchChoices] filtered pendingEntries:', filtered.length, 'entries for player', currentPriority);
      return filtered;
    }
    // For stack items (already on stack), don't show graph-based search UI
    // Search choices for stack items come from pendingSearchChoices only
    if (isStackItem) {
      return [];
    }
    return graphEntries;
  }, [pendingEntries, graphEntries, currentPriority, isStackItem]);

  const searchTargetsByEffect = useMemo(() => {
    const result: Record<string, Record<string, any>> = {};
    searchEntries.forEach((entry) => {
      if (!result[entry.nodeId]) {
        result[entry.nodeId] = {};
      }
      const existing = result[entry.nodeId].search_results_by_player ?? {};
      result[entry.nodeId].search_results_by_player = {
        ...existing,
        [entry.playerId]: entry.selectedIds,
      };
    });
    return result;
  }, [searchEntries]);

  const searchErrors = useMemo(() => {
    const errors: string[] = [];
    searchEntries.forEach((entry) => {
      if (entry.maxSelections && entry.selectedIds.length > entry.maxSelections) {
        errors.push(`${entry.label}: select up to ${entry.maxSelections} card(s).`);
      }
      entry.selectedIds.forEach((id) => {
        if (!entry.candidates.find((candidate) => candidate.id === id)) {
          errors.push(`${entry.label}: invalid selection ${id}.`);
        }
      });
    });
    return errors;
  }, [searchEntries]);

  // Flag to indicate if the current player has pending search choices
  const hasPendingSearchChoices = searchEntries.length > 0 && pendingEntries.length > 0;

  return {
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
    hasPendingSearchChoices,
  };
};

