import type { UnifiedEffect } from '@/lib/unifiedEffect';
import type { CostEntry } from '@/lib/activationCosts';
import { CostListEditor } from '@/features/builder/components/CostListEditor';

interface ActivatedConfigProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

export function ActivatedConfig({ effect, onChange }: ActivatedConfigProps) {
  const items = (effect.cost?.items ?? [{ type: 'tap_self' }]) as CostEntry[];

  const handleCostsChange = (next: CostEntry[]) => {
    const safe = next.length > 0 ? next : [{ type: 'tap_self' as const }];
    onChange({
      ...effect,
      cost: { ...(effect.cost ?? {}), items: safe },
    });
  };

  return (
    <div className="space-y-3">
      <p className="text-sm text-[color:var(--theme-text-secondary)]">
        Activation cost — what a player pays to use this ability (tap, mana, sacrifice, etc.).
      </p>
      <CostListEditor label="Activation cost" value={items} onChange={handleCostsChange} />
    </div>
  );
}
