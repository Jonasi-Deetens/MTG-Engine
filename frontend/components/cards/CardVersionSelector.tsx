'use client';

// frontend/components/cards/CardVersionSelector.tsx

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { CardData } from './CardPreview';

interface CardVersionSelectorProps {
  currentCard: CardData;
  allVersions: CardData[];
  onVersionChange: (card: CardData) => void;
  loading?: boolean;
}

export function CardVersionSelector({ 
  currentCard, 
  allVersions, 
  onVersionChange,
  loading = false 
}: CardVersionSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Don't show selector if there's only one version
  if (allVersions.length <= 1) {
    return null;
  }

  const currentVersionLabel = currentCard.set_code && currentCard.collector_number
    ? `${currentCard.set_code.toUpperCase()} #${currentCard.collector_number}`
    : currentCard.set_code?.toUpperCase() || 'Current Version';

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="w-full px-3 py-2 bg-[color:var(--theme-input-bg)] hover:bg-[color:var(--theme-card-hover)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-between gap-2"
      >
        <span className="text-xs text-[color:var(--theme-text-secondary)]">Version:</span>
        <span className="text-xs font-semibold">{currentVersionLabel}</span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute top-full left-0 right-0 mt-1 bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg shadow-xl z-20 max-h-96 overflow-y-auto">
            <div className="p-2 space-y-1">
              {allVersions.map((version) => {
                const isCurrent = version.card_id === currentCard.card_id;
                const versionLabel = version.set_code && version.collector_number
                  ? `${version.set_code.toUpperCase()} #${version.collector_number}`
                  : version.set_code?.toUpperCase() || 'Unknown';
                const imageUrl = version.image_uris?.small || version.image_uris?.normal;

                return (
                  <button
                    key={version.card_id}
                    type="button"
                    onClick={() => {
                      onVersionChange(version);
                      setIsOpen(false);
                    }}
                    className={`w-full p-2 rounded text-left transition-colors flex items-center gap-3 ${
                      isCurrent
                        ? 'bg-[color:var(--theme-card-hover)] border border-[color:var(--theme-accent-primary)]'
                        : 'hover:bg-[color:var(--theme-card-hover)] border border-transparent'
                    }`}
                  >
                    {imageUrl && (
                      <div className="relative w-12 h-16 flex-shrink-0">
                        <Image
                          src={imageUrl}
                          alt={version.name}
                          fill
                          className="object-cover rounded"
                          sizes="48px"
                          unoptimized
                        />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className={`text-xs font-semibold ${isCurrent ? 'text-[color:var(--theme-accent-primary)]' : 'text-[color:var(--theme-text-primary)]'}`}>
                        {versionLabel}
                      </div>
                      {version.set_code && (
                        <div className="text-xs text-[color:var(--theme-text-secondary)] truncate">
                          {version.set_code}
                        </div>
                      )}
                    </div>
                    {isCurrent && (
                      <svg
                        className="w-4 h-4 text-[color:var(--theme-accent-primary)] flex-shrink-0"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

