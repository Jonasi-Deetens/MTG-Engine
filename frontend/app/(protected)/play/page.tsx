"use client";

import { DeckSetupPanel } from '@/features/game/components/DeckSetupPanel';
import { PlayProviders, usePlayGame, usePlaySetup } from '@/app/(protected)/play/PlayProviders';
import { PlayActionsPanel } from '@/app/(protected)/play/components/PlayActionsPanel';
import { PlayHeader } from '@/app/(protected)/play/components/PlayHeader';
import { PlayMat } from '@/app/(protected)/play/components/PlayMat';

function PlayPageContent() {
  const { gameState } = usePlayGame();
  const { deckList, selectedDeckIds, setupLoading, canStart, handleSelectDeck, startGame } = usePlaySetup();

  return (
    <div className="space-y-6">
      <PlayHeader />

      {!gameState && (
        <DeckSetupPanel
          deckList={deckList}
          selectedDeckIds={selectedDeckIds}
          loading={setupLoading}
          canStart={canStart}
          onSelectDeck={handleSelectDeck}
          onStart={startGame}
        />
      )}

      {gameState && (
        <div className="play-surface">
          <div className="play-layout">
            <div className="play-mat">
              <PlayMat />
            </div>
            <aside className="play-panel">
              <PlayActionsPanel />
            </aside>
          </div>
        </div>
      )}
    </div>
  );
}

export default function PlayPage() {
  return (
    <PlayProviders>
      <PlayPageContent />
    </PlayProviders>
  );
}
