'use client';

// frontend/components/decks/DeckCard.tsx

import { useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { DeckResponse, DeckDetailResponse } from '@/lib/decks';
import { Button } from '@/components/ui/Button';
import { BookOpen, Users, Layers, Clock, Lock } from 'lucide-react';

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
  const [scanProgress, setScanProgress] = useState(0);
  const scanTimerRef = useRef<number | null>(null);
  const cardId = useMemo(
    () => Math.random().toString(36).substring(2, 8).toUpperCase(),
    []
  );

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

  const handleMouseEnter = () => {
    if (scanTimerRef.current) {
      window.clearInterval(scanTimerRef.current);
    }
    setScanProgress(0);
    let progress = 0;
    scanTimerRef.current = window.setInterval(() => {
      progress += 5;
      setScanProgress(progress);
      if (progress >= 100 && scanTimerRef.current) {
        window.clearInterval(scanTimerRef.current);
        scanTimerRef.current = null;
      }
    }, 30);
  };

  const handleMouseLeave = () => {
    if (scanTimerRef.current) {
      window.clearInterval(scanTimerRef.current);
      scanTimerRef.current = null;
    }
    setScanProgress(0);
  };

  useEffect(() => {
    return () => {
      if (scanTimerRef.current) {
        window.clearInterval(scanTimerRef.current);
      }
    };
  }, []);

  return (
    <div
      className={`relative w-full max-w-sm cursor-pointer group ${className || ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      tabIndex={0}
    >
      <div className="relative bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-border-default)] overflow-hidden">
        <div className="absolute -top-1.5 -left-1.5 w-4 h-4 border-t border-l border-[color:var(--theme-border-default)] z-20" />
        <div className="absolute -bottom-1.5 -right-1.5 w-4 h-4 border-b border-r border-[color:var(--theme-border-default)] z-20" />

        <div className="relative h-48 overflow-hidden">
          {artUrl ? (
            <img
              src={artUrl}
              alt={commanders[0]?.card?.name || deck.name}
              className="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
              draggable={false}
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-[color:var(--theme-bg-secondary)] flex items-center justify-center">
              <span className="font-mono text-xs text-[color:var(--theme-text-muted)] tracking-widest">
                NO_IMAGE_DATA
              </span>
            </div>
          )}

          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[color:var(--theme-card-bg)]/80" />

          <div
            className="absolute inset-0 opacity-20 transition-opacity duration-300"
            style={{
              backgroundImage: `
                linear-gradient(to right, var(--theme-text-primary) 1px, transparent 1px),
                linear-gradient(to bottom, var(--theme-text-primary) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px',
            }}
          />

          <div
            className="absolute left-0 right-0 h-px bg-[color:var(--theme-text-primary)]/60 transition-all duration-75"
            style={{ top: `${scanProgress}%` }}
          >
            <div className="absolute inset-0 bg-[color:var(--theme-text-primary)]/40 blur-sm" />
          </div>

          <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-[color:var(--theme-bg-primary)]/90 border border-[color:var(--theme-border-default)] px-2 py-1">
            <Lock className="w-3 h-3 text-[color:var(--theme-text-muted)]" />
            <span className="font-mono text-[12px] tracking-widest text-[color:var(--theme-text-muted)] uppercase">
              {deck.is_public ? 'Public' : 'Private'}
            </span>
          </div>

          <div className="absolute top-3 right-3 bg-[color:var(--theme-text-primary)] text-[color:var(--theme-bg-primary)] px-2 py-1">
            <span className="font-mono text-[12px] tracking-widest uppercase flex items-center gap-1">
              {deck.format}
            </span>
          </div>

          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 opacity-0 group-hover:opacity-60 transition-opacity duration-300">
            <div className="absolute top-0 left-1/2 w-px h-3 bg-[color:var(--theme-text-primary)] -translate-x-1/2" />
            <div className="absolute bottom-0 left-1/2 w-px h-3 bg-[color:var(--theme-text-primary)] -translate-x-1/2" />
            <div className="absolute left-0 top-1/2 w-3 h-px bg-[color:var(--theme-text-primary)] -translate-y-1/2" />
            <div className="absolute right-0 top-1/2 w-3 h-px bg-[color:var(--theme-text-primary)] -translate-y-1/2" />
            <div className="absolute inset-3 border border-[color:var(--theme-text-primary)]/50" />
          </div>
        </div>

        <div className="p-4 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-sans font-semibold text-lg text-[color:var(--theme-text-primary)] tracking-wide leading-tight">
              {deck.name}
            </h3>
            <div className="flex items-center gap-3 text-[color:var(--theme-text-muted)] shrink-0">
              <div className="flex items-center gap-1">
                <Users className="w-3.5 h-3.5" />
                <span className="font-mono text-[11px]">{deck.commander_count}</span>
              </div>
              <div className="flex items-center gap-1">
                <Layers className="w-3.5 h-3.5" />
                <span className="font-mono text-[11px]">{deck.card_count}</span>
              </div>
            </div>
          </div>

          <div className="relative h-px bg-[color:var(--theme-border-default)]">
            <div className="absolute left-0 top-0 w-2 h-px bg-[color:var(--theme-text-primary)]" />
            <div className="absolute right-0 top-0 w-2 h-px bg-[color:var(--theme-text-primary)]" />
          </div>

          <p className="font-mono text-xs text-[color:var(--theme-text-muted)] leading-relaxed line-clamp-2">
            {deck.description || 'No description provided.'}
          </p>

          {commanders.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 -mt-1">
              <span className="inline-flex items-center font-mono text-[10px] leading-none tracking-[0.2em] text-[color:var(--theme-text-muted)] uppercase">
                Commanders
              </span>
              {commanders.map((commander) => (
                <span
                  key={commander.card_id}
                  className="bg-[color:var(--theme-bg-secondary)] border border-[color:var(--theme-border-default)] px-2 py-0.5 font-mono text-xs leading-none text-[color:var(--theme-text-primary)]"
                >
                  {commander.card.name}
                </span>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-1.5 text-[color:var(--theme-text-muted)]">
              <Clock className="w-3 h-3" />
              <span className="font-mono text-[10px] tracking-wider">
                Updated {formatRelativeTime(deck.updated_at)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="w-16 h-1 bg-[color:var(--theme-bg-secondary)] overflow-hidden">
                <div
                  className="h-full bg-[color:var(--theme-text-primary)] transition-all duration-75"
                  style={{ width: `${scanProgress}%` }}
                />
              </div>
              <span className="font-mono text-[10px] text-[color:var(--theme-text-muted)] w-8">
                {scanProgress.toString().padStart(3, '0')}%
              </span>
            </div>
          </div>

          {showActions && (
            <div className="flex gap-2 pt-2">
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

        <div className="bg-[color:var(--theme-bg-secondary)]/50 border-t border-[color:var(--theme-border-default)] px-4 py-2 flex items-center justify-between">
          <span className="font-mono text-[9px] tracking-[0.15em] text-[color:var(--theme-text-muted)]">
            DECK::ARCHIVE
          </span>
          <span className="font-mono text-[9px] tracking-[0.15em] text-[color:var(--theme-text-muted)]">
            ID_{cardId}
          </span>
        </div>
      </div>

      <div className="absolute -top-2 -left-2 w-2 h-2 border-t border-l border-[color:var(--theme-accent-primary)]" />
      <div className="absolute -bottom-2 -right-2 w-2 h-2 border-b border-r border-[color:var(--theme-accent-primary)]" />
    </div>
  );
}

