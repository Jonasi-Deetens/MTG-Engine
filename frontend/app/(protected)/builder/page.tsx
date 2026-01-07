'use client';

// frontend/app/(protected)/builder/page.tsx

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useBuilderStore, CardData } from '@/store/builderStore';
import { cards } from '@/lib/api';
import { abilities } from '@/lib/abilities';
import { Button } from '@/components/ui/Button';
import { CardPreview } from '@/components/cards/CardPreview';
import { AbilityTabs } from '@/components/builder/AbilityTabs';
import { ValidationPanel } from '@/components/builder/ValidationPanel';
import { AbilityTreeView } from '@/components/builder/AbilityTreeView';

export default function BuilderPage() {
  const searchParams = useSearchParams();
  const { currentCard, setCurrentCard, loadFromGraph, clearAll } = useBuilderStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [searching, setSearching] = useState(false);

  const handleGetRandomCard = async () => {
    setLoading(true);
    setError('');
    setSearchTerm('');
    try {
      const card = await cards.getRandom();
      console.log('Random card received:', card);
      console.log('Card ID:', card?.card_id);
      if (!card?.card_id) {
        console.error('Card missing card_id!', card);
        setError('Card data is invalid - missing card ID');
        return;
      }
      // Clear abilities first before setting new card
      clearAll();
      setCurrentCard(card as CardData);
      // Try to load saved graph for this card
      await loadSavedGraph(card.card_id);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch random card');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchCard = async () => {
    if (!searchTerm.trim()) {
      setError('Please enter a card name');
      return;
    }

    setSearching(true);
    setError('');
    try {
      const results = await cards.search(searchTerm, 1, 1);
      if (results.cards && results.cards.length > 0) {
        const card = results.cards[0] as CardData;
        console.log('Search card received:', card);
        console.log('Card ID:', card?.card_id);
        if (!card?.card_id) {
          console.error('Card missing card_id!', card);
          setError('Card data is invalid - missing card ID');
          return;
        }
        // Clear abilities first before setting new card
        clearAll();
        setCurrentCard(card);
        setSearchTerm('');
        // Try to load saved graph for this card
        await loadSavedGraph(card.card_id);
      } else {
        setError(`No card found with name "${searchTerm}"`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to search for card');
    } finally {
      setSearching(false);
    }
  };

  const handleSearchKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearchCard();
    }
  };

  const loadSavedGraph = async (cardId: string) => {
    try {
      console.log('Loading graph for card_id:', cardId);
      const saved = await abilities.getCardGraph(cardId);
      console.log('Loaded graph response:', saved);
      if (saved && saved.ability_graph) {
        // Load the saved graph into the store (abilities already cleared before this)
        loadFromGraph(saved.ability_graph);
        console.log('Graph loaded into store');
      }
    } catch (err: any) {
      // Graph doesn't exist yet, that's fine - abilities already cleared
      if (err.status === 404) {
        console.log('No saved graph found for card_id:', cardId);
      } else {
        console.error('Error loading saved graph:', err);
      }
    }
  };

  const handleVersionChange = async (newCard: CardData) => {
    console.log('Version changed to:', newCard.card_id);
    // Clear abilities first
    clearAll();
    // Set new card
    setCurrentCard(newCard);
    // Load graph for new version (will check all versions)
    await loadSavedGraph(newCard.card_id);
  };

  // Load card from query parameter on mount
  useEffect(() => {
    const cardId = searchParams.get('card');
    if (cardId && (!currentCard || currentCard.card_id !== cardId)) {
      const loadCardFromQuery = async () => {
        setLoading(true);
        setError('');
        try {
          const card = await cards.getById(cardId);
          if (card?.card_id) {
            clearAll();
            setCurrentCard(card as CardData);
            await loadSavedGraph(card.card_id);
          }
        } catch (err: any) {
          setError(err?.data?.detail || err?.message || 'Failed to load card');
        } finally {
          setLoading(false);
        }
      };
      loadCardFromQuery();
    }
  }, [searchParams, currentCard, setCurrentCard, clearAll]);

  return (
    <div className="min-h-screen bg-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-4">
        {/* Top Section: Card Preview */}
        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-white">Ability Builder</h1>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  placeholder="Search card by name..."
                  className="px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none text-sm w-64"
                />
                <Button
                  onClick={handleSearchCard}
                  disabled={searching || !searchTerm.trim()}
                  variant="secondary"
                  size="sm"
                >
                  {searching ? 'Searching...' : 'Search'}
                </Button>
              </div>
              <Button
                onClick={handleGetRandomCard}
                disabled={loading}
                variant="primary"
                size="sm"
              >
                {loading ? 'Loading...' : 'Random Card'}
              </Button>
            </div>
          </div>
          {error && (
            <div className="mb-4 p-3 bg-red-900/50 text-red-200 rounded text-sm">
              {error}
            </div>
          )}
          {currentCard && (
            <div className="flex items-start gap-6">
              <div className="w-48 shrink-0">
                <CardPreview card={currentCard} onVersionChange={handleVersionChange} />
              </div>
              <div className="flex-1 text-slate-300 space-y-3">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">{currentCard.name}</h2>
                  {currentCard.mana_cost && (
                    <p className="text-base font-mono text-amber-400">
                      {currentCard.mana_cost}
                    </p>
                  )}
                </div>
                
                {currentCard.type_line && (
                  <div>
                    <span className="text-xs text-slate-400 uppercase tracking-wide">Type</span>
                    <p className="text-sm text-white mt-1">{currentCard.type_line}</p>
                  </div>
                )}
                
                {(currentCard.power && currentCard.toughness) && (
                  <div>
                    <span className="text-xs text-slate-400 uppercase tracking-wide">Power / Toughness</span>
                    <p className="text-sm text-white mt-1 font-mono">
                      {currentCard.power} / {currentCard.toughness}
                    </p>
                  </div>
                )}
                
                {currentCard.colors && currentCard.colors.length > 0 && (
                  <div>
                    <span className="text-xs text-slate-400 uppercase tracking-wide">Colors</span>
                    <div className="flex gap-2 mt-1">
                      {currentCard.colors.map((color, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 rounded text-xs font-medium bg-slate-700 text-white capitalize"
                        >
                          {color}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {currentCard.oracle_text && (
                  <div>
                    <span className="text-xs text-slate-400 uppercase tracking-wide">Oracle Text</span>
                    <p className="text-sm text-slate-200 mt-1 whitespace-pre-wrap leading-relaxed">
                      {currentCard.oracle_text}
                    </p>
                  </div>
                )}
                
                {(currentCard.set_code || currentCard.collector_number) && (
                  <div className="flex gap-4 text-xs text-slate-400">
                    {currentCard.set_code && (
                      <div>
                        <span className="uppercase tracking-wide">Set:</span>{' '}
                        <span className="text-slate-300">{currentCard.set_code.toUpperCase()}</span>
                      </div>
                    )}
                    {currentCard.collector_number && (
                      <div>
                        <span className="uppercase tracking-wide">#:</span>{' '}
                        <span className="text-slate-300">{currentCard.collector_number}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
          {!currentCard && (
            <div className="text-center py-8 text-slate-500">
              <p className="text-lg mb-2">No card selected</p>
              <p className="text-sm mb-4">Search for a card by name or click "Random Card" to start building abilities</p>
              <Link href="/getting-started">
                <Button variant="outline" size="sm">
                  View Getting Started Guide
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Main Section: Split between Tabs and Preview */}
        <div className="grid grid-cols-2 gap-4">
          {/* Left: Ability Builder Tabs */}
          <div className="bg-slate-800 rounded-lg p-6 min-h-[500px]">
            <AbilityTabs />
          </div>

          {/* Right: Tree View Preview */}
          <div className="bg-slate-800 rounded-lg p-6 min-h-[500px] overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">Ability Preview</h2>
            <AbilityTreeView />
          </div>
        </div>

        {/* Bottom Section: Validation */}
        <div className="bg-slate-800 rounded-lg p-6">
          <ValidationPanel />
        </div>
      </div>
    </div>
  );
}

