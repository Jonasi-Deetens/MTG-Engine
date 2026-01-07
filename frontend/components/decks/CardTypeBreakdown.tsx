'use client';

// frontend/components/decks/CardTypeBreakdown.tsx

import { DeckCardResponse } from '@/lib/decks';
import { useMemo } from 'react';

interface CardTypeBreakdownProps {
  cards: DeckCardResponse[];
}

export function CardTypeBreakdown({ cards }: CardTypeBreakdownProps) {
  const typeData = useMemo(() => {
    const types: { [type: string]: number } = {
      'Creature': 0,
      'Land': 0,
      'Instant': 0,
      'Sorcery': 0,
      'Enchantment': 0,
      'Artifact': 0,
      'Planeswalker': 0,
      'Other': 0,
    };
    
    cards.forEach((deckCard) => {
      const typeLine = deckCard.card.type_line || '';
      const quantity = deckCard.quantity;
      
      if (!typeLine || typeLine.trim() === '') {
        // If no type line, count as Other
        types['Other'] += quantity;
        return;
      }
      
      // Parse type line - cards can have multiple types
      // Check in order of specificity (more specific first)
      const typeLineLower = typeLine.toLowerCase().trim();
      let hasMatchedType = false;
      
      if (typeLineLower.includes('creature')) {
        types['Creature'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('land')) {
        types['Land'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('instant')) {
        types['Instant'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('sorcery')) {
        types['Sorcery'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('planeswalker')) {
        types['Planeswalker'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('enchantment') && !typeLineLower.includes('creature')) {
        types['Enchantment'] += quantity;
        hasMatchedType = true;
      }
      if (typeLineLower.includes('artifact') && !typeLineLower.includes('creature')) {
        types['Artifact'] += quantity;
        hasMatchedType = true;
      }
      
      // If none matched, count as Other
      if (!hasMatchedType) {
        types['Other'] += quantity;
      }
    });
    
    return Object.entries(types)
      .filter(([, count]) => count > 0)
      .map(([type, count]) => ({ type, count }));
  }, [cards]);
  
  const total = typeData.reduce((sum, item) => sum + item.count, 0);
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-red-500',
    'bg-yellow-500',
    'bg-purple-500',
    'bg-cyan-500',
    'bg-orange-500',
    'bg-pink-500',
  ];
  
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-white">Card Types</h3>
      <div className="space-y-2">
        {typeData.map((item, index) => {
          const percentage = total > 0 ? (item.count / total) * 100 : 0;
          return (
            <div key={item.type} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-300">{item.type}</span>
                <span className="text-slate-400">{item.count} ({percentage.toFixed(1)}%)</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div
                  className={`${colors[index % colors.length]} h-2 rounded-full transition-all`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
      {typeData.length === 0 && (
        <p className="text-slate-400 text-sm">No cards to analyze</p>
      )}
    </div>
  );
}

