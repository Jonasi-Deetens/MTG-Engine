import { Button } from '@/components/ui/Button';
import { formatEffect } from '@/lib/effectTypes';
import type { EffectStep } from '@/lib/unifiedEffect';

interface EffectCardProps {
  step: EffectStep;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

function describeEffect(step: EffectStep): string {
  const body = step.effect.effect;
  if (body.kind === 'one_shot') {
    return formatEffect(body.action as any);
  }
  if (body.kind === 'continuous') {
    const modifier = body.modifier as any;
    if (modifier?.type === 'add_keyword' && modifier.keyword) {
      return `Grant ${modifier.keyword}`;
    }
    return `Continuous (${modifier?.type || 'modifier'})`;
  }
  if (body.kind === 'replacement') {
    return 'Replacement effect';
  }
  if (body.kind === 'prevention') {
    return 'Prevention effect';
  }
  return 'Effect';
}

export function EffectCard({ step, onEdit, onDelete }: EffectCardProps) {
  return (
    <div className="border border-[color:var(--theme-card-border)] rounded-lg p-3 bg-[color:var(--theme-card-bg)] space-y-2">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="text-sm font-medium text-[color:var(--theme-text-primary)]">
            {describeEffect(step)}
          </div>
          <div className="text-xs text-[color:var(--theme-text-secondary)]">
            {step.effect.initiation} · {step.effect.persistence} · {step.effect.resolution}
          </div>
        </div>
        <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
          <Button size="sm" variant="outline" onClick={() => onEdit(step.id)}>
            Edit
          </Button>
          <Button size="sm" variant="outline" onClick={() => onDelete(step.id)}>
            Remove
          </Button>
        </div>
      </div>
    </div>
  );
}
