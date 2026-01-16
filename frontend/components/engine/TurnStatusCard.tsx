'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface TurnStatusCardProps {
  turnNumber: number;
  phase: string;
  step: string;
  activePlayerIndex: number;
  currentPriority: number | null;
  loading: boolean;
  onPassPriority: () => void;
  onAdvanceStep: () => void;
}

export function TurnStatusCard({
  turnNumber,
  phase,
  step,
  activePlayerIndex,
  currentPriority,
  loading,
  onPassPriority,
  onAdvanceStep,
}: TurnStatusCardProps) {
  return (
    <Card variant="bordered" className="p-4 flex flex-wrap items-center justify-between gap-4">
      <div>
        <div className="text-sm text-[color:var(--theme-text-secondary)]">Turn</div>
        <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
          {turnNumber} · {phase} / {step}
        </div>
        <div className="text-xs text-[color:var(--theme-text-secondary)]">
          Active Player: {activePlayerIndex + 1}
          {typeof currentPriority === 'number' && ` · Priority: ${currentPriority + 1}`}
        </div>
      </div>
      <div className="flex gap-2">
        <Button variant="outline" onClick={onPassPriority} disabled={loading}>
          Pass Priority
        </Button>
        <Button variant="primary" onClick={onAdvanceStep} disabled={loading}>
          Advance Step
        </Button>
      </div>
    </Card>
  );
}

