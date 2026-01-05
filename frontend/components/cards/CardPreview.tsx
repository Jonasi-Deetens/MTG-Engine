'use client';

// frontend/components/cards/CardPreview.tsx

import { useState } from 'react';
import Image from 'next/image';
import { CardModal } from '@/components/ui/CardModal';

export interface CardData {
  card_id: string;
  name: string;
  mana_cost?: string;
  type_line?: string;
  oracle_text?: string;
  power?: string;
  toughness?: string;
  colors?: string[];
  image_uris?: {
    small?: string;
    normal?: string;
    large?: string;
  };
  set_code?: string;
  collector_number?: string;
}

interface CardPreviewProps {
  card: CardData;
}

export function CardPreview({ card }: CardPreviewProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const imageUrl = card.image_uris?.normal || card.image_uris?.small || card.image_uris?.large;
  
  return (
    <>
      <div className="aspect-[63/88] relative overflow-visible flex items-center justify-center">
        <div 
          className="absolute inset-0 transition-all duration-300 ease-out hover:scale-105 hover:shadow-2xl hover:shadow-black/60 cursor-pointer"
          onClick={() => setIsModalOpen(true)}
        >
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={card.name}
              fill
              className="object-cover rounded-xl"
              sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
              unoptimized
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs text-center p-2 bg-slate-800 rounded-lg">
              No Image
            </div>
          )}
        </div>
      </div>

      {imageUrl && (
        <CardModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          card={card}
          imageUrl={imageUrl}
        />
      )}
    </>
  );
}

