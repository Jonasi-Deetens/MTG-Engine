'use client';

import { TargetSelector } from '../TargetSelector';
import { EffectTargetGroup } from '../../hooks/useEffectTargeting';
import { EngineCardMap } from '@/lib/engine';

/**
 * TargetingSection - Target selection UI
 * 
 * Responsible for:
 * - Effect-based target selection
 * - Global target selection
 * - Copy spell target selection
 * - Target validation display
 */

interface TargetingSectionProps {
  // Effect targeting
  effectTargetGroups: EffectTargetGroup[];
  hasEffectTargets: boolean;
  
  // Global targeting
  filteredTargetableObjects: any[];
  filteredTargetPlayers: any[];
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  objectTargetStatus: Record<string, boolean | null>;
  playerTargetStatus: Record<number, boolean | null>;
  maxObjectTargets?: number | null;
  maxPlayerTargets?: number | null;
  objectLabel?: string;
  playerLabel?: string;
  
  // Copy targets
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
  copyTargetSelections: Array<{ objectIds: string[]; playerIds: number[] }>;
  copyTargetErrors: string[];
  copyEffectTargetGroups?: Array<EffectTargetGroup & { copyIndex: number }>;
  
  // Target errors
  targetSelectionErrors: string[];
  globalTargetErrors: string[];
  
  // Card info
  cardMap: EngineCardMap;
  
  // Actions
  onChangeTargetObjects: (ids: string[]) => void;
  onChangeTargetPlayers: (ids: number[]) => void;
  onChangeCopyTargetSelection: (index: number, selection: { objectIds: string[]; playerIds: number[] }) => void;
}

