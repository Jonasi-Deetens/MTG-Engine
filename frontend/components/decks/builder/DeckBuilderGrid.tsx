// frontend/components/decks/builder/DeckBuilderGrid.tsx

import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardType, DEFAULT_TYPE_LABELS } from '@/lib/utils/cardTypes';
import { EditableTypeList } from '@/components/decks/EditableTypeList';
import { getCardsForType, findListForType } from '@/utils/deckBuilder/cardGrouping';
import { CardData } from '@/components/cards/CardPreview';

interface DeckBuilderGridProps {
  cards: DeckCardResponse[];
  typeLists: DeckCustomListResponse[];
  deckFormat: string;
  onQuantityChange: (cardId: string, quantity: number) => void;
  onRemove: (cardId: string) => void;
  onCardHover: (card: DeckCardResponse | null) => void;
  onCardClick: (card: CardData) => void;
  onRename: (type: CardType, newName: string, listId?: number) => void;
}

export function DeckBuilderGrid({
  cards,
  typeLists,
  deckFormat,
  onQuantityChange,
  onRemove,
  onCardHover,
  onCardClick,
  onRename,
}: DeckBuilderGridProps) {
  const renderTypeList = (type: CardType) => {
    const list = findListForType(type, typeLists, cards);
    const typeCards = getCardsForType(type, cards, typeLists);
    
    return (
      <EditableTypeList
        key={list ? `list-${list.id}` : `type-${type}`}
        type={type}
        list={list || null}
        cards={typeCards}
        onQuantityChange={onQuantityChange}
        onRemove={onRemove}
        onCardHover={onCardHover}
        onCardClick={(deckCard) => onCardClick(deckCard.card)}
        onRename={onRename}
        showControls={true}
      />
    );
  };

  return (
    <>
      {/* Left Section - 2 Columns */}
      <div className="grid grid-cols-2 gap-x-4">
        {/* Left Column 1 - Creatures */}
        <div className="min-w-0">
          {renderTypeList('Creature')}
        </div>

        {/* Left Column 2 - Instants & Sorceries */}
        <div className="space-y-2 min-w-0">
          {(['Instant', 'Sorcery'] as CardType[]).map(type => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>
      </div>

      {/* Right Section - 2 Columns */}
      <div className="grid grid-cols-2 gap-x-4">
        {/* Right Column 1 - Artifacts & Enchantments */}
        <div className="space-y-2 min-w-0">
          {(['Artifact', 'Enchantment'] as CardType[]).map(type => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>

        {/* Right Column 2 - Lands, Planeswalkers & Other */}
        <div className="space-y-2 min-w-0">
          {(['Land', 'Planeswalker', 'Other'] as CardType[]).map(type => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

