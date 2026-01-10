'use client';

// frontend/components/decks/DeckCard.tsx

import Link from 'next/link';
import { DeckResponse, DeckDetailResponse } from '@/lib/decks';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { BookOpen, Users, Globe, Lock } from 'lucide-react';

interface DeckCardProps {
  deck: DeckResponse;
  deckDetail?: DeckDetailResponse;
  showActions?: boolean;
  onDelete?: (id: number, name: string) => void;
  variant?: 'default' | 'compact';
  className?: string;
}

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

  // Get background image: commander for commander decks, first card for others
  // Prefer art_crop (art-only, no frame) for better background effect
  let backgroundImageUrl: string | undefined;
  if (isCommanderDeck && commanders.length > 0) {
    const firstCommander = commanders[0]?.card;
    backgroundImageUrl = firstCommander?.image_uris?.art_crop || firstCommander?.image_uris?.normal || firstCommander?.image_uris?.large || firstCommander?.image_uris?.small;
  } else if (cards.length > 0) {
    const firstCard = cards[0]?.card;
    backgroundImageUrl = firstCard?.image_uris?.art_crop || firstCard?.image_uris?.normal || firstCard?.image_uris?.large || firstCard?.image_uris?.small;
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
      variant="elevated" 
      className={`relative transition-all duration-200 hover:scale-105 cursor-pointer h-full group overflow-visible border-0 ${className || ''}`}
      style={{
        backgroundImage: backgroundImageUrl ? `url('${backgroundImageUrl}')` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    >
      {/* Dark overlay for readability */}
      {backgroundImageUrl && (
        <div className="absolute inset-0 bg-black/60 rounded-lg" />
      )}
      {/* Glassmorphism effect on content only */}
      <div className="p-6 space-y-4 relative z-10 bg-black/30 backdrop-blur-md rounded-lg border border-white/10">
        {/* Header: Name + Public/Private Badge */}
        <div>
          <div className="flex items-start justify-between mb-3">
            <h3 className="text-xl font-semibold text-white flex-1 drop-shadow-lg">
              {deck.name}
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
          
          {/* Description */}
          {deck.description && (
            <p className="text-white/90 text-sm mb-3 line-clamp-2 drop-shadow">
              {deck.description}
            </p>
          )}
          
          {/* Format Badge */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <StatusBadge
              label={deck.format}
              variant="info"
              size="sm"
            />
          </div>
          
          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-white/90 drop-shadow">
            <span className="flex items-center gap-1">
              <BookOpen className="w-4 h-4" />
              {deck.card_count} cards
            </span>
            {deck.commander_count > 0 && (
              <span className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                {deck.commander_count} commander{deck.commander_count > 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        {/* Commander Names */}
        {isCommanderDeck && commanders.length > 0 && (
          <div className="space-y-1">
            <h4 className="text-sm font-medium text-white/90 drop-shadow">
              Commanders
            </h4>
            <div className="flex flex-wrap gap-2">
              {commanders.map((commander, index) => (
                <span key={commander.card_id} className="text-sm text-white/90 drop-shadow">
                  {commander.card.name}
                  {index < commanders.length - 1 && ','}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Last Updated */}
        <div className="text-xs text-white/80 drop-shadow">
          Updated {formatRelativeTime(deck.updated_at)}
        </div>

        {/* Action Buttons */}
        {showActions && (
          <div className="flex gap-2 pt-4 border-t border-white/20">
            <Link href={`/decks/${deck.id}`} className="flex-1">
              <Button variant="primary" size="sm" className="w-full">
                View
              </Button>
            </Link>
            <Link href={`/decks/builder?deck=${deck.id}`} className="flex-1">
              <Button variant="outline" size="sm" className="w-full">
                Edit
              </Button>
            </Link>
            {onDelete && (
              <Button
                onClick={() => onDelete(deck.id, deck.name)}
                variant="outline"
                size="sm"
                className="text-[color:var(--theme-status-error)] hover:opacity-90"
              >
                Delete
              </Button>
            )}
          </div>
        )}
      </div>
      
      {/* Theme-colored drop shadow on hover - on outer card */}
      <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-0" 
           style={{
             boxShadow: `0 4px 20px -4px var(--theme-accent-primary)`,
           }}
      />
    </Card>
  );
}

