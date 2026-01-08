'use client';

// frontend/components/decks/DeckImport.tsx

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { cards } from '@/lib/api';
import { useDeckStore } from '@/store/deckStore';

interface DeckImportProps {
  deckId: number;
  onImportSuccess?: () => void;
}

interface ParsedCard {
  quantity: number;
  name: string;
  originalLine: string;
}

interface ImportResult {
  success: number;
  failed: Array<{ name: string; reason: string }>;
}

export function DeckImport({ deckId, onImportSuccess }: DeckImportProps) {
  const [importText, setImportText] = useState('');
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const { addCard } = useDeckStore();

  const parseDeckList = (text: string): ParsedCard[] => {
    const lines = text.split('\n');
    const parsed: ParsedCard[] = [];

    for (const line of lines) {
      const trimmed = line.trim();
      
      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('//') || trimmed.startsWith('#')) {
        continue;
      }

      // Match patterns:
      // - "4 Lightning Bolt" (quantity + card name)
      // - "1x Lightning Bolt" (quantity with 'x' + card name)
      // - "Lightning Bolt" (default quantity 1)
      const match = trimmed.match(/^(\d+)\s*(?:x\s*)?(.+)$/i);
      
      if (match) {
        const quantity = parseInt(match[1], 10);
        const name = match[2].trim();
        if (name && quantity > 0) {
          parsed.push({ quantity, name, originalLine: trimmed });
        }
      } else {
        // No quantity specified, default to 1
        const name = trimmed;
        if (name) {
          parsed.push({ quantity: 1, name, originalLine: trimmed });
        }
      }
    }

    return parsed;
  };

  const handleImport = async () => {
    if (!importText.trim()) return;

    setImporting(true);
    setResult(null);

    const parsedCards = parseDeckList(importText);
    const importResult: ImportResult = {
      success: 0,
      failed: [],
    };

    try {
      // Process each card
      for (const parsedCard of parsedCards) {
        try {
          // Search for the card by name (exact match preferred)
          const searchResponse = await cards.search(parsedCard.name, 1, 10);
          
          if (!searchResponse.cards || searchResponse.cards.length === 0) {
            importResult.failed.push({
              name: parsedCard.name,
              reason: 'Card not found',
            });
            continue;
          }

          // Try to find exact match first
          let card = searchResponse.cards.find(
            (c: any) => c.name.toLowerCase() === parsedCard.name.toLowerCase()
          );

          // If no exact match, use first result
          if (!card) {
            card = searchResponse.cards[0];
          }

          // Add card to deck
          await addCard(deckId, card.card_id, parsedCard.quantity);
          importResult.success += parsedCard.quantity;
        } catch (err: any) {
          importResult.failed.push({
            name: parsedCard.name,
            reason: err?.data?.detail || err?.message || 'Failed to add card',
          });
        }
      }

      setResult(importResult);
      
      if (importResult.success > 0) {
        setImportText('');
        onImportSuccess?.();
      }
    } catch (err: any) {
      setResult({
        success: 0,
        failed: [{ name: 'Import', reason: err?.data?.detail || err?.message || 'Failed to import deck' }],
      });
    } finally {
      setImporting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Import Deck List</h3>
        <p className="text-sm text-slate-400 mb-4">
          Paste your deck list in text format. Supported formats:
        </p>
        <ul className="text-sm text-slate-400 list-disc list-inside mb-4 space-y-1">
          <li><code className="bg-slate-700 px-1 rounded">4 Lightning Bolt</code></li>
          <li><code className="bg-slate-700 px-1 rounded">1x Lightning Bolt</code></li>
          <li><code className="bg-slate-700 px-1 rounded">Lightning Bolt</code> (defaults to 1)</li>
        </ul>
      </div>

      <textarea
        value={importText}
        onChange={(e) => setImportText(e.target.value)}
        placeholder="4 Lightning Bolt&#10;2 Mountain&#10;1x Sol Ring&#10;..."
        rows={12}
        className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600 focus:border-amber-500 focus:outline-none font-mono text-sm"
      />

      <Button
        onClick={handleImport}
        disabled={importing || !importText.trim() || !deckId}
        variant="primary"
        className="w-full"
      >
        {importing ? 'Importing...' : 'Import Cards'}
      </Button>

      {result && (
        <div className={`p-4 rounded-lg border ${
          result.failed.length === 0
            ? 'bg-green-500/20 border-green-500/50 text-green-400'
            : result.success > 0
            ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400'
            : 'bg-red-500/20 border-red-500/50 text-red-400'
        }`}>
          <div className="font-semibold mb-2">
            Import {result.failed.length === 0 ? 'Complete' : 'Partial'}
          </div>
          <div className="text-sm space-y-1">
            <div>
              <strong>{result.success}</strong> card{result.success !== 1 ? 's' : ''} imported successfully
            </div>
            {result.failed.length > 0 && (
              <div className="mt-2">
                <strong>{result.failed.length}</strong> card{result.failed.length !== 1 ? 's' : ''} failed:
                <ul className="list-disc list-inside mt-1 ml-2 space-y-1">
                  {result.failed.map((fail, idx) => (
                    <li key={idx}>
                      <code className="bg-slate-800 px-1 rounded">{fail.name}</code>: {fail.reason}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

