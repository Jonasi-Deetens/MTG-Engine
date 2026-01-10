'use client';

// frontend/components/ui/RarityBadge.tsx

interface RarityBadgeProps {
  rarity?: string;
  className?: string;
}

const RARITY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  common: {
    bg: 'bg-slate-600/80',
    text: 'text-white',
    border: 'border-slate-500',
  },
  uncommon: {
    bg: 'bg-slate-400/80',
    text: 'text-white',
    border: 'border-slate-300',
  },
  rare: {
    bg: 'bg-[color:var(--theme-accent-primary)]/80',
    text: 'text-white',
    border: 'border-[color:var(--theme-accent-secondary)]',
  },
  mythic: {
    bg: 'bg-orange-600/80',
    text: 'text-white',
    border: 'border-orange-500',
  },
  special: {
    bg: 'bg-purple-600/80',
    text: 'text-white',
    border: 'border-purple-500',
  },
  bonus: {
    bg: 'bg-blue-600/80',
    text: 'text-white',
    border: 'border-blue-500',
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

