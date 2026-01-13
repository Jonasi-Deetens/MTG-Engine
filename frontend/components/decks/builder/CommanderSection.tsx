// frontend/components/decks/builder/CommanderSection.tsx

import { DeckCommanderResponse, DeckCardResponse } from '@/lib/decks';
import { DroppableList } from '@/components/decks/DroppableList';
import { CardData } from '@/components/cards/CardPreview';

interface CommanderSectionProps {
  commanders: DeckCommanderResponse[];
  onCommanderHover: (card: DeckCardResponse | null) => void;
  onCommanderClick: (card: CardData) => void;
  onRemoveCommander: (cardId: string) => void;
}

export function CommanderSection({
  commanders,
  onCommanderHover,
  onCommanderClick,
  onRemoveCommander,
}: CommanderSectionProps) {
  return (
    <DroppableList id="commander-list" className="space-y-2">
      <div>
        <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)] mb-2">
          Commander{commanders.length > 1 ? 's' : ''} ({commanders.length})
        </div>
        {commanders.length > 0 ? (
          <div>
            {commanders.map((commander) => {
              const manaCost = commander.card.mana_cost || '';
              return (
                <div
                  key={commander.card.card_id}
                  className="flex items-center gap-2 px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm cursor-pointer"
                  onMouseEnter={() => onCommanderHover({ 
                    card: commander.card, 
                    quantity: 1, 
                    card_id: commander.card_id,
                    list_id: null 
                  })}
                  onClick={() => onCommanderClick(commander.card)}
                >
                  <span className="flex-shrink-0 w-5 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                    1x
                  </span>
                  <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] truncate text-xs">
                    {commander.card.name}
                  </span>
                  {manaCost && (
                    <span className="flex-shrink-0 text-[color:var(--theme-accent-primary)] font-mono text-xs">
                      {manaCost}
                    </span>
                  )}
                  <div className="flex items-center gap-0.5 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemoveCommander(commander.card.card_id);
                      }}
                      className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20 rounded transition-colors text-xs"
                      title="Remove"
                    >
                      ×
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-4 text-[color:var(--theme-text-secondary)] text-sm">
            <p>Drop cards here to add as commander</p>
          </div>
        )}
      </div>
    </DroppableList>
  );
}

