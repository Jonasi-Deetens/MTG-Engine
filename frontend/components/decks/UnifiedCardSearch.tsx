'use client';

// frontend/components/decks/UnifiedCardSearch.tsx

import { useState, useEffect } from 'react';
import { CardData } from '@/components/cards/CardPreview';
import { cards } from '@/lib/api';
import { SearchInput } from '@/components/ui/SearchInput';
import { useDebounce } from '@/lib/hooks';

interface UnifiedCardSearchProps {
  onAddCard?: (card: CardData) => void;
  onAddCommander?: (card: CardData) => void;
  isCommanderFormat?: boolean;
  maxCommanders?: number;
  currentCommanderCount?: number;
}

export function UnifiedCardSearch({
  onAddCard,
  onAddCommander,
  isCommanderFormat = false,
  maxCommanders = 2,
  currentCommanderCount = 0,
}: UnifiedCardSearchProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CardData[]>([]);
  const [searching, setSearching] = useState(false);
  const debouncedQuery = useDebounce(searchQuery, 500);

  useEffect(() => {
    if (debouncedQuery.trim()) {
      setSearching(true);
      cards.search(debouncedQuery, 1, 20)
        .then(response => {
          setSearchResults(response.cards);
        })
        .catch(err => {
          console.error('Search failed:', err);
          setSearchResults([]);
        })
        .finally(() => {
          setSearching(false);
        });
    } else {
      setSearchResults([]);
    }
  }, [debouncedQuery]);

  const canAddCommander = isCommanderFormat && currentCommanderCount < maxCommanders;

  return (
    <div className="space-y-2">
      <SearchInput
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search for cards or commanders..."
        size="sm"
      />
      
      {searching && (
        <div className="text-xs text-[color:var(--theme-text-secondary)] py-1">Searching...</div>
      )}
      
      {!searching && searchResults.length > 0 && (
        <div className="space-y-0.5 max-h-48 overflow-y-auto border border-[color:var(--theme-card-border)] rounded p-1.5">
          {searchResults.map((card) => {
            const manaCost = card.mana_cost || '';
            
            return (
              <div
                key={card.card_id}
                className="flex items-center gap-2 px-1.5 py-1 hover:bg-[color:var(--theme-card-hover)] rounded text-xs transition-colors"
              >
                <span className="text-[color:var(--theme-text-primary)] flex-1">
                  {card.name}
                </span>
                {manaCost && (
                  <span className="text-[color:var(--theme-accent-primary)] font-mono text-xs">
                    {manaCost}
                  </span>
                )}
                <div className="flex gap-1 flex-shrink-0">
                  {onAddCard && (
                    <button
                      onClick={() => {
                        onAddCard(card);
                        setSearchQuery('');
                        setSearchResults([]);
                      }}
                      className="px-2 py-0.5 text-xs bg-[color:var(--theme-button-primary-bg)] text-[color:var(--theme-button-primary-text)] rounded hover:opacity-90 transition-opacity"
                    >
                      Add Card
                    </button>
                  )}
                  {onAddCommander && canAddCommander && (
                    <button
                      onClick={() => {
                        onAddCommander(card);
                        setSearchQuery('');
                        setSearchResults([]);
                      }}
                      className="px-2 py-0.5 text-xs bg-[color:var(--theme-accent-primary)]/20 text-[color:var(--theme-accent-primary)] rounded hover:bg-[color:var(--theme-accent-primary)]/30 transition-colors"
                    >
                      Add Commander
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
      
      {!searching && debouncedQuery && searchResults.length === 0 && (
        <p className="text-xs text-[color:var(--theme-text-secondary)] text-center py-1">No cards found</p>
      )}
    </div>
  );
}

