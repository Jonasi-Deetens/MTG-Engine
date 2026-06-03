'use client';

import { MatZone } from './MatZone';
import { ZoneCard } from '../ZoneCard';
import { getObjectsByIds } from '../objectUtils';
import { getEtbChoiceDetail, getTemporaryDetail, getTemporaryStatus } from '../objectStatus';
import { EngineGameObjectSnapshot, EnginePlayerSnapshot, EngineCardMap } from '@/lib/engine';
import { BracketHeader, HudValue, StatusIndicator } from '@/components/ui/play/NierUIElements';

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
  const manaEntries = Object.entries(player.mana_pool).filter(([, value]) => value > 0);

  return (
    <div className="player-mat nier-panel">
      <div className="player-mat-header">
        <div className="space-y-2">
          <BracketHeader>PLAYER {String(player.id + 1).padStart(2, '0')}</BracketHeader>
          <div className="flex flex-wrap items-center gap-6">
            <HudValue label="Life" value={player.life} />
            <HudValue label="Mana Pool" value={manaTotal} tone="muted" />
          </div>
          {manaEntries.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-[color:var(--theme-text-muted)]">
              {manaEntries.map(([color, value]) => (
                <span key={color} className="flex items-center gap-2">
                  <span className="nier-mana-pip" />
                  {color}:{value}
                </span>
              ))}
            </div>
          )}
        </div>
        {isActive && (
          <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.22em] text-[color:var(--theme-text-secondary)]">
            <StatusIndicator tone="primary" pulse />
            Active
          </div>
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
