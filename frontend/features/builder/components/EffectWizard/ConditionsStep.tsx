'use client';

import { useState } from 'react';

import type { UnifiedEffect } from '@/lib/unifiedEffect';

interface ConditionsStepProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

export function ConditionsStep({ effect, onChange }: ConditionsStepProps) {
  const [draft, setDraft] = useState(
    JSON.stringify(effect.conditions ?? [], null, 2)
  );
  const [error, setError] = useState('');

  const handleApply = () => {
    try {
      const parsed = JSON.parse(draft);
      if (!Array.isArray(parsed)) {
        setError('Conditions must be an array');
        return;
      }
      onChange({ ...effect, conditions: parsed });
      setError('');
    } catch {
      setError('Invalid JSON');
    }
  };

  return (
    <div className="space-y-3">
      <p className="text-sm text-[color:var(--theme-text-secondary)]">
        Optional conditions for this effect (advanced).
      </p>
      <textarea
        className="w-full rounded border border-[color:var(--theme-card-border)] bg-transparent px-2 py-1 text-xs"
        rows={6}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
      />
      {error && <div className="text-xs text-[color:var(--theme-status-error)]">{error}</div>}
      <button
        className="text-xs text-[color:var(--theme-accent-primary)]"
        onClick={handleApply}
      >
        Apply conditions
      </button>
    </div>
  );
}
