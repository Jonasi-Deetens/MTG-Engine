'use client';

// frontend/components/ui/CardModal.tsx

import { useEffect } from 'react';
import { createPortal } from 'react-dom';
import Image from 'next/image';
import Link from 'next/link';
import { CardData } from '@/components/cards/CardPreview';

interface CardModalProps {
  isOpen: boolean;
  onClose: () => void;
  card: CardData;
  imageUrl: string;
}

export function CardModal({ isOpen, onClose, card, imageUrl }: CardModalProps) {
  // Close modal on Escape key and prevent body scroll
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/95 backdrop-blur-sm transition-opacity duration-200"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={`Full size view of ${card.name}`}
    >
      {/* Action buttons */}
      <div className="absolute top-4 right-4 z-[10000] flex gap-2">
        <Link
          href={`/cards/${card.card_id}`}
          onClick={onClose}
          className="p-3 rounded-full bg-amber-600/90 hover:bg-amber-500/90 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 shadow-lg flex items-center gap-2"
          aria-label="View card details"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
          <span className="text-sm font-medium hidden sm:inline">View Details</span>
        </Link>
        <button
          onClick={onClose}
          className="p-3 rounded-full bg-slate-900/90 hover:bg-slate-800/90 text-white transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 shadow-lg"
          aria-label="Close modal"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      {/* Content container - prevent click propagation */}
      <div
        className="relative w-full h-full flex flex-col lg:flex-row items-center justify-center p-4 lg:p-6 gap-6 lg:gap-8 max-w-7xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Card Image */}
        <div className="flex-shrink-0 w-full max-w-sm lg:max-w-md h-auto max-h-[60vh] lg:max-h-[90vh] flex items-center justify-center">
          <div className="relative w-full aspect-[63/88]">
            <Image
              src={imageUrl}
              alt={card.name}
              fill
              className="object-contain rounded-[25px]"
              priority
              unoptimized
            />
          </div>
        </div>

        {/* Card Details */}
        <div className="flex-1 w-full lg:max-w-lg space-y-4 lg:space-y-6 text-white overflow-y-auto max-h-[60vh] lg:max-h-[90vh] pr-2">
          {/* Name and Mana Cost */}
          <div>
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 sm:gap-4 mb-2">
              <h1 className="font-heading text-2xl sm:text-3xl lg:text-4xl font-bold text-white leading-tight">
                {card.name}
              </h1>
              {card.mana_cost && (
                <div className="text-xl sm:text-2xl text-slate-300 font-semibold whitespace-nowrap">
                  {card.mana_cost}
                </div>
              )}
            </div>
            {card.type_line && (
              <p className="text-base sm:text-lg text-slate-400 italic">
                {card.type_line}
              </p>
            )}
          </div>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent" />

          {/* Oracle Text */}
          {card.oracle_text && (
            <div className="space-y-2">
              <p className="text-xs text-slate-500 uppercase tracking-wider">
                Oracle Text
              </p>
              <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-line">
                {card.oracle_text}
              </p>
            </div>
          )}

          {/* Power/Toughness */}
          {(card.power || card.toughness) && (
            <div className="flex items-center gap-4">
              {card.power && (
                <div className="space-y-1">
                  <p className="text-xs text-slate-500 uppercase tracking-wider">
                    Power
                  </p>
                  <p className="text-lg text-slate-300 font-semibold">
                    {card.power}
                  </p>
                </div>
              )}
              {card.toughness && (
                <div className="space-y-1">
                  <p className="text-xs text-slate-500 uppercase tracking-wider">
                    Toughness
                  </p>
                  <p className="text-lg text-slate-300 font-semibold">
                    {card.toughness}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Colors */}
          {card.colors && card.colors.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs text-slate-500 uppercase tracking-wider">
                Colors
              </p>
              <div className="flex gap-2">
                {card.colors.map((color, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 text-xs font-semibold rounded bg-slate-700 text-slate-300"
                  >
                    {color}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Set Information */}
          {card.set_code && (
            <div className="space-y-1">
              <p className="text-xs text-slate-500 uppercase tracking-wider">
                Set
              </p>
              <p className="text-sm text-slate-300 font-semibold">
                {card.set_code.toUpperCase()}
                {card.collector_number && (
                  <span className="text-slate-500 ml-2">
                    #{card.collector_number}
                  </span>
                )}
              </p>
            </div>
          )}

          {/* Card ID */}
          <div className="space-y-1 pt-4 border-t border-slate-700">
            <p className="text-xs text-slate-500 uppercase tracking-wider">
              Card ID
            </p>
            <p className="text-xs text-slate-400 font-mono break-all">
              {card.card_id}
            </p>
          </div>
        </div>
      </div>

      {/* Click outside to close hint */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 text-slate-400 text-sm z-[10000] pointer-events-none">
        Click outside or press ESC to close
      </div>
    </div>
  );

  return typeof window !== 'undefined' ? createPortal(modalContent, document.body) : null;
}

