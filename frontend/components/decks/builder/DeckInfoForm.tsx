// frontend/components/decks/builder/DeckInfoForm.tsx

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { FormatSelector } from '@/components/decks/FormatSelector';

interface DeckInfoFormProps {
  deckName: string;
  deckDescription: string;
  deckFormat: string;
  isPublic: boolean;
  saving: boolean;
  loading: boolean;
  hasDeck: boolean;
  onNameChange: (name: string) => void;
  onDescriptionChange: (description: string) => void;
  onFormatChange: (format: string) => void;
  onPublicChange: (isPublic: boolean) => void;
  onSave: () => void;
}

export function DeckInfoForm({
  deckName,
  deckDescription,
  deckFormat,
  isPublic,
  saving,
  loading,
  hasDeck,
  onNameChange,
  onDescriptionChange,
  onFormatChange,
  onPublicChange,
  onSave,
}: DeckInfoFormProps) {
  return (
    <Card variant="elevated">
      <div className="p-3 space-y-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
          <div>
            <label className="block text-xs font-medium text-[color:var(--theme-text-secondary)] mb-1">
              Deck Name *
            </label>
            <input
              type="text"
              value={deckName}
              onChange={(e) => onNameChange(e.target.value)}
              placeholder="My Awesome Deck"
              className="w-full px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-[color:var(--theme-text-secondary)] mb-1">
              Description
            </label>
            <input
              type="text"
              value={deckDescription}
              onChange={(e) => onDescriptionChange(e.target.value)}
              placeholder="Describe your deck..."
              className="w-full px-2 py-1.5 text-sm bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
            />
          </div>
          <div className="flex items-end gap-2">
            <div className="flex-1">
              <FormatSelector
                value={deckFormat}
                onChange={onFormatChange}
                disabled={hasDeck}
              />
            </div>
            <div className="flex items-center gap-1">
              <input
                type="checkbox"
                id="isPublic"
                checked={isPublic}
                onChange={(e) => onPublicChange(e.target.checked)}
                className="w-4 h-4 text-[color:var(--theme-accent-primary)] bg-[color:var(--theme-input-bg)] border-[color:var(--theme-input-border)] rounded focus:ring-[color:var(--theme-border-focus)]"
              />
              <label htmlFor="isPublic" className="text-xs text-[color:var(--theme-text-secondary)]">
                Public
              </label>
            </div>
            <Button
              onClick={onSave}
              disabled={saving || loading || !deckName.trim()}
              variant="primary"
              size="sm"
            >
              {saving ? 'Saving...' : hasDeck ? 'Update' : 'Create'}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}

