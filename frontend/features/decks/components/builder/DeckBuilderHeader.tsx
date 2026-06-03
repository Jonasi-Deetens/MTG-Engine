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
    <div className="flex flex-col gap-4 pb-3 border-b border-[color:var(--theme-card-border)] sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <Button
          onClick={() => router.push('/decks')}
          variant="outline"
          size="sm"
          className="mb-2 w-full sm:w-auto"
        >
          ← Back to Decks
        </Button>
        <h1
          className="font-heading text-3xl font-bold text-[color:var(--theme-text-primary)] mb-2 nier-glitch"
          data-text={deckName ? `Editing: ${deckName}` : 'Deck Builder'}
        >
          {deckName ? `Editing: ${deckName}` : 'Deck Builder'}
        </h1>
      </div>
      <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
        {deckId && (
          <>
            <Button
              onClick={onImportClick}
              variant="outline"
              size="sm"
              className="w-full sm:w-auto"
            >
              Import
            </Button>
            <Button
              onClick={() => router.push(`/decks/${deckId}`)}
              variant="outline"
              size="sm"
              className="w-full sm:w-auto"
            >
              View
            </Button>
          </>
        )}
      </div>
    </div>
  );
}

