import { EngineCardMap, EngineGameObjectSnapshot, EnginePlayerSnapshot } from '@/lib/engine';

interface TargetSelectorProps {
  objects: EngineGameObjectSnapshot[];
  players: EnginePlayerSnapshot[];
  cardMap: EngineCardMap;
  selectedObjectIds: string[];
  selectedPlayerIds: number[];
  objectLabel?: string;
  playerLabel?: string;
  maxObjectTargets?: number | null;
  maxPlayerTargets?: number | null;
  objectTargetStatus?: Record<string, boolean | null>;
  playerTargetStatus?: Record<number, boolean | null>;
  onChangeObjects: (next: string[]) => void;
  onChangePlayers: (next: number[]) => void;
  onClear: () => void;
}

export function TargetSelector({
  objects,
  players,
  cardMap,
  selectedObjectIds,
  selectedPlayerIds,
  objectLabel = 'Objects',
  playerLabel = 'Players',
  maxObjectTargets = null,
  maxPlayerTargets = null,
  objectTargetStatus,
  playerTargetStatus,
  onChangeObjects,
  onChangePlayers,
  onClear,
}: TargetSelectorProps) {
  const renderStatus = (isLegal?: boolean | null) => {
    if (isLegal === undefined || isLegal === null) {
      return <span className="w-2 h-2 rounded-full bg-[color:var(--theme-border-default)]" />;
    }
    return (
      <span
        className={`w-2 h-2 rounded-full ${
          isLegal ? 'bg-[color:var(--theme-status-success)]' : 'bg-[color:var(--theme-status-error)]'
        }`}
      />
    );
  };
  const toggleObject = (objectId: string) => {
    if (selectedObjectIds.includes(objectId)) {
      onChangeObjects(selectedObjectIds.filter((id) => id !== objectId));
      return;
    }
    if (maxObjectTargets && selectedObjectIds.length >= maxObjectTargets) {
      return;
    }
    onChangeObjects([...selectedObjectIds, objectId]);
  };

  const togglePlayer = (playerId: number) => {
    if (selectedPlayerIds.includes(playerId)) {
      onChangePlayers(selectedPlayerIds.filter((id) => id !== playerId));
      return;
    }
    if (maxPlayerTargets && selectedPlayerIds.length >= maxPlayerTargets) {
      return;
    }
    onChangePlayers([...selectedPlayerIds, playerId]);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Targets</div>
        <button
          type="button"
          onClick={onClear}
          className="text-xs text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]"
        >
          Clear
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-2">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">{objectLabel}</div>
          {maxObjectTargets && (
            <div className="text-[color:var(--theme-text-secondary)] text-xs">
              {selectedObjectIds.length}/{maxObjectTargets} selected
            </div>
          )}
          <div className="space-y-1 max-h-40 overflow-auto pr-1">
            {objects.length === 0 && (
              <div className="text-xs text-[color:var(--theme-text-secondary)]">No objects</div>
            )}
            {objects.map((obj) => (
              <label key={`target-${obj.id}`} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedObjectIds.includes(obj.id)}
                  onChange={() => toggleObject(obj.id)}
                  disabled={
                    !!maxObjectTargets &&
                    selectedObjectIds.length >= maxObjectTargets &&
                    !selectedObjectIds.includes(obj.id)
                  }
                />
                {renderStatus(objectTargetStatus?.[obj.id])}
                <span className="text-[color:var(--theme-text-secondary)]">
                  {cardMap[obj.id]?.name || obj.name}
                </span>
              </label>
            ))}
          </div>
        </div>
        <div className="space-y-2">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">{playerLabel}</div>
          {maxPlayerTargets && (
            <div className="text-[color:var(--theme-text-secondary)] text-xs">
              {selectedPlayerIds.length}/{maxPlayerTargets} selected
            </div>
          )}
          <div className="space-y-1">
            {players.map((player) => (
              <label key={`target-player-${player.id}`} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selectedPlayerIds.includes(player.id)}
                  onChange={() => togglePlayer(player.id)}
                  disabled={
                    !!maxPlayerTargets &&
                    selectedPlayerIds.length >= maxPlayerTargets &&
                    !selectedPlayerIds.includes(player.id)
                  }
                />
                {renderStatus(playerTargetStatus?.[player.id])}
                <span className="text-[color:var(--theme-text-secondary)]">Player {player.id + 1}</span>
              </label>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

