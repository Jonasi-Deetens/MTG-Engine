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
        <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)] mb-2">Import Deck List</h3>
        <p className="text-sm text-[color:var(--theme-text-secondary)] mb-4">
          Paste your deck list in text format. Supported formats:
        </p>
        <ul className="text-sm text-[color:var(--theme-text-secondary)] list-disc list-inside mb-4 space-y-1">
          <li><code className="bg-[color:var(--theme-card-hover)] px-1 rounded border border-[color:var(--theme-card-border)]">4 Lightning Bolt</code></li>
          <li><code className="bg-[color:var(--theme-card-hover)] px-1 rounded border border-[color:var(--theme-card-border)]">1x Lightning Bolt</code></li>
          <li><code className="bg-[color:var(--theme-card-hover)] px-1 rounded border border-[color:var(--theme-card-border)]">Lightning Bolt</code> (defaults to 1)</li>
        </ul>
      </div>

      <textarea
        value={importText}
        onChange={(e) => setImportText(e.target.value)}
        placeholder="4 Lightning Bolt&#10;2 Mountain&#10;1x Sol Ring&#10;..."
        rows={12}
        className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none font-mono text-sm"
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
            ? 'bg-[color:var(--theme-status-success)]/20 border-[color:var(--theme-status-success)]/50 text-[color:var(--theme-status-success)]'
            : result.success > 0
            ? 'bg-[color:var(--theme-status-warning)]/20 border-[color:var(--theme-status-warning)]/50 text-[color:var(--theme-status-warning)]'
            : 'bg-[color:var(--theme-status-error)]/20 border-[color:var(--theme-status-error)]/50 text-[color:var(--theme-status-error)]'
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
                      <code className="bg-[color:var(--theme-card-hover)] px-1 rounded border border-[color:var(--theme-card-border)]">{fail.name}</code>: {fail.reason}
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

