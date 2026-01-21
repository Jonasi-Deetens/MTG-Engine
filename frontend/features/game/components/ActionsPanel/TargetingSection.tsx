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
  
  // Copy targets
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
  copyTargetSelections: Array<{ objectIds: string[]; playerIds: number[] }>;
  copyTargetErrors: string[];
  
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
  copyTargetsEnabled,
  copyTargetsCount,
  copyTargetSelections,
  copyTargetErrors,
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
          
          {group.objects.length > 0 && (
            <TargetSelector
              label={group.objectLabel ?? 'Objects'}
              options={group.objects.map((obj) => ({
                value: obj.id,
                label: cardMap[obj.id]?.name || obj.name || obj.id,
                status: group.objectTargetStatus?.[obj.id] ?? null,
              }))}
              selectedIds={group.selectedObjectIds}
              onChange={(ids) => group.onChangeObjects(ids)}
              maxSelections={group.maxObjectTargets ?? undefined}
            />
          )}
          
          {group.players.length > 0 && (
            <TargetSelector
              label={group.playerLabel ?? 'Players'}
              options={group.players.map((player) => ({
                value: player.id.toString(),
                label: `Player ${player.id + 1}`,
                status: group.playerTargetStatus?.[player.id] ?? null,
              }))}
              selectedIds={group.selectedPlayerIds.map(String)}
              onChange={(ids) => group.onChangePlayers(ids.map(Number))}
              maxSelections={group.maxPlayerTargets ?? undefined}
            />
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
        <>
          {filteredTargetableObjects.length > 0 && (
            <TargetSelector
              label="Target Objects"
              options={filteredTargetableObjects.map((obj) => ({
                value: obj.id,
                label: cardMap[obj.id]?.name || obj.name || obj.id,
                status: objectTargetStatus[obj.id] ?? null,
              }))}
              selectedIds={selectedTargetObjectIds}
              onChange={onChangeTargetObjects}
            />
          )}
          
          {filteredTargetPlayers.length > 0 && (
            <TargetSelector
              label="Target Players"
              options={filteredTargetPlayers.map((player) => ({
                value: player.id.toString(),
                label: `Player ${player.id + 1}`,
                status: playerTargetStatus[player.id] ?? null,
              }))}
              selectedIds={selectedTargetPlayerIds.map(String)}
              onChange={(ids) => onChangeTargetPlayers(ids.map(Number))}
            />
          )}
        </>
      )}

      {/* Copy spell targets */}
      {copyTargetsEnabled && copyTargetsCount > 0 && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Copy Targets</h4>
          {Array.from({ length: copyTargetsCount }).map((_, index) => {
            const selection = copyTargetSelections[index] ?? { objectIds: [], playerIds: [] };
            return (
              <div key={index} className="rounded border p-2 space-y-2">
                <label className="text-xs text-muted-foreground">Copy {index + 1}</label>
                
                {filteredTargetableObjects.length > 0 && (
                  <TargetSelector
                    label="Objects"
                    options={filteredTargetableObjects.map((obj) => ({
                      value: obj.id,
                      label: cardMap[obj.id]?.name || obj.name || obj.id,
                      status: null,
                    }))}
                    selectedIds={selection.objectIds}
                    onChange={(ids) => onChangeCopyTargetSelection(index, { ...selection, objectIds: ids })}
                  />
                )}
                
                {filteredTargetPlayers.length > 0 && (
                  <TargetSelector
                    label="Players"
                    options={filteredTargetPlayers.map((player) => ({
                      value: player.id.toString(),
                      label: `Player ${player.id + 1}`,
                      status: null,
                    }))}
                    selectedIds={selection.playerIds.map(String)}
                    onChange={(ids) => onChangeCopyTargetSelection(index, { ...selection, playerIds: ids.map(Number) })}
                  />
                )}
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
