'use client';

// frontend/features/decks/components/EditableTypeList.tsx

import { useState, useEffect } from 'react';
import { DeckCardResponse, DeckCustomListResponse } from '@/lib/decks';
import { DroppableList } from './DroppableList';
import { CardDragHandle } from './CardDragHandle';
import { CardType, DEFAULT_TYPE_LABELS, getCardType } from '@/lib/utils/cardTypes';

interface EditableTypeListProps {
  type: CardType;
  list: DeckCustomListResponse | null;
  cards: DeckCardResponse[];
  onQuantityChange?: (cardId: string, quantity: number) => void;
  onRemove?: (cardId: string) => void;
  onCardHover?: (card: DeckCardResponse | null) => void;
  onCardClick?: (card: DeckCardResponse) => void;
  onRename?: (type: CardType, newName: string, listId?: number) => void;
  showControls?: boolean;
}

export function EditableTypeList({
  type,
  list,
  cards,
  onQuantityChange,
  onRemove,
  onCardHover,
  onCardClick,
  onRename,
  showControls = true,
}: EditableTypeListProps) {
  const [isEditing, setIsEditing] = useState(false);
  const displayName = list?.name || DEFAULT_TYPE_LABELS[type];
  const [editName, setEditName] = useState(displayName);
  
  // Update editName when list name or ID changes (but not while editing)
  useEffect(() => {
    if (!isEditing) {
      const newDisplayName = list?.name || DEFAULT_TYPE_LABELS[type];
      setEditName(newDisplayName);
    }
  }, [list?.name, list?.id, type, isEditing]);
  
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

  const handleRename = () => {
    if (editName.trim() && editName !== displayName && onRename) {
      onRename(type, editName.trim(), list?.id);
    } else {
      // Reset to current name if unchanged
      setEditName(displayName);
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRename();
    } else if (e.key === 'Escape') {
      setEditName(displayName);
      setIsEditing(false);
    }
  };

  const dropId = list ? `list-${list.id}` : `type-${type}`;

  return (
    <DroppableList id={dropId} className="space-y-2">
      <div className="space-y-0.5">
        {/* Editable Section Header */}
        <div className="px-1.5 py-1 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)] flex items-center gap-2 group">
          {isEditing ? (
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onBlur={handleRename}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent border-b border-[color:var(--theme-accent-primary)] focus:outline-none text-[color:var(--theme-text-primary)]"
              autoFocus
            />
          ) : (
            <>
              <span 
                className="flex-1 cursor-pointer hover:text-[color:var(--theme-text-primary)]"
                onDoubleClick={() => setIsEditing(true)}
                title="Double-click to rename"
              >
                {displayName} ({totalCount})
              </span>
              <button
                onClick={() => setIsEditing(true)}
                className="opacity-0 group-hover:opacity-100 transition-opacity text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]"
                title="Rename list"
              >
                ✎
              </button>
            </>
          )}
        </div>
        
        {/* Card List */}
        {cards.length === 0 ? (
          <div className="text-center py-4 text-[color:var(--theme-text-secondary)] text-sm">
            <p>No cards in this list</p>
          </div>
        ) : (
          <div className="min-w-0 overflow-hidden">
            {cards.map((deckCard) => {
            const manaCost = deckCard.card.mana_cost || '';
            
            return (
              <div
                key={deckCard.card_id}
                className="flex items-center gap-2 px-1.5 py-0.5 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm min-w-0"
              >
                {/* Drag Handle Area - Quantity, Name, Mana Cost */}
                <CardDragHandle
                  card={deckCard}
                  onHover={onCardHover}
                  onClick={onCardClick}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0 overflow-hidden">
                    {/* Quantity */}
                    <span className="flex-shrink-0 w-5 text-right text-xs font-medium text-[color:var(--theme-accent-primary)]">
                      {deckCard.quantity}x
                    </span>
                    
                    {/* Card Name */}
                    <span className="flex-1 min-w-0 text-[color:var(--theme-text-primary)] truncate text-xs overflow-hidden">
                      {deckCard.card.name}
                    </span>
                    
                    {/* Mana Cost */}
                    {manaCost && (
                      <span className="flex-shrink-0 text-[color:var(--theme-accent-primary)] font-mono text-xs">
                        {manaCost}
                      </span>
                    )}
                  </div>
                </CardDragHandle>
                
                {/* Controls - Not draggable */}
                {showControls && (
                  <div 
                    className="flex items-center gap-0.5 flex-shrink-0"
                    onMouseDown={(e) => e.stopPropagation()}
                    onClick={(e) => e.stopPropagation()}
                  >
                    <button
                      onClick={(e) => { e.stopPropagation(); handleQuantityChange(deckCard.card_id, -1); }}
                      onMouseDown={(e) => { e.stopPropagation(); }}
                      disabled={deckCard.quantity <= 1}
                      className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-xs"
                      title="Decrease"
                    >
                      −
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleQuantityChange(deckCard.card_id, 1); }}
                      onMouseDown={(e) => { e.stopPropagation(); }}
                      className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-card-hover)] rounded transition-colors text-xs"
                      title="Increase"
                    >
                      +
                    </button>
                    {onRemove && (
                      <button
                        onClick={(e) => { e.stopPropagation(); handleRemove(deckCard.card_id); }}
                        onMouseDown={(e) => { e.stopPropagation(); }}
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
        )}
      </div>
    </DroppableList>
  );
}

// Re-export for backwards compatibility
export { getCardType, type CardType, DEFAULT_TYPE_LABELS };
