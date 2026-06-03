import { useEffect, useMemo, useState } from 'react';
import type { Dispatch, SetStateAction } from 'react';

interface ReplacementConflict {
  key: string;
  [key: string]: any;
}

interface UseReplacementStateProps {
  replacementConflicts: ReplacementConflict[];
}

interface UseReplacementStateResult {
  replacementChoices: Record<string, string>;
  setReplacementChoices: Dispatch<SetStateAction<Record<string, string>>>;
  highlightedReplacementKey: string | null;
  setHighlightedReplacementKey: Dispatch<SetStateAction<string | null>>;
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: ReplacementConflict[];
}

/**
 * Manages replacement effect choices and tracks unresolved damage replacements.
 */
export function useReplacementState({
  replacementConflicts,
}: UseReplacementStateProps): UseReplacementStateResult {
  const [replacementChoices, setReplacementChoices] = useState<Record<string, string>>({});
  const [highlightedReplacementKey, setHighlightedReplacementKey] = useState<string | null>(null);

  const hasUnresolvedDamageReplacements = useMemo(
    () => replacementConflicts.some(
      (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
    ),
    [replacementConflicts, replacementChoices]
  );

  const unresolvedDamageReplacements = useMemo(
    () => replacementConflicts.filter(
      (entry) => entry.key.startsWith('damage:event:') && !replacementChoices[entry.key]
    ),
    [replacementConflicts, replacementChoices]
  );

  // Auto-highlight first unresolved damage replacement
  useEffect(() => {
    if (unresolvedDamageReplacements.length === 0) {
      setHighlightedReplacementKey(null);
      return;
    }
    if (!highlightedReplacementKey || !unresolvedDamageReplacements.some((entry) => entry.key === highlightedReplacementKey)) {
      setHighlightedReplacementKey(unresolvedDamageReplacements[0].key);
    }
  }, [highlightedReplacementKey, unresolvedDamageReplacements]);

  return {
    replacementChoices,
    setReplacementChoices,
    highlightedReplacementKey,
    setHighlightedReplacementKey,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
  };
}
