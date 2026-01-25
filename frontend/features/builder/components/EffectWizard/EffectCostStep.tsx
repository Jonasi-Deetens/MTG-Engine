import type { UnifiedEffect } from '@/lib/unifiedEffect';
import type { CostEntry } from '@/lib/activationCosts';
import type { OptionalCostEntry } from '@/lib/optionalCosts';
import { CostListEditor } from '@/features/builder/components/CostListEditor';
import { OptionalCostListEditor } from '@/features/builder/components/OptionalCostListEditor';

interface EffectCostStepProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
}

export function EffectCostStep({ effect, onChange }: EffectCostStepProps) {
  const additionalCosts = Array.isArray(effect.additionalCosts)
    ? (effect.additionalCosts as CostEntry[])
    : [];
  const optionalCosts = Array.isArray(effect.optionalCosts)
    ? (effect.optionalCosts as OptionalCostEntry[])
    : [];

  const updateAdditionalCosts = (nextCosts: CostEntry[]) => {
    onChange({ ...effect, additionalCosts: nextCosts });
  };
  const updateOptionalCosts = (nextCosts: OptionalCostEntry[]) => {
    onChange({ ...effect, optionalCosts: nextCosts });
  };

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <div className="text-sm text-[color:var(--theme-text-secondary)]">
          Additional costs required to use this effect.
        </div>
        <CostListEditor label="Additional Costs" value={additionalCosts} onChange={updateAdditionalCosts} />
      </div>
      <div className="space-y-3">
        <div className="text-sm text-[color:var(--theme-text-secondary)]">
          Optional costs you may pay when casting.
        </div>
        <OptionalCostListEditor value={optionalCosts} onChange={updateOptionalCosts} />
      </div>
    </div>
  );
}
