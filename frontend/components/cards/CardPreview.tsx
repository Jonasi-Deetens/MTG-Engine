// frontend/components/cards/CardPreview.tsx

import Image from 'next/image';
import { Card } from '@/components/ui/Card';

export interface CardData {
  card_id: string;
  name: string;
  mana_cost?: string;
  type_line?: string;
  image_uris?: {
    small?: string;
    normal?: string;
    large?: string;
  };
  set_code?: string;
}

interface CardPreviewProps {
  card: CardData;
  onClick?: () => void;
}

export function CardPreview({ card, onClick }: CardPreviewProps) {
  const imageUrl = card.image_uris?.normal || card.image_uris?.small;
  
  return (
    <Card
      variant="default"
      className="card-hover cursor-pointer h-full flex flex-col"
      onClick={onClick}
    >
      <div className="aspect-[63/88] relative mb-3 rounded overflow-hidden bg-slate-700 flex items-center justify-center">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={card.name}
            fill
            className="object-cover"
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
            unoptimized
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs text-center p-2">
            No Image
          </div>
        )}
      </div>
      <div className="flex-1">
        <h3 className="font-semibold text-white text-sm mb-1 line-clamp-2">
          {card.name}
        </h3>
        {card.mana_cost && (
          <p className="text-xs text-slate-400 mb-1">{card.mana_cost}</p>
        )}
        {card.type_line && (
          <p className="text-xs text-slate-500 line-clamp-1">{card.type_line}</p>
        )}
      </div>
    </Card>
  );
}

