/* eslint-disable @next/next/no-img-element */
'use client';

import { Card } from '@/components/ui/Card';
import { ZoneCard } from '@/components/engine/ZoneCard';
import { getObjectsByIds } from '@/components/engine/objectUtils';
import { getTemporaryDetail, getTemporaryStatus, getEtbChoiceDetail } from '@/components/engine/objectStatus';
import { EngineGameObjectSnapshot, EnginePlayerSnapshot, EngineCardMap } from '@/lib/engine';

interface PlayerZoneProps {
  player: EnginePlayerSnapshot;
  objects: EngineGameObjectSnapshot[];
  cardMap: EngineCardMap;
  isActive: boolean;
  selectedHandId?: string | null;
  selectedBattlefieldIds?: Set<string>;
  selectedBattlefieldId?: string | null;
  onSelectHand?: (objectId: string) => void;
  onToggleBattlefield?: (objectId: string) => void;
  onSelectBattlefield?: (objectId: string) => void;
}


export function PlayerZone({
  player,
  objects,
  cardMap,
  isActive,
  selectedHandId,
  selectedBattlefieldIds,
  selectedBattlefieldId,
  onSelectHand,
  onToggleBattlefield,
  onSelectBattlefield,
}: PlayerZoneProps) {
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
          {commandObjects.map((obj) => (
            <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
          ))}
        </div>
      </div>

      <div>
        <div className="text-xs uppercase text-[color:var(--theme-text-secondary)] mb-2">Battlefield</div>
        <div className="flex gap-2 flex-wrap">
          {battlefieldObjects.length === 0 && (
            <span className="text-xs text-[color:var(--theme-text-secondary)]">No permanents</span>
          )}
          {battlefieldObjects.map((obj) => (
            <ZoneCard
              key={obj.id}
              obj={obj}
              cardMap={cardMap}
              onClick={
                onToggleBattlefield
                  ? () => onToggleBattlefield(obj.id)
                  : onSelectBattlefield
                    ? () => onSelectBattlefield(obj.id)
                    : undefined
              }
              selected={onToggleBattlefield ? selectedBattlefieldIds?.has(obj.id) : selectedBattlefieldId === obj.id}
              statusLabel={getTemporaryStatus(obj)}
              statusDetail={[getTemporaryDetail(obj), getEtbChoiceDetail(obj)].filter(Boolean).join(' · ') || null}
            />
          ))}
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
          {handObjects.map((obj) => (
            <ZoneCard
              key={obj.id}
              obj={obj}
              cardMap={cardMap}
              onClick={onSelectHand ? () => onSelectHand(obj.id) : undefined}
              selected={selectedHandId === obj.id}
            />
          ))}
        </div>
      </div>
    </Card>
  );
}
