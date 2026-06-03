import { useMemo } from 'react';

interface EffectTargetGroup {
  label: string;
  minTargets?: number | null;
  selectedObjectIds: string[];
  selectedPlayerIds: number[];
  errors?: string[];
}

interface UseTargetSelectionErrorsProps {
  hasEffectTargets: boolean;
  effectTargetGroups: EffectTargetGroup[];
  globalTargetErrors: string[];
  searchErrors: string[];
  copyTargetErrors: string[];
  copyTargetErrorsGlobal: string[];
  minTargetsGlobal: Record<string, number> | null;
  resolvedTargetObjectIds: string[];
  resolvedTargetPlayerIds: number[];
}

/**
 * Computes target selection validation errors.
 * Handles both effect-based targeting and global targeting modes.
 */
export function useTargetSelectionErrors({
  hasEffectTargets,
  effectTargetGroups,
  globalTargetErrors,
  searchErrors,
  copyTargetErrors,
  copyTargetErrorsGlobal,
  minTargetsGlobal,
  resolvedTargetObjectIds,
  resolvedTargetPlayerIds,
}: UseTargetSelectionErrorsProps): string[] {
  return useMemo(() => {
    if (hasEffectTargets) {
      const errors: string[] = [];
      
      effectTargetGroups.forEach((group) => {
        const min = group.minTargets ?? 0;
        if (min > 0) {
          const count = group.selectedObjectIds.length + group.selectedPlayerIds.length;
          if (count < min) {
            errors.push(`${group.label}: select at least ${min} target${min === 1 ? '' : 's'}.`);
          }
        }
        if (group.errors && group.errors.length > 0) {
          group.errors.forEach((error) => {
            errors.push(`${group.label}: ${error}`);
          });
        }
      });
      
      if (globalTargetErrors.length > 0) {
        errors.push(...globalTargetErrors);
      }
      if (searchErrors.length > 0) {
        errors.push(...searchErrors);
      }
      if (copyTargetErrors.length > 0) {
        errors.push(...copyTargetErrors);
      }
      
      return errors;
    }

    // Global targeting mode
    const min = minTargetsGlobal?.target ?? 0;
    const count = resolvedTargetObjectIds.length + resolvedTargetPlayerIds.length;
    
    if (min > 0 && count < min) {
      return [`Select at least ${min} target${min === 1 ? '' : 's'}.`];
    }
    
    if (copyTargetErrorsGlobal.length > 0) {
      return copyTargetErrorsGlobal;
    }
    
    return [];
  }, [
    effectTargetGroups,
    globalTargetErrors,
    searchErrors,
    hasEffectTargets,
    minTargetsGlobal,
    copyTargetErrors,
    copyTargetErrorsGlobal,
    resolvedTargetObjectIds.length,
    resolvedTargetPlayerIds.length,
  ]);
}
