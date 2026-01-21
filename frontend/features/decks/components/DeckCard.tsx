'use client';

// frontend/components/decks/DeckCard.tsx

import Link from 'next/link';
import { DeckResponse, DeckDetailResponse } from '@/lib/decks';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Card } from '@/components/ui/Card';
import { HoverShadow } from '@/components/ui/HoverShadow';
import { BookOpen, Users, Globe, Lock } from 'lucide-react';

interface DeckCardProps {
  deck: DeckResponse;
  deckDetail?: DeckDetailResponse;
  showActions?: boolean;
  onDelete?: (id: number, name: string) => void;
  variant?: 'default' | 'compact';
  className?: string;
}

// Card-y visual layout, but *no* Card wrapper. Instead, effects/borders are handled on container directly
export function DeckCard({
  deck,
  deckDetail,
  showActions = true,
  onDelete,
  variant = 'default',
  className,
}: DeckCardProps) {
  const isCommanderDeck = deck.format === 'Commander' && deck.commander_count > 0;
  const commanders = deckDetail?.commanders || [];
  const cards = deckDetail?.cards || [];

  // Prefer art_crop (art-only, no frame) for better background effect
  let artUrl: string | undefined;
  if (isCommanderDeck && commanders.length > 0) {
    const firstCommander = commanders[0]?.card;
    artUrl = firstCommander?.image_uris?.art_crop || firstCommander?.image_uris?.normal || firstCommander?.image_uris?.large || firstCommander?.image_uris?.small;
  } else if (cards.length > 0) {
    const firstCard = cards[0]?.card;
    artUrl = firstCard?.image_uris?.art_crop || firstCard?.image_uris?.normal || firstCard?.image_uris?.large || firstCard?.image_uris?.small;
  }

  // Format relative time
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;

    return date.toLocaleDateString();
  };

  return (
    <Card
      variant="bare"
      className={`relative flex flex-col sm:flex-row items-stretch hover:scale-105 rounded-lg ${className || ''}`}
      tabIndex={0}
    >
      <HoverShadow />
      {/* Side image panel (art) */}
      <div className="w-full sm:w-40 shrink-0 h-48 sm:h-auto relative rounded-lg flex-none bg-[color:var(--theme-bg-tertiary)] aspect-[5/7]">
        {artUrl ? (
          <img
            src={artUrl}
            alt={deck.name + ' art'}
            className="w-full h-full object-cover object-center sm:rounded-l-lg rounded-t-lg sm:rounded-tr-none"
            draggable={false}
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full bg-[color:var(--theme-bg-secondary)]/60 flex items-center justify-center sm:rounded-l-lg rounded-t-lg sm:rounded-tr-none">
            <BookOpen className="opacity-60 w-12 h-12 text-[color:var(--theme-text-muted)]" />
          </div>
        )}
      </div>

      {/* Content panel */}
      <div
        className="flex-1 flex flex-col justify-between p-4 gap-3 rounded-b-lg sm:rounded-bl-none sm:rounded-r-lg relative z-10 bg-[color:var(--theme-bg-primary)] bg-opacity-80 backdrop-blur-sm">
        <div>
          <div className="flex flex-row flex-wrap items-center justify-between gap-2 mb-1">
            <h3 className="text-lg sm:text-xl font-semibold text-[color:var(--theme-text-primary)] break-words flex-1 min-w-0 leading-tight">
              <span className="truncate block">{deck.name}</span>
            </h3>
            <div className="flex items-center gap-2 ml-2">
              {deck.is_public ? (
                <StatusBadge
                  label="Public"
                  variant="success"
                  icon={Globe}
                  size="sm"
                />
              ) : (
                <StatusBadge
                  label="Private"
                  variant="default"
                  icon={Lock}
                  size="sm"
                />
              )}
            </div>
          </div>

          {/* BADGES ROW */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <StatusBadge label={deck.format} variant="info" size="sm" />
            {deck.commander_count > 0 && (
              <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-[color:var(--theme-accent-primary)]/10 text-[color:var(--theme-accent-primary)] rounded font-medium">
                <Users className="w-3.5 h-3.5" />
                {deck.commander_count} commander{deck.commander_count > 1 ? 's' : ''}
              </span>
            )}
            <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-[color:var(--theme-card-bg)] text-[color:var(--theme-text-secondary)] rounded font-medium">
              <BookOpen className="w-3.5 h-3.5" />
              {deck.card_count} cards
            </span>
          </div>

          {/* Description */}
          {deck.description && (
            <p className="text-[color:var(--theme-text-secondary)] text-sm mb-2 line-clamp-2">
              {deck.description}
            </p>
          )}

          {/* Commanders (for commander format) */}
          {isCommanderDeck && commanders.length > 0 && (
            <div className="my-1 flex flex-wrap items-center gap-2">
              <span className="text-xs font-semibold uppercase text-[color:var(--theme-text-muted)] mr-2 tracking-widest">
                Commanders
              </span>
              {commanders.map((commander, idx) => (
                <span className="inline-block text-xs px-2 py-0.5 rounded bg-[color:var(--theme-accent-primary)]/10 text-[color:var(--theme-accent-primary)]" key={commander.card_id}>
                  {commander.card.name}
                  {idx < commanders.length - 1 && ','}
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-row flex-wrap items-end justify-between ">
          {/* Last updated */}
          <div className="text-xs text-[color:var(--theme-text-muted)] mr-2">
            Updated {formatRelativeTime(deck.updated_at)}
          </div>

          {/* ACTION BUTTONS */}
          {showActions && (
            <div className="flex gap-2 mt-1 min-w-[170px]">
              <Link href={`/decks/${deck.id}`} className="flex-1 min-w-0">
                <Button variant="primary" size="sm" className="w-full">
                  View
                </Button>
              </Link>
              <Link href={`/decks/builder?deck=${deck.id}`} className="flex-1 min-w-0">
                <Button variant="outline" size="sm" className="w-full">
                  Edit
                </Button>
              </Link>
              {onDelete && (
                <Button
                  onClick={e => {
                    e.preventDefault();
                    onDelete(deck.id, deck.name);
                  }}
                  variant="outline"
                  size="sm"
                  className="text-[color:var(--theme-status-error)] hover:opacity-90 min-w-0"
                >
                  Delete
                </Button>
              )}
            </div>
          )}
        </div>
      </div>

    </Card>
  );
}

