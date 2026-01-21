'use client';

import { Card } from '@/components/ui/Card';
import { usePlayGame } from '@/app/(protected)/play/PlayProviders';

export function PlayHeader() {
  // Using the focused usePlayGame() hook instead of the monolithic usePlayState()
  const { error } = usePlayGame();

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2">
          Playtest Commander
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Select four Commander decks and play using the engine rules.
        </p>
      </div>

      {error && (
        <Card variant="bordered" className="p-4 text-[color:var(--theme-status-error)]">
          {error}
        </Card>
      )}
    </div>
  );
}
