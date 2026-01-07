// frontend/components/cards/CardGrid.tsx

import { CardPreview, CardData } from './CardPreview';

interface CardGridProps {
  cards: CardData[];
}

export function CardGrid({ cards }: CardGridProps) {
  if (cards.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400 text-lg">No cards found</p>
        <p className="text-slate-500 text-sm mt-2">Try adjusting your search</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {cards.map((card) => (
        <CardPreview
          key={card.card_id}
          card={card}
          linkToDetail={true}
        />
      ))}
    </div>
  );
}

