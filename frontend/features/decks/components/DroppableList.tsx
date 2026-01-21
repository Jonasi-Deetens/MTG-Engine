'use client';

// frontend/components/decks/DroppableList.tsx

import { useDroppable } from '@dnd-kit/core';
import { cn } from '@/lib/utils';

interface DroppableListProps {
  id: string;
  children: React.ReactNode;
  className?: string;
}

export function DroppableList({ id, children, className }: DroppableListProps) {
  const { setNodeRef, isOver } = useDroppable({
    id,
  });

  return (
    <div
      ref={setNodeRef}
      className={cn(
        'transition-colors',
        isOver && 'bg-[color:var(--theme-accent-primary)]/10 border-2 border-[color:var(--theme-accent-primary)] rounded-lg',
        className
      )}
    >
      {children}
    </div>
  );
}

