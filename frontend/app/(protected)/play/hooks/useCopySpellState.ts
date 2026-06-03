import { useEffect, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

interface CopyTargetSelection {
  objectIds: string[];
  playerIds: number[];
}

interface UseCopySpellStateProps {
  selectedGraph: any;
  optionalCopyCount: number;
}

interface UseCopySpellStateResult {
  copySpellConfig: { enabled: boolean; amount: number };
  copyTargetSelections: CopyTargetSelection[];
  setCopyTargetSelections: Dispatch<SetStateAction<CopyTargetSelection[]>>;
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
}

/**
 * Manages copy spell configuration and target selections for spell copies.
 */
export function useCopySpellState({
  selectedGraph,
  optionalCopyCount,
}: UseCopySpellStateProps): UseCopySpellStateResult {
  const [copyTargetSelections, setCopyTargetSelections] = useState<CopyTargetSelection[]>([]);

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

  // Maintain copy target selection array size
  useEffect(() => {
    if (!copyTargetsEnabled) {
      setCopyTargetSelections([]);
      return;
    }
    
    setCopyTargetSelections((prev) => {
      const next = [...prev];
      while (next.length < copyTargetsCount) {
        next.push({ objectIds: [], playerIds: [] });
      }
      return next.slice(0, copyTargetsCount);
    });
  }, [copyTargetsCount, copyTargetsEnabled]);

  return {
    copySpellConfig,
    copyTargetSelections,
    setCopyTargetSelections,
    copyTargetsEnabled,
    copyTargetsCount,
  };
}
