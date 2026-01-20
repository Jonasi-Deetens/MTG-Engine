'use client';

import { MatZone } from '@/components/engine/playmat/MatZone';
import { ZoneCard } from '@/components/engine/ZoneCard';
import { getObjectsByIds } from '@/components/engine/objectUtils';
import { getEtbChoiceDetail, getTemporaryDetail, getTemporaryStatus } from '@/components/engine/objectStatus';
import { EngineGameObjectSnapshot, EnginePlayerSnapshot, EngineCardMap } from '@/lib/engine';

interface PlayerMatProps {
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

export function PlayerMat({
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
}: PlayerMatProps) {
  const handObjects = getObjectsByIds(player.hand, objects);
  const battlefieldObjects = getObjectsByIds(player.battlefield, objects);
  const commandObjects = getObjectsByIds(player.command, objects);
  const graveyardObjects = getObjectsByIds(player.graveyard, objects);
  const exileObjects = getObjectsByIds(player.exile, objects);
  const libraryCount = player.library.length;
  const manaTotal = Object.values(player.mana_pool).reduce((sum, val) => sum + val, 0);

  return (
    <div className="rounded-2xl border border-[color:var(--theme-border)] bg-[color:var(--theme-bg-secondary)]/10 p-4 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
            Player {player.id + 1}
          </div>
          <div className="text-sm text-[color:var(--theme-text-secondary)]">
            Life: {player.life} · Mana: {manaTotal}
          </div>
        </div>
        {isActive && (
          <span className="text-xs uppercase tracking-wide text-[color:var(--theme-accent-primary)]">
            Active
          </span>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-6">
        <MatZone title="Battlefield" count={battlefieldObjects.length} className="lg:col-span-4">
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
        </MatZone>

        <MatZone title="Hand" count={handObjects.length} className="lg:col-span-2">
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
        </MatZone>

        <MatZone title="Command" count={commandObjects.length} className="lg:col-span-2">
          <div className="flex gap-2 flex-wrap">
            {commandObjects.length === 0 && (
              <span className="text-xs text-[color:var(--theme-text-secondary)]">No commander</span>
            )}
            {commandObjects.map((obj) => (
              <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
            ))}
          </div>
        </MatZone>

        <MatZone title="Graveyard" count={graveyardObjects.length} className="lg:col-span-2">
          <div className="flex gap-2 flex-wrap">
            {graveyardObjects.length === 0 && (
              <span className="text-xs text-[color:var(--theme-text-secondary)]">Empty graveyard</span>
            )}
            {graveyardObjects.map((obj) => (
              <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
            ))}
          </div>
        </MatZone>

        <MatZone title="Exile" count={exileObjects.length} className="lg:col-span-2">
          <div className="flex gap-2 flex-wrap">
            {exileObjects.length === 0 && (
              <span className="text-xs text-[color:var(--theme-text-secondary)]">Empty exile</span>
            )}
            {exileObjects.map((obj) => (
              <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
            ))}
          </div>
        </MatZone>

        <MatZone title="Library" count={libraryCount} className="lg:col-span-2">
          <div className="text-sm text-[color:var(--theme-text-secondary)]">{libraryCount} cards</div>
        </MatZone>
      </div>
    </div>
  );
}
