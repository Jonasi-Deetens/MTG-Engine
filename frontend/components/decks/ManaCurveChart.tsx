'use client';

// frontend/components/decks/ManaCurveChart.tsx

import { DeckCardResponse } from '@/lib/decks';
import { useMemo } from 'react';

interface ManaCurveChartProps {
  cards: DeckCardResponse[];
}

export function ManaCurveChart({ cards }: ManaCurveChartProps) {
  const curveData = useMemo(() => {
    const curve: { [cmc: number]: number } = {};
    
    cards.forEach((deckCard) => {
      // Use mana_value if available (more accurate)
      let cmc = 0;
      if (deckCard.card.mana_value !== undefined && deckCard.card.mana_value !== null) {
        cmc = deckCard.card.mana_value;
      } else if (deckCard.card.mana_cost) {
        // Fallback to parsing mana cost
        cmc = parseManaCost(deckCard.card.mana_cost);
      }
      // Lands and cards without mana cost go to CMC 0
      
      curve[cmc] = (curve[cmc] || 0) + deckCard.quantity;
    });
    
    // Fill in missing CMC values from 0 to 7+
    const result: { cmc: number; count: number }[] = [];
    for (let i = 0; i <= 7; i++) {
      result.push({ cmc: i, count: curve[i] || 0 });
    }
    
    // Add 7+ category for anything higher
    const sevenPlus = Object.entries(curve)
      .filter(([cmc]) => parseInt(cmc) > 7)
      .reduce((sum, [, count]) => sum + count, 0);
    if (sevenPlus > 0) {
      result.push({ cmc: 8, count: sevenPlus }); // Use 8 to represent 7+
    }
    
    return result;
  }, [cards]);
  
  const maxCount = Math.max(...curveData.map(d => d.count), 1);
  
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold text-white">Mana Curve</h3>
      {cards.length === 0 ? (
        <p className="text-slate-400 text-sm">No cards to analyze</p>
      ) : (
        <div className="flex items-end gap-1 h-48">
          {curveData.map((data) => {
            // Calculate height as percentage of max count
            const heightPercent = maxCount > 0 ? (data.count / maxCount) * 100 : 0;
            // Ensure minimum 2% height for visibility when count > 0
            const finalHeightPercent = data.count > 0 ? Math.max(heightPercent, 2) : 0;
            
            return (
              <div key={data.cmc} className="flex-1 flex flex-col items-center gap-1 min-w-0 h-full">
                <div className="w-full h-full flex flex-col justify-end">
                  {data.count > 0 && (
                    <div
                      className="w-full bg-amber-500 rounded-t transition-all hover:bg-amber-400"
                      style={{ 
                        height: `${finalHeightPercent}%`,
                      }}
                      title={`CMC ${data.cmc === 8 ? '7+' : data.cmc}: ${data.count} cards`}
                    />
                  )}
                </div>
                <div className="flex flex-col items-center gap-0.5 mt-1">
                  <span className="text-xs text-slate-400 font-mono">
                    {data.cmc === 8 ? '7+' : data.cmc}
                  </span>
                  <span className="text-xs text-slate-500">
                    {data.count}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function parseManaCost(manaCost: string): number {
  // Remove curly braces and count symbols
  // This is simplified - real parsing would handle hybrid mana, X costs, etc.
  const cleaned = manaCost.replace(/{/g, '').replace(/}/g, '');
  let cmc = 0;
  
  for (const char of cleaned) {
    if (char === 'X' || char === 'x') {
      // X costs are typically 0 for curve purposes
      continue;
    } else if (char >= '0' && char <= '9') {
      cmc += parseInt(char);
    } else {
      // Colored mana symbols count as 1
      cmc += 1;
    }
  }
  
  return cmc;
}

