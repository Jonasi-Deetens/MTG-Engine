"use client";

import './play.css';

import { useEffect } from 'react';
import { DeckSetupPanel } from '@/features/game/components/DeckSetupPanel';
import { PlayProviders, usePlayGame, usePlaySetup } from '@/app/(protected)/play/PlayProviders';
import { PlayActionsPanel } from '@/app/(protected)/play/components/PlayActionsPanel';
import { PlayHeader } from '@/app/(protected)/play/components/PlayHeader';
import { PlayMat } from '@/app/(protected)/play/components/PlayMat';

function PlayPageContent() {
  const { gameState } = usePlayGame();
  const { deckList, selectedDeckIds, setupLoading, canStart, handleSelectDeck, startGame } = usePlaySetup();

  useEffect(() => {
    document.body.classList.add('play-ui-body');
    return () => {
      document.body.classList.remove('play-ui-body');
    };
  }, []);

  return (
    <div className="play-ui" data-play-theme="nier">
      <div className="play-page space-y-6 nier-noise">
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
            <span className="nier-scanline" aria-hidden="true" />
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