export function TargetingSection({
  effectTargetGroups,
  hasEffectTargets,
  filteredTargetableObjects,
  filteredTargetPlayers,
  selectedTargetObjectIds,
  selectedTargetPlayerIds,
  objectTargetStatus,
  playerTargetStatus,
  maxObjectTargets,
  maxPlayerTargets,
  objectLabel = 'Objects',
  playerLabel = 'Players',
  copyTargetsEnabled,
  copyTargetsCount,
  copyTargetSelections,
  copyTargetErrors,
  copyEffectTargetGroups,
  targetSelectionErrors,
  globalTargetErrors,
  cardMap,
  onChangeTargetObjects,
  onChangeTargetPlayers,
  onChangeCopyTargetSelection,
}: TargetingSectionProps) {
  if (!hasEffectTargets && filteredTargetableObjects.length === 0 && filteredTargetPlayers.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold">Targets</h3>

      {/* Effect-based targeting */}
      {hasEffectTargets && effectTargetGroups.map((group) => (
        <div key={group.id} className="space-y-2">
          <label className="text-sm font-medium">{group.label}</label>
          <TargetSelector
            objects={group.objects}
            players={group.players}
            cardMap={cardMap}
            selectedObjectIds={group.selectedObjectIds}
            selectedPlayerIds={group.selectedPlayerIds}
            objectLabel={group.objectLabel ?? objectLabel}
            playerLabel={group.playerLabel ?? playerLabel}
            maxObjectTargets={group.maxObjectTargets ?? undefined}
            maxPlayerTargets={group.maxPlayerTargets ?? undefined}
            objectTargetStatus={group.objectTargetStatus}
            playerTargetStatus={group.playerTargetStatus}
            onChangeObjects={group.onChangeObjects}
            onChangePlayers={group.onChangePlayers}
            onClear={group.onClear}
          />
          {typeof group.minTargets === 'number' && group.minTargets > 0 && (
            <div className="text-xs text-[color:var(--theme-text-secondary)]">
              Minimum targets: {group.minTargets}
            </div>
          )}
          {group.errors && group.errors.length > 0 && (
            <ul className="text-sm text-destructive">
              {group.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          )}
        </div>
      ))}

      {/* Global targeting (for simple spells) */}
      {!hasEffectTargets && (
        <TargetSelector
          objects={filteredTargetableObjects}
          players={filteredTargetPlayers}
          cardMap={cardMap}
          selectedObjectIds={selectedTargetObjectIds}
          selectedPlayerIds={selectedTargetPlayerIds}
          objectLabel={objectLabel}
          playerLabel={playerLabel}
          maxObjectTargets={maxObjectTargets ?? undefined}
          maxPlayerTargets={maxPlayerTargets ?? undefined}
          objectTargetStatus={objectTargetStatus}
          playerTargetStatus={playerTargetStatus}
          onChangeObjects={onChangeTargetObjects}
          onChangePlayers={onChangeTargetPlayers}
          onClear={() => {
            onChangeTargetObjects([]);
            onChangeTargetPlayers([]);
          }}
        />
      )}

      {/* Copy spell targets */}
      {copyEffectTargetGroups && copyEffectTargetGroups.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Copy Targets</h4>
          {Array.from(new Set(copyEffectTargetGroups.map((entry) => entry.copyIndex))).map((copyIndex) => {
            const groups = copyEffectTargetGroups.filter((entry) => entry.copyIndex === copyIndex);
            return (
              <div key={`copy-effect-${copyIndex}`} className="space-y-2">
                <div className="text-xs text-[color:var(--theme-text-secondary)]">Copy {copyIndex + 1}</div>
                {groups.map((group) => (
                  <div key={group.id} className="space-y-2">
                    <label className="text-xs uppercase text-[color:var(--theme-text-secondary)]">
                      {group.label}
                    </label>
                    <TargetSelector
                      objects={group.objects}
                      players={group.players}
                      cardMap={cardMap}
                      selectedObjectIds={group.selectedObjectIds}
                      selectedPlayerIds={group.selectedPlayerIds}
                      objectLabel={group.objectLabel ?? objectLabel}
                      playerLabel={group.playerLabel ?? playerLabel}
                      maxObjectTargets={group.maxObjectTargets ?? undefined}
                      maxPlayerTargets={group.maxPlayerTargets ?? undefined}
                      onChangeObjects={group.onChangeObjects}
                      onChangePlayers={group.onChangePlayers}
                      onClear={group.onClear}
                    />
                    {typeof group.minTargets === 'number' && group.minTargets > 0 && (
                      <div className="text-xs text-[color:var(--theme-text-secondary)]">
                        Minimum targets: {group.minTargets}
                      </div>
                    )}
                    {group.errors && group.errors.length > 0 && (
                      <div className="text-xs text-[color:var(--theme-status-error)]">
                        {group.errors.join(' ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}

      {!copyEffectTargetGroups && copyTargetsEnabled && copyTargetsCount > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Copy Targets</h4>
          {Array.from({ length: copyTargetsCount }).map((_, index) => {
            const selection = copyTargetSelections[index] ?? { objectIds: [], playerIds: [] };
            return (
              <div key={index} className="rounded border p-2 space-y-2">
                <label className="text-xs text-muted-foreground">Copy {index + 1}</label>
                
                <TargetSelector
                  objects={filteredTargetableObjects}
                  players={filteredTargetPlayers}
                  cardMap={cardMap}
                  selectedObjectIds={selection.objectIds}
                  selectedPlayerIds={selection.playerIds}
                  objectLabel={objectLabel}
                  playerLabel={playerLabel}
                  maxObjectTargets={maxObjectTargets ?? undefined}
                  maxPlayerTargets={maxPlayerTargets ?? undefined}
                  onChangeObjects={(ids) => onChangeCopyTargetSelection(index, { ...selection, objectIds: ids })}
                  onChangePlayers={(ids) =>
                    onChangeCopyTargetSelection(index, { ...selection, playerIds: ids })
                  }
                  onClear={() => onChangeCopyTargetSelection(index, { objectIds: [], playerIds: [] })}
                />
              </div>
            );
          })}
        </div>
      )}

      {/* Target selection errors */}
      {targetSelectionErrors.length > 0 && (
        <div className="rounded border border-destructive bg-destructive/10 p-2">
          <ul className="text-sm text-destructive">
            {targetSelectionErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Global target errors */}
      {globalTargetErrors.length > 0 && (
        <div className="rounded border border-warning bg-warning/10 p-2">
          <ul className="text-sm text-warning">
            {globalTargetErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Copy target errors */}
      {copyTargetErrors.length > 0 && (
        <div className="rounded border border-destructive bg-destructive/10 p-2">
          <ul className="text-sm text-destructive">
            {copyTargetErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
