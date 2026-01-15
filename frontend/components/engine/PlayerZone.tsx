/* eslint-disable @next/next/no-img-element */
'use client';

import { CardPreview, CardData } from '@/components/cards/CardPreview';
import { Card } from '@/components/ui/Card';
import { EngineGameObjectSnapshot, EnginePlayerSnapshot, EngineCardMap } from '@/lib/engine';

interface PlayerZoneProps {
  player: EnginePlayerSnapshot;
  objects: EngineGameObjectSnapshot[];
  cardMap: EngineCardMap;
  isActive: boolean;
}

const getObjectsByIds = (ids: string[], objects: EngineGameObjectSnapshot[]) => {
  const map = new Map(objects.map((obj) => [obj.id, obj]));
  return ids.map((id) => map.get(id)).filter(Boolean) as EngineGameObjectSnapshot[];
};

const renderCard = (obj: EngineGameObjectSnapshot, cardMap: EngineCardMap) => {
  const card = cardMap[obj.id];
  if (!card) {
    return (
      <Card key={obj.id} variant="bordered" className="p-2 text-xs text-[color:var(--theme-text-secondary)]">
        <div className="font-semibold text-[color:var(--theme-text-primary)]">{obj.name}</div>
        <div>{obj.types.join(' ') || 'Unknown'}</div>
        {obj.power !== null && obj.toughness !== null && (
          <div>{obj.power}/{obj.toughness}</div>
        )}
      </Card>
    );
  }

  return (
    <div key={obj.id} className="w-24">
      <CardPreview card={card as CardData} disableClick />
    </div>
  );
};

export function PlayerZone({ player, objects, cardMap, isActive }: PlayerZoneProps) {
  const handObjects = getObjectsByIds(player.hand, objects);
  const battlefieldObjects = getObjectsByIds(player.battlefield, objects);
  const commandObjects = getObjectsByIds(player.command, objects);

  return (
    <Card variant="bordered" className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
            Player {player.id + 1}
          </div>
          <div className="text-sm text-[color:var(--theme-text-secondary)]">
            Life: {player.life} · Mana: {Object.values(player.mana_pool).reduce((sum, val) => sum + val, 0)}
          </div>
        </div>
        {isActive && (
          <span className="text-xs uppercase tracking-wide text-[color:var(--theme-accent-primary)]">
            Active
          </span>
        )}
      </div>

      <div>
        <div className="text-xs uppercase text-[color:var(--theme-text-secondary)] mb-2">Commander Zone</div>
        <div className="flex gap-2 flex-wrap">
          {commandObjects.length === 0 && (
            <span className="text-xs text-[color:var(--theme-text-secondary)]">No commander</span>
          )}
          {commandObjects.map((obj) => renderCard(obj, cardMap))}
        </div>
      </div>

      <div>
        <div className="text-xs uppercase text-[color:var(--theme-text-secondary)] mb-2">Battlefield</div>
        <div className="flex gap-2 flex-wrap">
          {battlefieldObjects.length === 0 && (
            <span className="text-xs text-[color:var(--theme-text-secondary)]">No permanents</span>
          )}
          {battlefieldObjects.map((obj) => renderCard(obj, cardMap))}
        </div>
      </div>

      <div>
        <div className="text-xs uppercase text-[color:var(--theme-text-secondary)] mb-2">
          Hand ({handObjects.length})
        </div>
        <div className="flex gap-2 flex-wrap">
          {handObjects.length === 0 && (
            <span className="text-xs text-[color:var(--theme-text-secondary)]">Empty hand</span>
          )}
          {handObjects.map((obj) => renderCard(obj, cardMap))}
        </div>
      </div>
    </Card>
  );
}
