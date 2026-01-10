'use client';

// frontend/components/collections/FavoriteButton.tsx

import { useState, useEffect } from 'react';
import { collections } from '@/lib/collections';

interface FavoriteButtonProps {
  cardId: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function FavoriteButton({ cardId, size = 'md', className = '' }: FavoriteButtonProps) {
  const [isFavorite, setIsFavorite] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const checkFavorite = async () => {
      if (!cardId) return;
      try {
        const result = await collections.checkFavorite(cardId);
        setIsFavorite(result.is_favorite);
      } catch (err) {
        console.error('Failed to check favorite status:', err);
      } finally {
        setChecking(false);
      }
    };
    checkFavorite();
  }, [cardId]);

  const handleToggle = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (loading || checking) return;

    setLoading(true);
    try {
      if (isFavorite) {
        await collections.removeFavorite(cardId);
        setIsFavorite(false);
      } else {
        await collections.addFavorite(cardId);
        setIsFavorite(true);
      }
    } catch (err: any) {
      console.error('Failed to toggle favorite:', err);
      alert(err?.data?.detail || 'Failed to update favorite');
    } finally {
      setLoading(false);
    }
  };

  if (checking) {
    return null;
  }

  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`${sizeClasses[size]} cursor-pointer transition-all hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
    >
      {isFavorite ? (
        <svg className="w-full h-full text-[color:var(--theme-accent-primary)] fill-current" viewBox="0 0 24 24">
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      ) : (
        <svg className="w-full h-full text-[color:var(--theme-text-muted)] hover:text-[color:var(--theme-accent-primary)] fill-none stroke-current" viewBox="0 0 24 24" strokeWidth={2}>
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
      )}
    </button>
  );
}

