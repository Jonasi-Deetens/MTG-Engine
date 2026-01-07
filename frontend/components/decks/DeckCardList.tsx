'use client';

// frontend/components/decks/DeckCardList.tsx

import { DeckCardResponse } from '@/lib/decks';
import { CardPreview } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';

interface DeckCardListProps {
  cards: DeckCardResponse[];
  onQuantityChange?: (cardId: string, quantity: number) => void;
  onRemove?: (cardId: string) => void;
  showControls?: boolean;
}

export function DeckCardList({ cards, onQuantityChange, onRemove, showControls = true }: DeckCardListProps) {
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

  if (cards.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400">
        <p>No cards in deck</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {cards.map((deckCard) => (
        <div
          key={deckCard.card_id}
          className="flex items-center gap-4 p-3 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors"
        >
          <div className="flex-shrink-0 w-16">
            <CardPreview card={deckCard.card} />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-white truncate">{deckCard.card.name}</h4>
            <p className="text-sm text-slate-400">{deckCard.card.type_line}</p>
            {deckCard.card.mana_cost && (
              <p className="text-sm text-amber-400 font-mono">{deckCard.card.mana_cost}</p>
            )}
          </div>
          {showControls && (
            <div className="flex items-center gap-2">
              <Button
                onClick={() => handleQuantityChange(deckCard.card_id, -1)}
                variant="outline"
                size="sm"
                disabled={deckCard.quantity <= 1}
              >
                -
              </Button>
              <span className="w-12 text-center font-semibold text-white">
                {deckCard.quantity}
              </span>
              <Button
                onClick={() => handleQuantityChange(deckCard.card_id, 1)}
                variant="outline"
                size="sm"
              >
                +
              </Button>
              {onRemove && (
                <Button
                  onClick={() => handleRemove(deckCard.card_id)}
                  variant="outline"
                  size="sm"
                  className="text-red-400 hover:text-red-300"
                >
                  Remove
                </Button>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

