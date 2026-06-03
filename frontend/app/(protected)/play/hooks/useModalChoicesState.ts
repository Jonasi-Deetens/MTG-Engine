import { useCallback, useEffect, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';
import { buildModalChoiceErrors, deriveModalConfig } from '@/lib/modalChoices';

interface UseModalChoicesStateProps {
  activeGraph: any;
  selectedGraph: any;
  selectedHandId: string | null;
  entwineSelected: boolean;
}

interface UseModalChoicesStateResult {
  modalChoiceConfig: any;
  selectedModalModes: string[];
  setSelectedModalModes: Dispatch<SetStateAction<string[]>>;
  modalChoiceErrors: string[];
  modalChoicesForCast: string[];
  handleToggleModalMode: (modeId: string) => void;
}

/**
 * Manages modal choice selection for spells with modal abilities.
 * Handles entwine mode override where all modes are selected.
 */
export function useModalChoicesState({
  activeGraph,
  selectedGraph,
  selectedHandId,
  entwineSelected,
}: UseModalChoicesStateProps): UseModalChoicesStateResult {
  const [selectedModalModes, setSelectedModalModes] = useState<string[]>([]);

  const modalChoiceConfig = useMemo(() => deriveModalConfig(activeGraph), [activeGraph]);

  const modalChoiceErrors = useMemo(
    () => buildModalChoiceErrors(modalChoiceConfig, selectedModalModes),
    [modalChoiceConfig, selectedModalModes]
  );

  // Reset modal modes when selected graph changes
  useEffect(() => {
    setSelectedModalModes([]);
  }, [selectedGraph, selectedHandId]);

  // Auto-select all modes when entwine is selected
  useEffect(() => {
    if (!entwineSelected || !modalChoiceConfig) return;
    setSelectedModalModes(modalChoiceConfig.modes.map((mode: any) => mode.id));
  }, [entwineSelected, modalChoiceConfig]);

  // Compute modal choices for casting (all modes if entwine, otherwise selected)
  const modalChoicesForCast = useMemo(() => {
    if (!entwineSelected || !modalChoiceConfig) return selectedModalModes;
    return modalChoiceConfig.modes.map((mode: any) => mode.id);
  }, [entwineSelected, modalChoiceConfig, selectedModalModes]);

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

  return {
    modalChoiceConfig,
    selectedModalModes,
    setSelectedModalModes,
    modalChoiceErrors,
    modalChoicesForCast,
    handleToggleModalMode,
  };
}
