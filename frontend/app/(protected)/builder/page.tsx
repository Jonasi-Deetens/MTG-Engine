'use client';

// frontend/app/(protected)/builder/page.tsx

import { useState } from 'react';
import { useBuilderStore, CardData } from '@/store/builderStore';
import { cards } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { CardPreview } from '@/components/cards/CardPreview';
import { AbilityTabs } from '@/components/builder/AbilityTabs';
import { ValidationPanel } from '@/components/builder/ValidationPanel';

export default function BuilderPage() {
  const { currentCard, setCurrentCard } = useBuilderStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGetRandomCard = async () => {
    setLoading(true);
    setError('');
    try {
      const card = await cards.getRandom();
      setCurrentCard(card as CardData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch random card');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4">
      <div className="max-w-7xl mx-auto space-y-4">
        {/* Top Section: Card Preview */}
        <div className="bg-slate-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-white">Ability Builder</h1>
            <Button
              onClick={handleGetRandomCard}
              disabled={loading}
              className="bg-amber-600 hover:bg-amber-700"
            >
              {loading ? 'Loading...' : 'Get Random Card'}
            </Button>
          </div>
          {error && (
            <div className="mb-4 p-3 bg-red-900/50 text-red-200 rounded text-sm">
              {error}
            </div>
          )}
          {currentCard && (
            <div className="flex items-center gap-6">
              <div className="w-48">
                <CardPreview card={currentCard} />
              </div>
              <div className="flex-1 text-slate-300">
                <h2 className="text-xl font-semibold text-white mb-2">{currentCard.name}</h2>
                {currentCard.mana_cost && (
                  <p className="text-sm mb-1">
                    <span className="text-slate-400">Cost:</span> {currentCard.mana_cost}
                  </p>
                )}
                {currentCard.type_line && (
                  <p className="text-sm mb-1">
                    <span className="text-slate-400">Type:</span> {currentCard.type_line}
                  </p>
                )}
                {currentCard.power && currentCard.toughness && (
                  <p className="text-sm">
                    <span className="text-slate-400">P/T:</span> {currentCard.power}/{currentCard.toughness}
                  </p>
                )}
              </div>
            </div>
          )}
          {!currentCard && (
            <div className="text-center py-8 text-slate-500">
              <p>No card selected</p>
              <p className="text-sm mt-2">Click "Get Random Card" to start building abilities</p>
            </div>
          )}
        </div>

        {/* Main Section: Ability Builder Tabs */}
        <div className="bg-slate-800 rounded-lg p-6 min-h-[500px]">
          <AbilityTabs />
        </div>

        {/* Bottom Section: Validation */}
        <div className="bg-slate-800 rounded-lg p-6">
          <ValidationPanel />
        </div>
      </div>
    </div>
  );
}

