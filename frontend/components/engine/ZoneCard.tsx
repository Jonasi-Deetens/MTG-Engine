/* eslint-disable @next/next/no-img-element */
'use client';

import { CardPreview, CardData } from '@/components/cards/CardPreview';
import { Card } from '@/components/ui/Card';
import { EngineGameObjectSnapshot, EngineCardMap } from '@/lib/engine';

export interface ZoneCardProps {
  obj: EngineGameObjectSnapshot;
  cardMap: EngineCardMap;
  onClick?: () => void;
  selected?: boolean;
  statusLabel?: string | null;
  statusDetail?: string | null;
  className?: string;
}

export function ZoneCard({
  obj,
  cardMap,
  onClick,
  selected,
  statusLabel,
  statusDetail,
  className,
}: ZoneCardProps) {
  const card = cardMap[obj.id];
  const showsTappedClass = Boolean(className?.includes('zone-card-tapped'));
  const isTapped = Boolean(obj.tapped && showsTappedClass);
  const selectedClass = selected ? 'ring-2 ring-amber-500 rounded-lg' : '';
  const wrapperClass = `${onClick ? 'cursor-pointer' : 'cursor-default'} zone-card ${selectedClass} ${className || ''}`.trim();

  if (!card) {
    return (
      <button type="button" onClick={onClick} className={`text-left ${wrapperClass}`} title={statusDetail || undefined}>
        <Card
          variant="bordered"
          className="p-2 text-xs text-[color:var(--theme-text-secondary)]"
        >
          <div className="flex items-center justify-between">
            <div className="font-semibold text-[color:var(--theme-text-primary)]">{obj.name}</div>
            {statusLabel && (
              <span className="text-[10px] text-[color:var(--theme-text-secondary)]">{statusLabel}</span>
            )}
          </div>
          <div>{obj.types.join(' ') || 'Unknown'}</div>
          {obj.power !== null && obj.toughness !== null && (
            <div>{obj.power}/{obj.toughness}</div>
          )}
        </Card>
      </button>
    );
  }

  return (
    <button type="button" onClick={onClick} className={`w-24 ${wrapperClass}`} title={statusDetail || undefined}>
      <div className="space-y-1">
        <div className="zone-card-face">
          <CardPreview card={card as CardData} disableClick />
          {isTapped && <span className="zone-card-overlay" aria-hidden="true" />}
        </div>
        {statusLabel && (
          <div className="text-[10px] text-[color:var(--theme-text-secondary)] text-center">{statusLabel}</div>
        )}
      </div>
    </button>
  );
}
