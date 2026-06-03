'use client';

// frontend/components/decks/CommanderSelector.tsx

import { useState } from 'react';
import { CardData } from '@/components/cards/CardPreview';
import { cards } from '@/lib/api';

interface CommanderSelectorProps {
  commanders: CardData[];
  onAdd: (cardId: string, position: number) => void;
  onRemove: (cardId: string) => void;
  maxCommanders?: number;
}

export function CommanderSelector({ commanders, onAdd, onRemove, maxCommanders = 2 }: CommanderSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<CardData[]>([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const response = await cards.search(searchQuery, 1, 10);
      setSearchResults(response.cards);
    } catch (err) {
      console.error('Failed to search cards:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleAddCommander = (card: CardData) => {
    const position = commanders.length;
    if (position < maxCommanders) {
      onAdd(card.card_id, position);
      setSearchQuery('');
      setSearchResults([]);
    }
  };

  const canAddMore = commanders.length < maxCommanders;

  return (
    <div className="space-y-2">
      <div>
        <div className="px-2 py-1.5 text-xs font-semibold text-[color:var(--theme-text-secondary)] uppercase tracking-wide border-b border-[color:var(--theme-card-border)] mb-0.5">
          Commander{commanders.length > 1 ? 's' : ''} ({commanders.length})
        </div>
        {commanders.length === 0 ? (
          <p className="px-2 py-1 text-[color:var(--theme-text-secondary)] text-xs">No commanders selected</p>
        ) : (
          <div className="divide-y divide-[color:var(--theme-card-border)]">
            {commanders.map((commander, index) => {
              const manaCost = commander.mana_cost || '';
              
              return (
                <div
                  key={commander.card_id}
                  className="flex items-center gap-3 px-2 py-1 hover:bg-[color:var(--theme-card-hover)] transition-colors text-sm"
                >
                  <button
                    onClick={() => onRemove(commander.card_id)}
                    className="w-5 h-5 flex items-center justify-center text-[color:var(--theme-status-error)] hover:bg-[color:var(--theme-status-error)]/20 rounded transition-colors text-xs flex-shrink-0"
                    title="Remove commander"
                  >
                    ×
                  </button>
                  <span className="text-xs text-[color:var(--theme-text-secondary)] flex-shrink-0 w-4">
                    {index + 1}.
                  </span>
                  <span className="font-medium text-[color:var(--theme-text-primary)] flex-1">
                    {commander.name}
                  </span>
                  {manaCost && (
                    <span className="text-[color:var(--theme-accent-primary)] font-mono text-xs flex-shrink-0">
                      {manaCost}
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {canAddMore && (
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search for commander..."
              className="flex-1 px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
            <button
              onClick={handleSearch}
              disabled={searching || !searchQuery.trim()}
              className="px-3 py-1.5 text-sm bg-[color:var(--theme-accent-primary)] text-[color:var(--theme-button-primary-text)] rounded hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              {searching ? '...' : 'Search'}
            </button>
          </div>

          {searchResults.length > 0 && (
            <div className="space-y-1 max-h-48 overflow-y-auto border border-[color:var(--theme-card-border)] rounded p-2">
              {searchResults.map((card) => {
                const manaCost = card.mana_cost || '';
                const typeLine = card.type_line || '';
                
                return (
                  <button
                    key={card.card_id}
                    onClick={() => handleAddCommander(card)}
                    className="w-full text-left px-2 py-1.5 hover:bg-[color:var(--theme-card-hover)] rounded text-sm transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-[color:var(--theme-text-primary)] flex-1">
                        {card.name}
                      </span>
                      {manaCost && (
                        <span className="text-[color:var(--theme-accent-primary)] font-mono text-xs">
                          ({manaCost})
                        </span>
                      )}
                      {typeLine && (
                        <span className="text-[color:var(--theme-text-secondary)] text-xs">
                          - {typeLine}
                        </span>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}

      {!canAddMore && (
        <p className="text-[color:var(--theme-text-secondary)] text-xs">Maximum {maxCommanders} commanders allowed</p>
      )}
    </div>
  );
}

