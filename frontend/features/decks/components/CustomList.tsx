'use client';

// frontend/components/decks/CustomList.tsx

import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { DroppableList } from './DroppableList';
import { DraggableCard } from './DraggableCard';

interface CustomListProps {
  list: DeckCustomListResponse;
  cards: DeckCardResponse[];
  onQuantityChange?: (cardId: string, quantity: number) => void;
  onRemove?: (cardId: string) => void;
  onCardHover?: (card: DeckCardResponse | null) => void;
  onCardClick?: (card: DeckCardResponse) => void;
  showControls?: boolean;
}

export function CustomList({
  list,
  cards,
  onQuantityChange,
  onRemove,
  onCardHover,
  onCardClick,
  showControls = true,
}: CustomListProps) {
  const totalCount = cards.reduce((sum, card) => sum + card.quantity, 0);

  const handleQuantityChange = (cardId: string, delta: number) => {
    const card = cards.find(c => c.card_id === cardId);
    if (card && onQuantityChange) {
      const newQuantity = Math.max(1, card.quantity + delta);
      onQuantityChange(cardId, newQuantity);
    }
  };

  const handleRemove = (cardId: string) => {
    if (onRemove) {
      onRemove(cardId);
    }
  };

  const dropId = list.id === 0 ? 'uncategorized' : `list-${list.id}`;

  if (cards.length === 0) {
    return (
      <DroppableList id={dropId} className="space-y-2">
        <div className="space-y-0.5">
          <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)]">
            {list.name} (0)
          </div>
          <div className="text-center py-4 text-[color:var(--theme-text-secondary)] text-sm">
            <p>No cards in this list</p>
          </div>
        </div>
      </DroppableList>
    );
  }

  return (
    <DroppableList id={dropId} className="space-y-2">
      <div className="space-y-0.5">
        {/* Section Header - matches DeckCardList */}
        <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)]">
          {list.name} ({totalCount})
        </div>
        
        {/* Card List - matches DeckCardList layout exactly */}
        <div>
          {cards.map((deckCard) => {
            const manaCost = deckCard.card.mana_cost || '';
            
            return (
              <DraggableCard key={deckCard.card_id} card={deckCard}>
                <div
                  className="flex items-center gap-2 px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm cursor-pointer"
                  onMouseEnter={() => onCardHover?.(deckCard)}
                  onMouseLeave={() => onCardHover?.(null)}
                  onClick={() => onCardClick?.(deckCard)}
                >
                  {/* Quantity */}
                  <span className="flex-shrink-0 w-5 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                    {deckCard.quantity}x
                  </span>
                  
                  {/* Card Name */}
                  <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] truncate text-xs">
                    {deckCard.card.name}
                  </span>
                  
                  {/* Mana Cost */}
                  {manaCost && (
                    <span className="flex-shrink-0 text-[color:var(--theme-accent-primary)] font-mono text-xs">
                      {manaCost}
                    </span>
                  )}
                  
                  {/* Controls */}
                  {showControls && (
                    <div className="flex items-center gap-0.5 flex-shrink-0">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleQuantityChange(deckCard.card_id, -1); }}
                        disabled={deckCard.quantity <= 1}
                        className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-xs"
                        title="Decrease"
                      >
                        −
                      </button>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleQuantityChange(deckCard.card_id, 1); }}
                        className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded transition-colors text-xs"
                        title="Increase"
                      >
                        +
                      </button>
                      {onRemove && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleRemove(deckCard.card_id); }}
                          className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20 rounded transition-colors text-xs"
                          title="Remove"
                        >
                          ×
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </DraggableCard>
            );
          })}
        </div>
      </div>
    </DroppableList>
  );
}

