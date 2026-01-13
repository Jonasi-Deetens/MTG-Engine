'use client';

// frontend/components/decks/DraggableCard.tsx

import { useDraggable } from '@dnd-kit/core';
import { DeckCardResponse } from '@/lib/decks';

interface DraggableCardProps {
  card: DeckCardResponse;
  children: React.ReactNode;
}

export function DraggableCard({ card, children }: DraggableCardProps) {
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
      className={isDragging ? 'opacity-50' : ''}
    >
      {children}
    </div>
  );
}

// Export a hook to get drag handle props
export function useDragHandle() {
  const { attributes, listeners } = useDraggable({
    id: '', // Will be set by parent
  });
  
  return {
    ...listeners,
    ...attributes,
    style: { cursor: 'grab' } as React.CSSProperties,
  };
}

