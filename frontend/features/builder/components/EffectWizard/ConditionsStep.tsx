'use client';

import type { UnifiedEffect, ConditionSpec } from '@/lib/unifiedEffect';
import { ConditionBuilder } from '@/features/builder/components/ConditionBuilder';
import { Button } from '@/components/ui/Button';
import type { StructuredCondition } from '@/lib/conditionTypes';

interface ConditionsStepProps {
  effect: UnifiedEffect;
  onChange: (effect: UnifiedEffect) => void;
  previousSteps?: Array<{ id: string; index: number; label: string }>;
}

export function ConditionsStep({ effect, onChange, previousSteps = [] }: ConditionsStepProps) {
  const conditions = (effect.conditions ?? []) as StructuredCondition[];

  const handleAdd = () => {
    const newCondition: StructuredCondition = { type: 'control_count', value: 1, permanentType: 'creature' };
    onChange({ ...effect, conditions: [...conditions, newCondition] });
  };

  const handleUpdate = (index: number, updated: StructuredCondition | undefined) => {
    if (!updated) {
      const next = conditions.filter((_, i) => i !== index);
      onChange({ ...effect, conditions: next.length ? next : undefined });
    } else {
      const next = [...conditions];
      next[index] = updated;
      onChange({ ...effect, conditions: next });
    }
  };

  const handleRemove = (index: number) => {
    const next = conditions.filter((_, i) => i !== index);
    onChange({ ...effect, conditions: next.length ? next : undefined });
  };

  return (
    <div className="space-y-4">
      <p className="text-sm text-[color:var(--theme-text-secondary)]">
        Add conditions that must be met for this effect to trigger/apply.
      </p>
      {conditions.length === 0 ? (
        <p className="text-xs text-[color:var(--theme-text-muted)]">No conditions added yet.</p>
      ) : (
        <div className="space-y-3">
          {conditions.map((condition, index) => (
            <div key={`condition-${index}`} className="relative">
              <ConditionBuilder
                condition={condition}
                onChange={(updated) => handleUpdate(index, updated)}
                onRemove={() => handleRemove(index)}
                previousSteps={previousSteps}
              />
            </div>
          ))}
        </div>
      )}
      <Button variant="outline" onClick={handleAdd} className="text-xs">
        Add Condition
      </Button>
    </div>
  );
}
