'use client';

// frontend/components/cards/LegalityDisplay.tsx

interface LegalityDisplayProps {
  legalities?: Record<string, string>;
  className?: string;
}

const FORMATS = [
  'standard',
  'pioneer',
  'modern',
  'legacy',
  'vintage',
  'commander',
  'pauper',
  'historic',
  'brawl',
  'penny',
  'duel',
  'oldschool',
  'premodern',
];

const LEGALITY_COLORS: Record<string, { bg: string; text: string; dot: string; label: string }> = {
  legal: {
    bg: 'bg-[color:var(--theme-status-success)]/20',
    text: 'text-[color:var(--theme-status-success)]',
    dot: 'bg-[color:var(--theme-status-success)] border-[color:var(--theme-status-success)]',
    label: 'Legal',
  },
  banned: {
    bg: 'bg-[color:var(--theme-status-error)]/20',
    text: 'text-[color:var(--theme-status-error)]',
    dot: 'bg-[color:var(--theme-status-error)] border-[color:var(--theme-status-error)]',
    label: 'Banned',
  },
  restricted: {
    bg: 'bg-[color:var(--theme-status-warning)]/20',
    text: 'text-[color:var(--theme-status-warning)]',
    dot: 'bg-[color:var(--theme-status-warning)] border-[color:var(--theme-status-warning)]',
    label: 'Restricted',
  },
  not_legal: {
    bg: 'bg-[color:var(--theme-bg-secondary)]',
    text: 'text-[color:var(--theme-text-secondary)]',
    dot: 'bg-[color:var(--theme-bg-tertiary)] border-[color:var(--theme-border-default)]',
    label: 'Not Legal',
  },
};

function getLegalityStyle(legality: string | undefined) {
  if (!legality) return LEGALITY_COLORS.not_legal;
  return LEGALITY_COLORS[legality.toLowerCase()] || LEGALITY_COLORS.not_legal;
}

export function LegalityDisplay({ legalities, className = '' }: LegalityDisplayProps) {
  if (!legalities || Object.keys(legalities).length === 0) {
    return (
      <div className={`text-sm text-[color:var(--theme-text-secondary)] ${className}`}>
        No legality information available
      </div>
    );
  }

  // Filter to only show formats that exist in our list
  const relevantFormats = FORMATS.filter((format) => legalities[format]);

  if (relevantFormats.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <p className="text-xs text-[color:var(--theme-text-muted)] uppercase tracking-wider mb-2">
        Format Legality
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
        {relevantFormats.map((format) => {
          const legality = legalities[format];
          const style = getLegalityStyle(legality);
          return (
            <div
              key={format}
              className={`flex items-center gap-2 px-2 py-1 rounded text-xs ${style.bg} ${style.text}`}
            >
              <div className={`w-2 h-2 rounded-full border ${style.dot}`} />
              <span className="font-medium capitalize">{format}</span>
              {legality && legality !== 'legal' && (
                <span className="text-xs opacity-75">({style.label})</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

