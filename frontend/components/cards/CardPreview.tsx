'use client';

// frontend/components/cards/CardPreview.tsx

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { CardModal } from '@/components/ui/CardModal';
import { CardVersionSelector } from './CardVersionSelector';
import { cards } from '@/lib/api';

export interface CardData {
  card_id: string;
  oracle_id?: string;
  name: string;
  mana_cost?: string;
  mana_value?: number;
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
  rarity?: string;
  legalities?: Record<string, string>;
  prices?: {
    usd?: string;
    usd_foil?: string;
    eur?: string;
    tix?: string;
  };
  artist?: string;
  flavor_text?: string;
}

interface CardPreviewProps {
  card: CardData;
  onVersionChange?: (card: CardData) => void;
  onAddToDeck?: (card: CardData) => void;
  showAddButton?: boolean;
}

export function CardPreview({ card, onVersionChange, onAddToDeck, showAddButton = false }: CardPreviewProps) {
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

  const handleCardClick = () => {
    if (onAddToDeck) {
      onAddToDeck(card);
    } else {
      setIsModalOpen(true);
    }
  };

  return (
    <>
      <div className="aspect-[63/88] relative overflow-hidden rounded-xl flex items-center justify-center group">
        <div 
          className={`absolute inset-0 transition-all duration-300 ease-out hover:scale-105 hover:shadow-2xl hover:shadow-black/60 cursor-pointer rounded-xl`}
          onClick={handleCardClick}
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
            <div className="w-full h-full flex items-center justify-center text-[color:var(--theme-text-secondary)] text-xs text-center p-2 bg-[color:var(--theme-card-hover)] rounded-xl">
              No Image
            </div>
          )}
        </div>

        {/* Add to Deck Button Overlay */}
        {showAddButton && onAddToDeck && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="w-12 h-12 rounded-full bg-[color:var(--theme-button-primary-bg)]/90 text-[color:var(--theme-button-primary-text)] shadow-lg flex items-center justify-center pointer-events-none">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </div>
          </div>
        )}

        {/* View Card Button (when in deck builder mode) */}
        {onAddToDeck && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsModalOpen(true);
            }}
            className="absolute top-2 right-2 p-2 bg-[color:var(--theme-card-bg)]/90 hover:bg-[color:var(--theme-card-bg)] text-[color:var(--theme-text-primary)] rounded-full opacity-0 group-hover:opacity-100 transition-opacity shadow-lg z-10 border border-[color:var(--theme-card-border)]"
            aria-label="View card details"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
        )}
      </div>

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

