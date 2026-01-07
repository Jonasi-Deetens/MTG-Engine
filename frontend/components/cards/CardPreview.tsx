'use client';

// frontend/components/cards/CardPreview.tsx

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { CardModal } from '@/components/ui/CardModal';
import { CardVersionSelector } from './CardVersionSelector';
import { FavoriteButton } from '@/components/collections/FavoriteButton';
import { cards } from '@/lib/api';

export interface CardData {
  card_id: string;
  oracle_id?: string;
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
  onVersionChange?: (card: CardData) => void;
  linkToDetail?: boolean; // If true, clicking card navigates to detail page instead of opening modal
}

export function CardPreview({ card, onVersionChange, linkToDetail = false }: CardPreviewProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [allVersions, setAllVersions] = useState<CardData[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);
  const imageUrl = card.image_uris?.normal || card.image_uris?.small || card.image_uris?.large;
  
  // Fetch all versions when card changes
  useEffect(() => {
    const fetchVersions = async () => {
      if (!card?.card_id || !onVersionChange) return;
      
      setLoadingVersions(true);
      try {
        const versions = await cards.getVersions(card.card_id);
        setAllVersions(versions || []);
      } catch (err) {
        console.error('Failed to fetch card versions:', err);
        setAllVersions([card]); // Fallback to just current card
      } finally {
        setLoadingVersions(false);
      }
    };

    fetchVersions();
  }, [card?.card_id, onVersionChange]);
  
  const cardImage = (
    <div className="aspect-[63/88] relative overflow-visible flex items-center justify-center group">
      <div 
        className={`absolute inset-0 transition-all duration-300 ease-out hover:scale-105 hover:shadow-2xl hover:shadow-black/60 ${linkToDetail ? 'cursor-pointer' : 'cursor-pointer'}`}
        onClick={linkToDetail ? undefined : () => setIsModalOpen(true)}
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
      {/* Favorite button overlay */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
        <FavoriteButton cardId={card.card_id} size="sm" />
      </div>
    </div>
  );
  
  return (
    <>
      {linkToDetail ? (
        <Link href={`/cards/${card.card_id}`}>
          {cardImage}
        </Link>
      ) : (
        cardImage
      )}

      {/* Version Selector */}
      {onVersionChange && (
        <div className="mt-3">
          <CardVersionSelector
            currentCard={card}
            allVersions={allVersions.length > 0 ? allVersions : [card]}
            onVersionChange={onVersionChange}
            loading={loadingVersions}
          />
        </div>
      )}

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

