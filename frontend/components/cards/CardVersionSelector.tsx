'use client';

// frontend/components/cards/CardVersionSelector.tsx

import { CardData } from './CardPreview';
import { Select } from '@/components/ui/Select';

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
  // Don't show selector if there's only one version
  if (allVersions.length <= 1) {
    return null;
  }

  const getVersionLabel = (version: CardData) => {
    if (version.set_code && version.collector_number) {
      return `${version.set_code.toUpperCase()} #${version.collector_number}`;
    }
    return version.set_code?.toUpperCase() || version.name;
  };

  return (
    <div className="space-y-1">
      <div className="text-xs font-mono tracking-[0.2em] uppercase text-[color:var(--theme-text-secondary)]">
        Version
      </div>
      <Select
        value={currentCard.card_id}
        onChange={(e) => {
          const next = allVersions.find((version) => version.card_id === e.target.value);
          if (next) {
            onVersionChange(next);
          }
        }}
        disabled={loading}
        className="w-full"
      >
        {allVersions.map((version) => (
          <option key={version.card_id} value={version.card_id}>
            {getVersionLabel(version)}
          </option>
        ))}
      </Select>
    </div>
  );
}

