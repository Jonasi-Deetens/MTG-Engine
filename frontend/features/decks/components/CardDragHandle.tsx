'use client';

// frontend/components/decks/CardDragHandle.tsx

import { useDraggable } from '@dnd-kit/core';
import { DeckCardResponse } from '@/lib/decks';

interface CardDragHandleProps {
  card: DeckCardResponse;
  children: React.ReactNode;
  onHover?: (card: DeckCardResponse | null) => void;
  onClick?: (card: DeckCardResponse) => void;
}

export function CardDragHandle({ card, children, onHover, onClick }: CardDragHandleProps) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `card-${card.card_id}`,
    data: {
      card,
    },
  });

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`cursor-grab active:cursor-grabbing flex-1 min-w-0 ${isDragging ? 'opacity-50' : ''}`}
      onMouseEnter={() => onHover?.(card)}
      onMouseLeave={() => onHover?.(null)}
      onClick={() => onClick?.(card)}
    >
      {children}
    </div>
  );
}

