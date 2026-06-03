'use client';

// frontend/components/ui/RarityBadge.tsx

interface RarityBadgeProps {
  rarity?: string;
  className?: string;
}

const RARITY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  common: {
    bg: 'bg-[color:var(--theme-bg-tertiary)]/80',
    text: 'text-[color:var(--theme-text-primary)]',
    border: 'border-[color:var(--theme-border-default)]',
  },
  uncommon: {
    bg: 'bg-[color:var(--theme-bg-secondary)]/80',
    text: 'text-[color:var(--theme-text-primary)]',
    border: 'border-[color:var(--theme-border-default)]',
  },
  rare: {
    bg: 'bg-[color:var(--theme-accent-primary)]/80',
    text: 'text-[color:var(--theme-button-primary-text)]',
    border: 'border-[color:var(--theme-accent-secondary)]',
  },
  mythic: {
    bg: 'bg-[color:var(--theme-status-warning)]/80',
    text: 'text-[color:var(--theme-button-primary-text)]',
    border: 'border-[color:var(--theme-status-warning)]',
  },
  special: {
    bg: 'bg-[color:var(--theme-status-info)]/80',
    text: 'text-[color:var(--theme-button-primary-text)]',
    border: 'border-[color:var(--theme-status-info)]',
  },
  bonus: {
    bg: 'bg-[color:var(--theme-status-success)]/80',
    text: 'text-[color:var(--theme-button-primary-text)]',
    border: 'border-[color:var(--theme-status-success)]',
  },
};

export function RarityBadge({ rarity, className = '' }: RarityBadgeProps) {
  if (!rarity) return null;

  const rarityLower = rarity.toLowerCase();
  const style = RARITY_STYLES[rarityLower] || RARITY_STYLES.common;

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold border ${style.bg} ${style.text} ${style.border} ${className}`}
    >
      {rarity}
    </span>
  );
}

