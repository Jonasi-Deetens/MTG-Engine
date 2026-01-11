'use client';

// frontend/components/decks/DeckCardList.tsx

import { useMemo } from 'react';
import { DeckCardResponse } from '@/lib/decks';

interface DeckCardListProps {
  cards: DeckCardResponse[];
  onQuantityChange?: (cardId: string, quantity: number) => void;
  onRemove?: (cardId: string) => void;
  showControls?: boolean;
  filterTypes?: CardType[];
  onCardHover?: (card: DeckCardResponse | null) => void;
  onCardClick?: (card: DeckCardResponse) => void;
}

type CardType = 'Creature' | 'Instant' | 'Sorcery' | 'Artifact' | 'Enchantment' | 'Planeswalker' | 'Land' | 'Other';

function getCardType(typeLine: string | null | undefined): CardType {
  if (!typeLine) return 'Other';
  
  const typeLineLower = typeLine.toLowerCase();
  
  if (typeLineLower.includes('creature')) return 'Creature';
  if (typeLineLower.includes('instant')) return 'Instant';
  if (typeLineLower.includes('sorcery')) return 'Sorcery';
  if (typeLineLower.includes('planeswalker')) return 'Planeswalker';
  if (typeLineLower.includes('land')) return 'Land';
  if (typeLineLower.includes('enchantment') && !typeLineLower.includes('creature')) return 'Enchantment';
  if (typeLineLower.includes('artifact') && !typeLineLower.includes('creature')) return 'Artifact';
  
  return 'Other';
}

const TYPE_ORDER: CardType[] = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Other'];
const TYPE_LABELS: Record<CardType, string> = {
  'Creature': 'Creatures',
  'Instant': 'Instants',
  'Sorcery': 'Sorceries',
  'Artifact': 'Artifacts',
  'Enchantment': 'Enchantments',
  'Planeswalker': 'Planeswalkers',
  'Land': 'Lands',
  'Other': 'Other',
};

export function DeckCardList({ cards, onQuantityChange, onRemove, showControls = true, filterTypes, onCardHover, onCardClick }: DeckCardListProps) {
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

  // Group cards by type
  const groupedCards = useMemo(() => {
    const groups: Record<CardType, DeckCardResponse[]> = {
      'Creature': [],
      'Instant': [],
      'Sorcery': [],
      'Artifact': [],
      'Enchantment': [],
      'Planeswalker': [],
      'Land': [],
      'Other': [],
    };

    cards.forEach((deckCard) => {
      const type = getCardType(deckCard.card.type_line);
      groups[type].push(deckCard);
    });

    // Sort cards within each group by name
    Object.keys(groups).forEach((type) => {
      groups[type as CardType].sort((a, b) => a.card.name.localeCompare(b.card.name));
    });

    return groups;
  }, [cards]);

  // Filter types if specified
  const displayTypes = filterTypes || TYPE_ORDER;

  if (cards.length === 0) {
    return (
      <div className="text-center py-4 text-[color:var(--theme-text-secondary)] text-sm">
        <p>No cards in deck</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {displayTypes.map((type) => {
        const typeCards = groupedCards[type];
        if (typeCards.length === 0) return null;

        const totalCount = typeCards.reduce((sum, card) => sum + card.quantity, 0);

        return (
          <div key={type} className="space-y-0.5">
            {/* Section Header */}
            <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)]">
              {TYPE_LABELS[type]} ({totalCount})
            </div>
            
            {/* Card List - Contact List Style */}
            <div>
              {typeCards.map((deckCard) => {
                const manaCost = deckCard.card.mana_cost || '';
                
                return (
                <div
                  key={deckCard.card_id}
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
                          onClick={() => handleQuantityChange(deckCard.card_id, -1)}
                          disabled={deckCard.quantity <= 1}
                          className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-xs"
                          title="Decrease"
                        >
                          −
                        </button>
                        <button
                          onClick={() => handleQuantityChange(deckCard.card_id, 1)}
                          className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded transition-colors text-xs"
                          title="Increase"
                        >
                          +
                        </button>
                        {onRemove && (
                          <button
                            onClick={() => handleRemove(deckCard.card_id)}
                            className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20 rounded transition-colors text-xs"
                            title="Remove"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

