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
  selectedCommandId?: string | null;
  selectedBattlefieldIds?: Set<string>;
  selectedBattlefieldId?: string | null;
  onSelectHand?: (objectId: string) => void;
  onSelectCommand?: (objectId: string) => void;
  onToggleBattlefield?: (objectId: string) => void;
  onSelectBattlefield?: (objectId: string) => void;
}

export function PlayerMat({
  player,
  objects,
  cardMap,
  isActive,
  selectedHandId,
  selectedCommandId,
  selectedBattlefieldIds,
  selectedBattlefieldId,
  onSelectHand,
  onSelectCommand,
  onToggleBattlefield,
  onSelectBattlefield,
}: PlayerMatProps) {
  const handObjects = getObjectsByIds(player.hand, objects, 'hand');
  const battlefieldObjects = getObjectsByIds(player.battlefield, objects, 'battlefield');
  const commandObjects = getObjectsByIds(player.command, objects, 'command');
  const graveyardObjects = getObjectsByIds(player.graveyard, objects, 'graveyard');
  const exileObjects = getObjectsByIds(player.exile, objects, 'exile');
  const libraryCount = player.library.length;
  const manaTotal = Object.values(player.mana_pool).reduce((sum, val) => sum + val, 0);

  return (
    <div className="player-mat">
      <div className="player-mat-header">
        <div>
          <div className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
            Player {player.id + 1}
          </div>
          <div className="text-sm text-[color:var(--theme-text-secondary)]">
            Life: {player.life} · Mana: {manaTotal}
          </div>
        </div>
        {isActive && (
          <span className="player-mat-active">
            Active
          </span>
        )}
      </div>

      <div className="player-mat-grid">
        <MatZone title="Battlefield" count={battlefieldObjects.length} className="player-mat-battlefield">
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
                className={obj.tapped ? 'zone-card-tapped' : undefined}
              />
            ))}
          </div>
        </MatZone>

        <div className="player-mat-side">
          <MatZone title="Library" count={libraryCount}>
            <div className="deck-stack" aria-label={`Library with ${libraryCount} cards`}>
              <div className="deck-card deck-card-1" />
              <div className="deck-card deck-card-2" />
              <div className="deck-card deck-card-3" />
              <span className="deck-count">{libraryCount}</span>
            </div>
          </MatZone>

          <MatZone title="Graveyard" count={graveyardObjects.length}>
            <div className="flex gap-2 flex-wrap">
              {graveyardObjects.length === 0 && (
                <span className="text-xs text-[color:var(--theme-text-secondary)]">Empty graveyard</span>
              )}
              {graveyardObjects.map((obj) => (
                <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
              ))}
            </div>
          </MatZone>

          <MatZone title="Exile" count={exileObjects.length}>
            <div className="flex gap-2 flex-wrap">
              {exileObjects.length === 0 && (
                <span className="text-xs text-[color:var(--theme-text-secondary)]">Empty exile</span>
              )}
              {exileObjects.map((obj) => (
                <ZoneCard key={obj.id} obj={obj} cardMap={cardMap} />
              ))}
            </div>
          </MatZone>

          <MatZone title="Command" count={commandObjects.length}>
            <div className="flex gap-2 flex-wrap">
              {commandObjects.length === 0 && (
                <span className="text-xs text-[color:var(--theme-text-secondary)]">No commander</span>
              )}
              {commandObjects.map((obj) => (
              <ZoneCard
                key={obj.id}
                obj={obj}
                cardMap={cardMap}
                onClick={onSelectCommand ? () => onSelectCommand(obj.id) : undefined}
                selected={selectedCommandId === obj.id}
              />
              ))}
            </div>
          </MatZone>
        </div>

        <MatZone title="Hand" count={handObjects.length} className="player-mat-hand">
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
      </div>
    </div>
  );
}
