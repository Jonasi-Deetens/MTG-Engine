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

const LEGALITY_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  legal: {
    bg: 'bg-green-600/20',
    text: 'text-green-400',
    label: 'Legal',
  },
  banned: {
    bg: 'bg-red-600/20',
    text: 'text-red-400',
    label: 'Banned',
  },
  restricted: {
    bg: 'bg-yellow-600/20',
    text: 'text-yellow-400',
    label: 'Restricted',
  },
  not_legal: {
    bg: 'bg-slate-600/20',
    text: 'text-slate-400',
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
      <div className={`text-sm text-slate-400 ${className}`}>
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
      <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">
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
              <div className={`w-2 h-2 rounded-full ${style.bg.replace('/20', '')} border ${style.text.replace('text-', 'border-')}`} />
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

