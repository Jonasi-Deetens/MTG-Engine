"use client";

import { DeckSetupPanel } from '@/components/engine/DeckSetupPanel';
import { PlayStateProvider, usePlayState } from '@/app/(protected)/play/PlayState';
import { PlayActionsPanel } from '@/app/(protected)/play/components/PlayActionsPanel';
import { PlayHeader } from '@/app/(protected)/play/components/PlayHeader';
import { PlayMat } from '@/app/(protected)/play/components/PlayMat';

function PlayPageContent() {
  const { gameState, deckList, selectedDeckIds, setupLoading, canStart, handleSelectDeck, startGame } = usePlayState();

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
        <div className="space-y-6">
          <PlayActionsPanel />
          <PlayMat />
        </div>
      )}
    </div>
  );
}

export default function PlayPage() {
  return (
    <PlayStateProvider>
      <PlayPageContent />
    </PlayStateProvider>
  );
}
