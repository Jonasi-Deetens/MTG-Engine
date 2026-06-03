'use client';

import { BracketHeader, HudValue, StatusIndicator } from '@/components/ui/play/NierUIElements';
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
    <div className="nier-panel space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-2">
          <BracketHeader>Turn Status</BracketHeader>
          <div className="flex flex-wrap items-center gap-6">
            <HudValue label="Turn" value={turnNumber} />
            <div className="space-y-1">
              <div className="text-xs uppercase tracking-[0.22em] text-[color:var(--theme-text-muted)]">
                Phase / Step
              </div>
              <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
                {phase} / {step}
              </div>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.18em] text-[color:var(--theme-text-secondary)]">
            <span>Active: {activePlayerIndex + 1}</span>
            {typeof currentPriority === 'number' && (
              <span className="flex items-center gap-2">
                <StatusIndicator tone="primary" pulse />
                Priority {currentPriority + 1}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" onClick={onPassPriority} disabled={loading}>
            Pass Priority
          </Button>
          <Button variant="primary" onClick={onAdvanceStep} disabled={loading}>
            Advance Step
          </Button>
        </div>
      </div>
    </div>
  );
}

