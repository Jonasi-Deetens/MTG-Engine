'use client';

import { useEffectStore } from '@/store/effectStore';
import { EffectCard } from './EffectCard';

interface EffectListProps {
  onEdit: (id: string) => void;
}

export function EffectList({ onEdit }: EffectListProps) {
  const { steps, removeStep } = useEffectStore();

  if (steps.length === 0) {
    return (
      <div className="text-center py-8 text-[color:var(--theme-text-secondary)]">
        <p className="text-sm">No effects added yet</p>
        <p className="text-xs mt-1">Add an effect to start building your ability graph</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {steps.map((step) => (
        <EffectCard
          key={step.id}
          step={step}
          onEdit={onEdit}
          onDelete={removeStep}
        />
      ))}
    </div>
  );
}
