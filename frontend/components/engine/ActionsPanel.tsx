'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { TargetSelector } from '@/components/engine/TargetSelector';
import { EnterChoicesPanel } from '@/components/engine/EnterChoicesPanel';
import { ManaPaymentPanel } from '@/components/engine/ManaPaymentPanel';
import { EngineCardMap, EngineCombatStateSnapshot } from '@/lib/engine';
import { ReplacementConflictEntry } from '@/hooks/useReplacementConflicts';
import { EnterChoiceConfig } from '@/lib/enterChoices';
import { ManaPaymentDetail } from '@/lib/manaPayment';

interface ActionsPanelProps {
  loading: boolean;
  selectedHandId: string | null;
  selectedBattlefieldId: string | null;
  preparedCast: { objectId: string; cost: any } | null;
  enterChoiceErrors: string[];
  manaPaymentErrors: string[];
  isMainPhase: boolean;
  isPriorityActivePlayer: boolean;
  isDeclareAttackers: boolean;
  isDeclareBlockers: boolean;
  isCombatDamage: boolean;
  isPriorityDefender: boolean;
  hasActivatedAbility: boolean;
  selectedAttackers: Set<string>;
  activeAttackerId: string | null;
  activeBlockerOrder: string[];
  selectedDefenderId: string | null;
  defenderOptions: Array<{ value: string; label: string }>;
  combatState: EngineCombatStateSnapshot | null | undefined;
  cardMap: EngineCardMap;
  onPlayLand: () => void;
  onPrepareCast: () => void;
  onFinalizeCast: () => void;
  onTapForMana: () => void;
  onActivateAbility: () => void;
  onDeclareAttackers: () => void;
  onDeclareBlockers: () => void;
  onAssignCombatDamage: () => void;
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: ReplacementConflictEntry[];
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
  onSelectDefender: (value: string | null) => void;
  onSelectActiveAttacker: (attackerId: string) => void;
  onReorderBlockerUp: (index: number) => void;
  onReorderBlockerDown: (index: number) => void;
  enterChoiceConfig: EnterChoiceConfig[];
  enterChoices: Record<string, string>;
  enterChoiceTargetOptions: Array<{ value: string; label: string }>;
  onEnterChoiceChange: (choiceType: string, value: string) => void;
  isComplexCost: boolean;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  costLabel: string;
  autoPayMana: boolean;
  onToggleAutoPay: (value: boolean) => void;
  onUpdatePaymentDetail: (updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  onUpdateManaPayment: (updater: (prev: Record<string, number>) => Record<string, number>) => void;
  targetObjects: any[];
  targetPlayers: EnginePlayerSnapshot[];
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  objectLabel: string;
  maxObjectTargets?: number;
  maxPlayerTargets?: number;
  objectTargetStatus: Record<string, boolean | null>;
  playerTargetStatus: Record<number, boolean | null>;
  onChangeTargetObjects: (ids: string[]) => void;
  onChangeTargetPlayers: (ids: number[]) => void;
  onClearTargets: () => void;
}

export function ActionsPanel({
  loading,
  selectedHandId,
  selectedBattlefieldId,
  preparedCast,
  enterChoiceErrors,
  manaPaymentErrors,
  isMainPhase,
  isPriorityActivePlayer,
  isDeclareAttackers,
  isDeclareBlockers,
  isCombatDamage,
  isPriorityDefender,
  hasActivatedAbility,
  selectedAttackers,
  activeAttackerId,
  activeBlockerOrder,
  selectedDefenderId,
  defenderOptions,
  combatState,
  cardMap,
  onPlayLand,
  onPrepareCast,
  onFinalizeCast,
  onTapForMana,
  onActivateAbility,
  onDeclareAttackers,
  onDeclareBlockers,
  onAssignCombatDamage,
  hasUnresolvedDamageReplacements,
  unresolvedDamageReplacements,
  blockerErrors,
  blockerErrorMap,
  onSelectDefender,
  onSelectActiveAttacker,
  onReorderBlockerUp,
  onReorderBlockerDown,
  enterChoiceConfig,
  enterChoices,
  enterChoiceTargetOptions,
  onEnterChoiceChange,
  isComplexCost,
  manaPool,
  manaPayment,
  manaPaymentDetail,
  costLabel,
  autoPayMana,
  onToggleAutoPay,
  onUpdatePaymentDetail,
  onUpdateManaPayment,
  targetObjects,
  targetPlayers,
  selectedTargetObjectIds,
  selectedTargetPlayerIds,
  objectLabel,
  maxObjectTargets,
  maxPlayerTargets,
  objectTargetStatus,
  playerTargetStatus,
  onChangeTargetObjects,
  onChangeTargetPlayers,
  onClearTargets,
}: ActionsPanelProps) {
  return (
    <Card variant="bordered" className="p-4 space-y-4">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Actions</div>
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" onClick={onPlayLand} disabled={!selectedHandId || !isMainPhase || !isPriorityActivePlayer || loading}>
          Play Land
        </Button>
        <Button variant="outline" onClick={onPrepareCast} disabled={!selectedHandId || loading}>
          Prepare Cast
        </Button>
        <Button
          variant="outline"
          onClick={onFinalizeCast}
          disabled={
            !preparedCast ||
            preparedCast.objectId !== selectedHandId ||
            enterChoiceErrors.length > 0 ||
            manaPaymentErrors.length > 0 ||
            loading
          }
        >
          Finalize Cast
        </Button>
        <Button variant="outline" onClick={onTapForMana} disabled={!selectedBattlefieldId || loading}>
          Tap for Mana
        </Button>
        <Button
          variant="outline"
          onClick={onActivateAbility}
          disabled={!selectedBattlefieldId || !hasActivatedAbility || loading}
        >
          Activate Ability
        </Button>
        <Button
          variant="outline"
          onClick={onDeclareAttackers}
          disabled={
            !isDeclareAttackers ||
            !isPriorityActivePlayer ||
            combatState?.attackers_declared ||
            loading
          }
        >
          Declare Attackers
        </Button>
        <Button
          variant="outline"
          onClick={onDeclareBlockers}
          disabled={
            !isDeclareBlockers ||
            !isPriorityDefender ||
            (combatState?.attackers?.length ? !activeAttackerId : false) ||
            combatState?.blockers_declared ||
            loading ||
            blockerErrors.length > 0
          }
        >
          Declare Blockers
        </Button>
        <Button
          variant="outline"
          onClick={onAssignCombatDamage}
          disabled={!isCombatDamage || !isPriorityActivePlayer || loading || hasUnresolvedDamageReplacements}
        >
          Assign Combat Damage
        </Button>
      </div>

      {isDeclareAttackers && (
        <div className="flex flex-wrap gap-3">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Defender</div>
          <select
            value={selectedDefenderId ?? ''}
            onChange={(e) => onSelectDefender(e.target.value || null)}
            className="px-3 py-1 bg-[color:var(--theme-input-bg)] text-[color:var(--theme-input-text)] rounded border border-[color:var(--theme-input-border)] focus:border-[color:var(--theme-border-focus)] focus:outline-none text-sm"
          >
            {defenderOptions.map((option) => (
              <option key={`defender-${option.value}`} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {isDeclareBlockers && combatState && (
        <div className="space-y-2">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Select Attacker</div>
          <div className="flex flex-wrap gap-2">
            {combatState.attackers.map((attackerId) => (
              <Button
                key={`attacker-${attackerId}`}
                variant={activeAttackerId === attackerId ? 'primary' : 'outline'}
                size="sm"
                onClick={() => onSelectActiveAttacker(attackerId)}
              >
                {cardMap[attackerId]?.name || attackerId}
              </Button>
            ))}
          </div>
          {activeAttackerId && activeBlockerOrder.length > 1 && (
            <div className="space-y-1">
              <div className="text-xs text-[color:var(--theme-text-secondary)]">
                Blocker order (assign damage in this order)
              </div>
              <div className="space-y-1">
                {activeBlockerOrder.map((blockerId, index) => (
                  <div key={`blocker-order-${blockerId}`} className="space-y-1">
                    <div className="flex items-center gap-2">
                      <div className="text-xs text-[color:var(--theme-text-secondary)]">
                        {cardMap[blockerId]?.name || blockerId}
                      </div>
                      <div className="flex gap-1">
                        <Button size="xs" variant="outline" onClick={() => onReorderBlockerUp(index)}>
                          ↑
                        </Button>
                        <Button size="xs" variant="outline" onClick={() => onReorderBlockerDown(index)}>
                          ↓
                        </Button>
                      </div>
                    </div>
                    {blockerErrorMap[blockerId]?.length ? (
                      <div className="text-xs text-[color:var(--theme-status-error)]">
                        {blockerErrorMap[blockerId].join(' ')}
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          )}
          {blockerErrors.length > 0 && (
            <div className="space-y-1 text-xs text-[color:var(--theme-status-error)]">
              {blockerErrors.map((error) => (
                <div key={error}>{error}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {isCombatDamage && hasUnresolvedDamageReplacements && (
        <div className="space-y-1 text-xs text-[color:var(--theme-text-secondary)]">
          <div>Choose a damage replacement/prevention before assigning combat damage.</div>
          {unresolvedDamageReplacements.length > 0 && (
            <div className="text-[color:var(--theme-text-muted)]">
              {unresolvedDamageReplacements.map((entry) => (
                <div key={`unresolved-${entry.key}`}>{entry.label}</div>
              ))}
            </div>
          )}
        </div>
      )}

      <EnterChoicesPanel
        configs={enterChoiceConfig}
        values={enterChoices}
        errors={enterChoiceErrors}
        targetOptions={enterChoiceTargetOptions}
        onChange={onEnterChoiceChange}
      />

      <ManaPaymentPanel
        active={!!(preparedCast && preparedCast.objectId === selectedHandId)}
        cost={preparedCast?.cost}
        costLabel={costLabel}
        autoPayMana={autoPayMana}
        isComplexCost={isComplexCost}
        manaPool={manaPool}
        manaPayment={manaPayment}
        manaPaymentDetail={manaPaymentDetail}
        errors={manaPaymentErrors}
        onToggleAutoPay={onToggleAutoPay}
        onUpdatePaymentDetail={onUpdatePaymentDetail}
        onUpdateManaPayment={onUpdateManaPayment}
      />

      <TargetSelector
        objects={targetObjects}
        players={targetPlayers}
        cardMap={cardMap}
        selectedObjectIds={selectedTargetObjectIds}
        selectedPlayerIds={selectedTargetPlayerIds}
        objectLabel={objectLabel}
        playerLabel="Players"
        maxObjectTargets={maxObjectTargets}
        maxPlayerTargets={maxPlayerTargets}
        objectTargetStatus={objectTargetStatus}
        playerTargetStatus={playerTargetStatus}
        onChangeObjects={onChangeTargetObjects}
        onChangePlayers={onChangeTargetPlayers}
        onClear={onClearTargets}
      />
    </Card>
  );
}

