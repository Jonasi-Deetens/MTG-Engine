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
  selectedHandId?: string | null;
  selectedBattlefieldIds?: Set<string>;
  selectedBattlefieldId?: string | null;
  onSelectHand?: (objectId: string) => void;
  onToggleBattlefield?: (objectId: string) => void;
  onSelectBattlefield?: (objectId: string) => void;
}

const getObjectsByIds = (ids: string[], objects: EngineGameObjectSnapshot[]) => {
  const map = new Map(objects.map((obj) => [obj.id, obj]));
  return ids.map((id) => map.get(id)).filter(Boolean) as EngineGameObjectSnapshot[];
};

const renderCard = (
  obj: EngineGameObjectSnapshot,
  cardMap: EngineCardMap,
  options?: { onClick?: () => void; selected?: boolean; statusLabel?: string | null; statusDetail?: string | null }
) => {
  const card = cardMap[obj.id];
  const selectedClass = options?.selected ? 'ring-2 ring-amber-500 rounded-lg' : '';
  const statusLabel = options?.statusLabel;
  const statusDetail = options?.statusDetail;
  if (!card) {
    return (
      <button
        key={obj.id}
        type="button"
        onClick={options?.onClick}
        className={`text-left ${options?.onClick ? 'cursor-pointer' : 'cursor-default'} ${selectedClass}`}
      >
        <Card
          variant="bordered"
          className="p-2 text-xs text-[color:var(--theme-text-secondary)]"
          title={statusDetail || undefined}
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
    <button
      key={obj.id}
      type="button"
      onClick={options?.onClick}
      className={`w-24 ${options?.onClick ? 'cursor-pointer' : 'cursor-default'} ${selectedClass}`}
      title={statusDetail || undefined}
    >
      <div className="space-y-1">
      <CardPreview card={card as CardData} disableClick />
        {statusLabel && (
          <div className="text-[10px] text-[color:var(--theme-text-secondary)] text-center">{statusLabel}</div>
        )}
      </div>
    </button>
  );
};

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

  const getTemporaryStatus = (obj: EngineGameObjectSnapshot) => {
    const durations = (obj.temporary_effects || [])
      .map((effect: any) => effect?.duration)
      .filter((duration: string | undefined) => Boolean(duration));
    if (durations.length === 0) return null;
    if (durations.includes('until_end_of_turn')) return 'Until EOT';
    if (durations.includes('until_end_of_combat')) return 'Until combat';
    if (durations.includes('until_end_of_your_next_turn')) return 'Until your next turn';
    if (durations.includes('until_your_next_upkeep')) return 'Until your next upkeep';
    return 'Temporary';
  };

  const getTemporaryDetail = (obj: EngineGameObjectSnapshot) => {
    const effects = obj.temporary_effects || [];
    if (effects.length === 0) return null;
    return effects
      .map((effect: any) => {
        const type = effect?.type;
        const duration = effect?.duration ? ` (${effect.duration})` : '';
        if (type === 'add_keyword') {
          return `Gain ${effect.keyword || 'keyword'}${duration}`;
        }
        if (type === 'remove_keyword') {
          return `Lose ${effect.keyword || 'keyword'}${duration}`;
        }
        if (type === 'set_power_toughness') {
          return `Set ${effect.power ?? '?'} / ${effect.toughness ?? '?'}${duration}`;
        }
        if (type === 'modify_power_toughness') {
          const power = effect.power ?? 0;
          const toughness = effect.toughness ?? 0;
          const powerSign = power >= 0 ? '+' : '';
          const toughnessSign = toughness >= 0 ? '+' : '';
          return `Modify ${powerSign}${power}/${toughnessSign}${toughness}${duration}`;
        }
        if (effect?.prevent_damage) {
          return `Prevent ${effect.prevent_damage} damage${duration}`;
        }
        return `Temporary effect${duration}`;
      })
      .join(', ');
  };

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
          {battlefieldObjects.map((obj) =>
            renderCard(obj, cardMap, {
              onClick: onToggleBattlefield
                ? () => onToggleBattlefield(obj.id)
                : onSelectBattlefield
                  ? () => onSelectBattlefield(obj.id)
                  : undefined,
              selected: onToggleBattlefield
                ? selectedBattlefieldIds?.has(obj.id)
                : selectedBattlefieldId === obj.id,
              statusLabel: getTemporaryStatus(obj),
              statusDetail: getTemporaryDetail(obj),
            })
          )}
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
          {handObjects.map((obj) =>
            renderCard(obj, cardMap, {
              onClick: onSelectHand ? () => onSelectHand(obj.id) : undefined,
              selected: selectedHandId === obj.id,
            })
          )}
        </div>
      </div>
    </Card>
  );
}
