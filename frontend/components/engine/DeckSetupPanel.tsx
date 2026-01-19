'use client';

import { DeckResponse } from '@/lib/decks';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface DeckSetupPanelProps {
  deckList: DeckResponse[];
  selectedDeckIds: Array<number | null>;
  loading: boolean;
  canStart: boolean;
  onSelectDeck: (index: number, value: string) => void;
  onStart: () => void;
}

export function DeckSetupPanel({
  deckList,
  selectedDeckIds,
  loading,
  canStart,
  onSelectDeck,
  onStart,
}: DeckSetupPanelProps) {
  return (
    <Card variant="bordered" className="p-4 space-y-4">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">
        Select decks for each player
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {selectedDeckIds.map((deckId, index) => (
          <div key={`player-${index}`} className="space-y-2">
            <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">
              Player {index + 1}
            </div>
            <select
              value={deckId ?? ''}
              onChange={(e) => onSelectDeck(index, e.target.value)}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            >
              <option value="">Select Commander deck...</option>
              {deckList.map((deck) => (
                <option key={deck.id} value={deck.id}>
                  {deck.name}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
      <div className="flex justify-end">
        <Button variant="primary" onClick={onStart} disabled={!canStart || loading}>
          {loading ? 'Starting...' : 'Start Game'}
        </Button>
      </div>
    </Card>
  );
}

