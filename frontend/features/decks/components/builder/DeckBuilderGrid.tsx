// frontend/components/decks/builder/DeckBuilderGrid.tsx

import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { CardType, DEFAULT_TYPE_LABELS } from '@/lib/utils/cardTypes';
import { EditableTypeList } from '../EditableTypeList';
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
  middleContent?: React.ReactNode;
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
  middleContent,
}: DeckBuilderGridProps) {
  const renderTypeList = (type: CardType) => {
    const list = findListForType(type, typeLists);
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
    <div className="grid grid-cols-1 xl:grid-cols-[2fr_1fr_2fr] gap-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 min-w-0">
        <div className="min-w-0">
          {renderTypeList('Creature')}
        </div>
        <div className="space-y-4 min-w-0">
          {(['Instant', 'Sorcery'] as CardType[]).map((type) => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4 min-w-0">
        {middleContent}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 min-w-0">
        <div className="space-y-4 min-w-0">
          {(['Artifact', 'Enchantment'] as CardType[]).map((type) => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>
        <div className="space-y-4 min-w-0">
          {(['Land', 'Planeswalker', 'Other'] as CardType[]).map((type) => (
            <div key={type}>
              {renderTypeList(type)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

