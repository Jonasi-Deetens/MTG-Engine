'use client';

// frontend/components/decks/CommanderSelector.tsx

import { useState } from 'react';
import { CardData } from '@/components/cards/CardPreview';
import { CardPreview } from '@/components/cards/CardPreview';
import { Button } from '@/components/ui/Button';
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
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Commanders</h3>
        {commanders.length === 0 ? (
          <p className="text-slate-400 text-sm">No commanders selected</p>
        ) : (
          <div className="flex gap-4 flex-wrap">
            {commanders.map((commander, index) => (
              <div key={commander.card_id} className="relative group">
                <CardPreview card={commander} />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemove(commander.card_id);
                  }}
                  className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-600 hover:bg-red-500 text-white flex items-center justify-center shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-10"
                  title="Remove commander"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                <p className="text-xs text-center text-slate-400 mt-1">
                  Commander {index + 1}
                </p>
              </div>
            ))}
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
              className="flex-1 px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none"
            />
            <Button
              onClick={handleSearch}
              disabled={searching || !searchQuery.trim()}
              variant="primary"
            >
              {searching ? 'Searching...' : 'Search'}
            </Button>
          </div>

          {searchResults.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-800 rounded-lg">
              {searchResults.map((card) => (
                <div
                  key={card.card_id}
                  className="cursor-pointer hover:scale-105 transition-transform"
                  onClick={() => handleAddCommander(card)}
                >
                  <CardPreview card={card} />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {!canAddMore && (
        <p className="text-slate-400 text-sm">Maximum {maxCommanders} commanders allowed</p>
      )}
    </div>
  );
}

