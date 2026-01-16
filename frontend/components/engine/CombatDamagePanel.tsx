'use client';

import { useMemo } from 'react';
import { Card } from '@/components/ui/Card';
import { EngineCardMap, EngineCombatStateSnapshot, EngineGameObjectSnapshot } from '@/lib/engine';
import { isEligibleForCombatPass } from '@/lib/combatDamage';

interface CombatDamagePanelProps {
  active: boolean;
  combatState: EngineCombatStateSnapshot | null | undefined;
  objects: EngineGameObjectSnapshot[];
  cardMap: EngineCardMap;
  defendingPlayerId: number | null;
  assignments: Record<string, Record<string, number>>;
  damagePass?: 'first_strike' | 'regular' | null;
  disabledReason?: string | null;
  onUpdateAssignment: (attackerId: string, targetId: string, value: number) => void;
}

export function CombatDamagePanel({
  active,
  combatState,
  objects,
  cardMap,
  defendingPlayerId,
  assignments,
  damagePass,
  disabledReason,
  onUpdateAssignment,
}: CombatDamagePanelProps) {
  const objectMap = useMemo(() => new Map(objects.map((obj) => [obj.id, obj])), [objects]);
  if (!active || !combatState) return null;

  return (
    <Card variant="bordered" className="p-4 space-y-3">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Combat Damage</div>
      {damagePass && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">
          {damagePass === 'first_strike' ? 'First strike damage' : 'Regular damage'}
        </div>
      )}
      {disabledReason && (
        <div className="text-xs text-[color:var(--theme-text-secondary)]">{disabledReason}</div>
      )}
      <div className="space-y-3">
        {combatState.attackers.map((attackerId) => {
          const attacker = objectMap.get(attackerId);
          if (!attacker) return null;
          if (!isEligibleForCombatPass(attacker.keywords, damagePass ?? undefined)) return null;
          const blockers = (combatState.blockers?.[attackerId] || [])
            .map((blockerId) => objectMap.get(blockerId))
            .filter((blocker) => blocker && blocker.zone === 'battlefield' && blocker.is_blocking);
          const attackerLabel = cardMap[attackerId]?.name || attacker.name || attackerId;
          const attackerAssignments = assignments[attackerId] || {};
          const canAssignToPlayer =
            blockers.length === 0 ||
            (Array.isArray(attacker.keywords) && attacker.keywords.includes('Trample'));
          const disabled = Boolean(disabledReason);

          return (
            <div key={`combat-assign-${attackerId}`} className="space-y-2">
              <div className="text-xs text-[color:var(--theme-text-secondary)]">
                {attackerLabel}
              </div>
              {blockers.length > 0 && (
                <div className="space-y-1">
                  {blockers.map((blocker) => {
                    const blockerLabel = cardMap[blocker.id]?.name || blocker.name || blocker.id;
                    const value = attackerAssignments[blocker.id] ?? 0;
                    return (
                      <div key={`assign-${attackerId}-${blocker.id}`} className="flex items-center gap-2">
                        <div className="text-xs text-[color:var(--theme-text-secondary)]">{blockerLabel}</div>
                        <input
                          type="number"
                          min={0}
                          value={value}
                          disabled={disabled}
                          onChange={(e) =>
                            onUpdateAssignment(attackerId, blocker.id, Math.max(0, Number(e.target.value || 0)))
                          }
                          className="w-16 px-2 py-1 text-xs bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                        />
                      </div>
                    );
                  })}
                </div>
              )}
              {canAssignToPlayer && typeof defendingPlayerId === 'number' && (
                <div className="flex items-center gap-2">
                  <div className="text-xs text-[color:var(--theme-text-secondary)]">
                    Player {defendingPlayerId + 1}
                  </div>
                  <input
                    type="number"
                    min={0}
                    value={attackerAssignments.player ?? 0}
                    disabled={disabled}
                    onChange={(e) =>
                      onUpdateAssignment(attackerId, 'player', Math.max(0, Number(e.target.value || 0)))
                    }
                    className="w-16 px-2 py-1 text-xs bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none"
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

