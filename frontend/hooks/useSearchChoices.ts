import { useMemo, useState } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';
import { isEffectActiveForModes, ModalChoiceConfig } from '@/lib/modalChoices';
import { formatEffect } from '@/lib/effectTypes';
import { filterSearchCandidates, resolvePlayerIdsForEffect } from '@/lib/searchFilters';

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

  const searchEntries = useMemo<SearchChoiceEntry[]>(() => {
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

  return {
    searchEntries,
    searchTargetsByEffect,
    searchErrors,
  };
};

