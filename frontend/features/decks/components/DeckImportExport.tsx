'use client';

// frontend/components/decks/DeckImportExport.tsx

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { decks, DeckExportResponse } from '@/lib/decks';

interface DeckImportExportProps {
  deckId: number;
  onImportSuccess?: () => void;
}

export function DeckImportExport({ deckId, onImportSuccess }: DeckImportExportProps) {
  const [importText, setImportText] = useState('');
  const [importing, setImporting] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportData, setExportData] = useState<string | null>(null);
  const [exportFormat, setExportFormat] = useState<'text' | 'json'>('text');

  const handleImport = async () => {
    if (!importText.trim()) return;
    
    setImporting(true);
    try {
      await decks.importDeck({
        format: 'text',
        data: importText,
      });
      setImportText('');
      onImportSuccess?.();
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to import deck');
    } finally {
      setImporting(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const result = await decks.exportDeck(deckId, exportFormat);
      setExportData(result.data);
    } catch (err: any) {
      alert(err?.data?.detail || 'Failed to export deck');
    } finally {
      setExporting(false);
    }
  };

  const handleCopyExport = () => {
    if (exportData) {
      navigator.clipboard.writeText(exportData);
      alert('Copied to clipboard!');
    }
  };

  return (
    <div className="space-y-6">
      {/* Import Section */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)]">Import Deck</h3>
        <textarea
          value={importText}
          onChange={(e) => setImportText(e.target.value)}
          placeholder="Paste deck list here (format: 4 Lightning Bolt)"
          rows={10}
          className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none font-mono text-sm"
        />
        <Button
          onClick={handleImport}
          disabled={importing || !importText.trim()}
          variant="primary"
        >
          {importing ? 'Importing...' : 'Import Deck'}
        </Button>
        <p className="text-xs text-[color:var(--theme-text-muted)]">
          Note: Import functionality is currently limited. Full parsing coming soon.
        </p>
      </div>

      {/* Export Section */}
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)]">Export Deck</h3>
        <div className="flex gap-2">
          <select
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value as 'text' | 'json')}
            className="px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
          >
            <option value="text">Text Format</option>
            <option value="json">JSON Format</option>
          </select>
          <Button
            onClick={handleExport}
            disabled={exporting}
            variant="primary"
          >
            {exporting ? 'Exporting...' : 'Export'}
          </Button>
        </div>
        
        {exportData && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm text-[color:var(--theme-text-secondary)]">Exported Data:</p>
              <Button
                onClick={handleCopyExport}
                variant="outline"
                size="sm"
              >
                Copy
              </Button>
            </div>
            <textarea
              value={exportData}
              readOnly
              rows={10}
              className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] font-mono text-sm"
            />
          </div>
        )}
      </div>
    </div>
  );
}

