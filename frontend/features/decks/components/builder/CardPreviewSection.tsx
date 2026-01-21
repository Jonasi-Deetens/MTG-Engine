// frontend/components/decks/builder/CardPreviewSection.tsx

import { DeckCardResponse } from '@/lib/decks';
import { CardPreview } from '@/components/cards/CardPreview';

interface CardPreviewSectionProps {
  previewCard: DeckCardResponse | null;
}

export function CardPreviewSection({ previewCard }: CardPreviewSectionProps) {
  return (
    <div className="flex items-start justify-center min-h-[300px]">
      {previewCard ? (
        <div className="sticky top-4 w-[280px]">
          {previewCard.card.image_uris?.normal || previewCard.card.image_uris?.small || previewCard.card.image_uris?.large ? (
            <>
              <CardPreview card={previewCard.card} disableClick={true} />
              {previewCard.quantity > 1 && (
                <div className="mt-2 text-center text-xs text-[color:var(--theme-text-secondary)]">
                  Quantity: {previewCard.quantity}x
                </div>
              )}
            </>
          ) : (
            <div className="aspect-[63/88] bg-[color:var(--theme-card-hover)] rounded-xl flex items-center justify-center text-[color:var(--theme-text-secondary)] text-sm p-4 text-center">
              <div>
                <div className="font-medium mb-1">{previewCard.card.name}</div>
                {previewCard.card.mana_cost && (
                  <div className="text-xs font-mono text-[color:var(--theme-accent-primary)]">
                    {previewCard.card.mana_cost}
                  </div>
                )}
                {previewCard.card.type_line && (
                  <div className="text-xs mt-1">{previewCard.card.type_line}</div>
                )}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center h-full text-sm text-[color:var(--theme-text-secondary)] text-center px-4">
          Hover over a card to see preview
        </div>
      )}
    </div>
  );
}

