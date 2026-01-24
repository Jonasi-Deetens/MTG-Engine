import type { UnifiedEffect } from '@/lib/unifiedEffect';

interface ReviewStepProps {
  effect: UnifiedEffect;
}

export function ReviewStep({ effect }: ReviewStepProps) {
  return (
    <div className="space-y-3">
      <div className="text-sm text-[color:var(--theme-text-secondary)]">
        Review the effect payload before saving.
      </div>
      <pre className="text-xs whitespace-pre-wrap bg-[color:var(--theme-bg-secondary)]/60 border border-[color:var(--theme-card-border)] rounded p-3">
        {JSON.stringify(effect, null, 2)}
      </pre>
    </div>
  );
}
