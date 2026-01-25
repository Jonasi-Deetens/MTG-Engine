'use client';

import { formatEffect } from '@/lib/effectTypes';
import type { EffectGraph, EffectStep } from '@/lib/unifiedEffect';
import { useEffectStore } from '@/store/effectStore';

interface EffectGraphPreviewProps {
  graph?: EffectGraph | null;
}

function describeStep(step: EffectStep): string {
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

export function EffectGraphPreview({ graph }: EffectGraphPreviewProps) {
  const sourceKind = useEffectStore((state) => state.sourceKind);
  const steps = useEffectStore((state) => state.steps);
  const currentCardId = useEffectStore((state) => state.currentCard?.card_id ?? null);

  const activeGraph =
    graph ??
    (steps.length
      ? {
          id: currentCardId ? `graph-${currentCardId}` : 'preview',
          sourceKind,
          steps,
        }
      : null);

  if (!activeGraph || !activeGraph.steps.length) {
    return (
      <div className="text-center py-8 text-[color:var(--theme-text-secondary)]">
        <p className="text-sm">No effects added yet</p>
        <p className="text-xs mt-1">Add effects to see the preview</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-xs text-[color:var(--theme-text-secondary)] space-y-1">
        <div>Source: {activeGraph.sourceKind}</div>
      </div>
      <div className="space-y-2">
        {activeGraph.steps.map((step) => (
          <div key={step.id} className="border-l-2 border-[color:var(--theme-border-default)] pl-3">
            <div className="text-sm text-[color:var(--theme-text-primary)]">
              {describeStep(step)}
            </div>
            <div className="text-xs text-[color:var(--theme-text-secondary)]">
              {step.effect.initiation} · {step.effect.persistence} · {step.effect.resolution}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
