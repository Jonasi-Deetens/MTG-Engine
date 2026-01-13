// frontend/components/decks/builder/DeckBuilderHeader.tsx

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';

interface DeckBuilderHeaderProps {
  deckName: string | null;
  onImportClick: () => void;
  deckId?: number;
}

export function DeckBuilderHeader({ deckName, onImportClick, deckId }: DeckBuilderHeaderProps) {
  const router = useRouter();

  return (
    <div className="flex items-center justify-between gap-4 pb-3 border-b border-[color:var(--theme-card-border)]">
      <div className="flex-1">
        <h1 className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)] mb-1">
          {deckName ? `Editing: ${deckName}` : 'Deck Builder'}
        </h1>
      </div>
      <div className="flex gap-2">
        {deckId && (
          <>
            <Button
              onClick={onImportClick}
              variant="outline"
              size="sm"
            >
              Import
            </Button>
            <Button
              onClick={() => router.push(`/decks/${deckId}`)}
              variant="outline"
              size="sm"
            >
              View
            </Button>
          </>
        )}
        <Button
          onClick={() => router.push('/decks')}
          variant="outline"
          size="sm"
        >
          Back
        </Button>
      </div>
    </div>
  );
}

