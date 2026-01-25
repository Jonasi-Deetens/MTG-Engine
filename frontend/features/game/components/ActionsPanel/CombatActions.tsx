'use client';

import { StylizedButton } from '@/components/ui/play/StylizedButton';
import { StylizedNativeSelect } from '@/components/ui/play/StylizedNativeSelect';
import { CombatDamagePanel } from '../CombatDamagePanel';
import { EngineCardMap, EngineCombatStateSnapshot } from '@/lib/engine';
import { ReplacementConflictEntry } from '../../hooks/useReplacementConflicts';

/**
 * CombatActions - Combat phase UI
 * 
 * Responsible for:
 * - Declare attackers button
 * - Declare blockers button
 * - Combat damage assignment
 * - Blocker ordering
 * - Defender selection
 */

interface CombatActionsProps {
  loading: boolean;
  isDeclareAttackers: boolean;
  isDeclareBlockers: boolean;
  isCombatDamage: boolean;
  isPriorityActivePlayer: boolean;
  isPriorityDefender: boolean;
  
  // Attacker selection
  selectedAttackers: Set<string>;
  selectedDefenderId: string | null;
  defenderOptions: Array<{ value: string; label: string }>;
  
  // Blocker selection
  activeAttackerId: string | null;
  activeBlockerOrder: string[];
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
  
  // Combat state
  combatState: EngineCombatStateSnapshot | null | undefined;
  cardMap: EngineCardMap;
  
  // Damage assignment
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: ReplacementConflictEntry[];
  
  // Actions
  onSelectDefender: (value: string | null) => void;
  onSelectActiveAttacker: (attackerId: string) => void;
  onReorderBlockerUp: (index: number) => void;
  onReorderBlockerDown: (index: number) => void;
  onDeclareAttackers: () => void;
  onDeclareBlockers: () => void;
  onAssignCombatDamage: () => void;
}

export function CombatActions({
  loading,
  isDeclareAttackers,
  isDeclareBlockers,
  isCombatDamage,
  isPriorityActivePlayer,
  isPriorityDefender,
  selectedAttackers,
  selectedDefenderId,
  defenderOptions,
  activeAttackerId,
  activeBlockerOrder,
  blockerErrors,
  blockerErrorMap,
  combatState,
  cardMap,
  hasUnresolvedDamageReplacements,
  unresolvedDamageReplacements,
  onSelectDefender,
  onSelectActiveAttacker,
  onReorderBlockerUp,
  onReorderBlockerDown,
  onDeclareAttackers,
  onDeclareBlockers,
  onAssignCombatDamage,
}: CombatActionsProps) {
  // Declare attackers phase
  if (isDeclareAttackers && isPriorityActivePlayer) {
    return (
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Declare Attackers</h3>
        
        {/* Defender Selection */}
        {defenderOptions.length > 1 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Attack Target</label>
            <StylizedNativeSelect
              value={selectedDefenderId ?? ''}
              onChange={(e) => onSelectDefender(e.target.value || null)}
            >
              <option value="">Select defender...</option>
              {defenderOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </StylizedNativeSelect>
          </div>
        )}

        <p className="text-sm text-muted-foreground">
          {selectedAttackers.size === 0
            ? 'Click creatures on the battlefield to select attackers'
            : `${selectedAttackers.size} attacker${selectedAttackers.size === 1 ? '' : 's'} selected`}
        </p>

        <StylizedButton
          onClick={onDeclareAttackers}
          disabled={loading}
          className="w-full"
        >
          Declare Attackers
        </StylizedButton>
      </div>
    );
  }

  // Declare blockers phase
  if (isDeclareBlockers && isPriorityDefender) {
    const attackers = combatState?.attackers ?? [];
    
    return (
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Declare Blockers</h3>

        {/* Attacker selection for blocking */}
        {attackers.length > 0 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Blocking</label>
            <StylizedNativeSelect
              value={activeAttackerId ?? ''}
              onChange={(e) => onSelectActiveAttacker(e.target.value)}
            >
              {attackers.map((attackerId) => {
                const name = cardMap[attackerId]?.name || attackerId;
                return (
                  <option key={attackerId} value={attackerId}>
                    {name}
                  </option>
                );
              })}
            </StylizedNativeSelect>
          </div>
        )}

        {/* Blocker order */}
        {activeBlockerOrder.length > 1 && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Blocker Order (damage assignment)</label>
            <div className="space-y-1">
              {activeBlockerOrder.map((blockerId, index) => {
                const name = cardMap[blockerId]?.name || blockerId;
                const errors = blockerErrorMap[blockerId] ?? [];
                return (
                  <div
                    key={blockerId}
                    className={`flex items-center justify-between rounded border p-2 ${
                      errors.length > 0 ? 'border-destructive' : ''
                    }`}
                  >
                    <span className="text-sm">
                      {index + 1}. {name}
                    </span>
                    <div className="flex gap-1">
                      <StylizedButton
                        variant="ghost"
                        onClick={() => onReorderBlockerUp(index)}
                        disabled={index === 0}
                        className="px-2 py-1 text-xs"
                      >
                        ↑
                      </StylizedButton>
                      <StylizedButton
                        variant="ghost"
                        onClick={() => onReorderBlockerDown(index)}
                        disabled={index === activeBlockerOrder.length - 1}
                        className="px-2 py-1 text-xs"
                      >
                        ↓
                      </StylizedButton>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Blocker errors */}
        {blockerErrors.length > 0 && (
          <div className="rounded border border-destructive bg-destructive/10 p-2">
            <ul className="text-sm text-destructive">
              {blockerErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}

        <StylizedButton
          onClick={onDeclareBlockers}
          disabled={loading || blockerErrors.length > 0}
          className="w-full"
        >
          Declare Blockers
        </StylizedButton>
      </div>
    );
  }

  // Combat damage phase
  if (isCombatDamage && isPriorityActivePlayer) {
    return (
      <div className="space-y-4">
        <h3 className="text-sm font-semibold">Combat Damage</h3>

        {hasUnresolvedDamageReplacements && (
          <div className="rounded border border-warning bg-warning/10 p-2">
            <p className="text-sm text-warning">
              {unresolvedDamageReplacements.length} damage replacement
              {unresolvedDamageReplacements.length === 1 ? '' : 's'} to resolve
            </p>
          </div>
        )}

        <StylizedButton
          onClick={onAssignCombatDamage}
          disabled={loading || hasUnresolvedDamageReplacements}
          className="w-full"
        >
          Assign Combat Damage
        </StylizedButton>
      </div>
    );
  }

  return null;
}
