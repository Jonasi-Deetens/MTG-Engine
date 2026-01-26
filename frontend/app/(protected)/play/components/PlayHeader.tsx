'use client';

import { usePlayGame } from '@/app/(protected)/play/PlayProviders';
import { BracketHeader } from '@/components/ui/play/NierUIElements';

export function PlayHeader() {
  // Using the focused usePlayGame() hook instead of the monolithic usePlayState()
  const { error } = usePlayGame();

  return (
    <div className="space-y-4">
      <div>
        <h1
          className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2 nier-glitch"
          data-text="Playtest Commander"
        >
          Playtest Commander
        </h1>
        <p className="text-[color:var(--theme-text-secondary)]">
          Select four Commander decks and play using the engine rules.
        </p>
      </div>

      {error && (
        <div className="nier-panel space-y-2 text-[color:var(--theme-status-error)]">
          <BracketHeader>Error</BracketHeader>
          <div className="text-sm">{error}</div>
        </div>
      )}
    </div>
  );
}
