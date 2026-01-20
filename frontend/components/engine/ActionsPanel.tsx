'use client';

import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { TargetSelector } from '@/components/engine/TargetSelector';
import { EnterChoicesPanel } from '@/components/engine/EnterChoicesPanel';
import { SearchChoicePanel } from '@/components/engine/SearchChoicePanel';
import { ModalChoicePanel } from '@/components/engine/ModalChoicePanel';
import { ManaPaymentPanel } from '@/components/engine/ManaPaymentPanel';
import { WardPaymentPanel } from '@/components/engine/WardPaymentPanel';
import { ActivationCostPanel } from '@/components/engine/ActivationCostPanel';
import { OptionalCostPanel } from '@/components/engine/OptionalCostPanel';
import { ConspirePanel } from '@/components/engine/ConspirePanel';
import { SplicePanel } from '@/components/engine/SplicePanel';
import { EngineCardMap, EngineCombatStateSnapshot, EnginePlayerSnapshot } from '@/lib/engine';
import { EffectTargetGroup } from '@/hooks/useEffectTargeting';
import { ReplacementConflictEntry } from '@/hooks/useReplacementConflicts';
import { EnterChoiceConfig } from '@/lib/enterChoices';
import { ModalChoiceConfig } from '@/lib/modalChoices';
import { ManaPaymentDetail } from '@/lib/manaPayment';
import { ActivationCostEntry } from '@/hooks/useActivationCosts';
import { AlternativeCostOption, OptionalCastCostOption } from '@/lib/graphCosts';

interface ActionsPanelProps {
  loading: boolean;
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  preparedCast: { objectId: string; cost: any } | null;
  enterChoiceErrors: string[];
  manaPaymentErrors: string[];
  hasWardPaymentErrors: boolean;
  hasActivationCostErrors: boolean;
  hasAdditionalCastCostErrors: boolean;
  hasAlternativeExtraCostErrors: boolean;
  hasOptionalCastCostErrors: boolean;
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
  modalChoiceConfig: ModalChoiceConfig | null;
  selectedModalModes: string[];
  modalChoiceErrors: string[];
  onToggleModalMode: (modeId: string) => void;
  modalChoiceDisabled?: boolean;
  isComplexCost: boolean;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  costLabel: string;
  commanderTax: number;
  showCommanderTax: boolean;
  autoPayMana: boolean;
  onToggleAutoPay: (value: boolean) => void;
  onUpdatePaymentDetail: (updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  onUpdateManaPayment: (updater: (prev: Record<string, number>) => Record<string, number>) => void;
  activationCosts: ActivationCostEntry[];
  activationPayments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  onUpdateActivationPayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }
  ) => void;
  onUpdateActivationPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  additionalCastCosts: ActivationCostEntry[];
  additionalCastPayments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  onUpdateAdditionalCastPayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }
  ) => void;
  onUpdateAdditionalCastPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  alternativeExtraCosts: ActivationCostEntry[];
  alternativeExtraPayments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  alternativeExtraPaymentDetails: Record<number, ManaPaymentDetail>;
  alternativeExtraCostErrors: string[];
  onUpdateAlternativeExtraPayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }
  ) => void;
  onUpdateAlternativeExtraPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  alternativeCostOptions: AlternativeCostOption[];
  selectedAlternativeCostTag: string | null;
  onSelectAlternativeCost: (value: string | null) => void;
  optionalCostOptions: OptionalCastCostOption[];
  optionalCostSelections: Record<string, number>;
  optionalCostErrors: string[];
  onToggleOptionalCost: (tag: string) => void;
  onUpdateOptionalCostCount: (tag: string, count: number) => void;
  optionalCostEntries: ActivationCostEntry[];
  optionalCostPayments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  optionalCostPaymentDetails: Record<number, ManaPaymentDetail>;
  optionalCostPaymentErrors: string[];
  onUpdateOptionalCostPayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }
  ) => void;
  onUpdateOptionalCostPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  conspireEnabled: boolean;
  conspireOptions: Array<{ value: string; label: string }>;
  conspireSelections: string[];
  conspireError?: string | null;
  onToggleConspire: (value: string) => void;
  spliceOptions: Array<{ cardId: string; label: string; costs: Array<{ type: string; [key: string]: any }> }>;
  spliceSelections: string[];
  onToggleSpliceCard: (cardId: string) => void;
  spliceCosts: ActivationCostEntry[];
  splicePayments: Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
    exile_ids?: string[];
  }>;
  splicePaymentDetails: Record<number, ManaPaymentDetail>;
  spliceCostErrors: string[];
  onUpdateSplicePayment: (
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
      exile_ids?: string[];
    }
  ) => void;
  onUpdateSplicePaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  autoPayWard: boolean;
  onToggleAutoPayWard: (value: boolean) => void;
  wardTargets: Array<{
    objectId: string;
    name: string;
    costs: Array<{
      cost: any;
      costLabel?: string;
      discardOptions: Array<{ value: string; label: string }>;
      sacrificeOptions: Array<{ value: string; label: string }>;
      tapOptions: Array<{ value: string; label: string }>;
    }>;
    hasMultipleCosts: boolean;
  }>;
  wardPayments: Record<string, Array<{
    mana_payment?: Record<string, number>;
    mana_payment_detail?: ManaPaymentDetail;
    life_payment?: number;
    discard_id?: string;
    discard_ids?: string[];
    sacrifice_id?: string;
    tap_id?: string;
  }>>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  onUpdateWardPayment: (
    objectId: string,
    index: number,
    updater: (prev: {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }) => {
      mana_payment?: Record<string, number>;
      mana_payment_detail?: ManaPaymentDetail;
      life_payment?: number;
      discard_id?: string;
      discard_ids?: string[];
      sacrifice_id?: string;
      tap_id?: string;
    }
  ) => void;
  onUpdateWardPaymentDetail: (
    objectId: string,
    updater: (prev: ManaPaymentDetail) => ManaPaymentDetail
  ) => void;
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
  effectTargetGroups?: EffectTargetGroup[];
  copyEffectTargetGroups?: Array<EffectTargetGroup & { copyIndex: number }>;
  targetSelectionErrors?: string[];
  copyTargetSelections?: Array<{ objectIds: string[]; playerIds: number[] }>;
  searchChoiceEntries?: Array<{
    id: string;
    label: string;
    zone: string;
    candidates: Array<{ id: string; label: string }>;
    selectedIds: string[];
    maxSelections?: number | null;
    onChange: (ids: string[]) => void;
  }>;
  searchChoiceErrors?: string[];
  onChangeCopyTarget: (index: number, objectIds: string[], playerIds: number[]) => void;
}

export function ActionsPanel({
  loading,
  selectedHandId,
  selectedCommandId,
  selectedBattlefieldId,
  preparedCast,
  enterChoiceErrors,
  manaPaymentErrors,
  hasWardPaymentErrors,
  hasActivationCostErrors,
  hasAdditionalCastCostErrors,
  hasAlternativeExtraCostErrors,
  hasOptionalCastCostErrors,
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
  modalChoiceConfig,
  selectedModalModes,
  modalChoiceErrors,
  onToggleModalMode,
  modalChoiceDisabled = false,
  isComplexCost,
  manaPool,
  manaPayment,
  manaPaymentDetail,
  costLabel,
  commanderTax,
  showCommanderTax,
  autoPayMana,
  onToggleAutoPay,
  onUpdatePaymentDetail,
  onUpdateManaPayment,
  activationCosts,
  activationPayments,
  activationPaymentDetails,
  activationCostErrors,
  onUpdateActivationPayment,
  onUpdateActivationPaymentDetail,
  additionalCastCosts,
  additionalCastPayments,
  additionalCastPaymentDetails,
  additionalCastCostErrors,
  onUpdateAdditionalCastPayment,
  onUpdateAdditionalCastPaymentDetail,
  alternativeExtraCosts,
  alternativeExtraPayments,
  alternativeExtraPaymentDetails,
  alternativeExtraCostErrors,
  onUpdateAlternativeExtraPayment,
  onUpdateAlternativeExtraPaymentDetail,
  alternativeCostOptions,
  selectedAlternativeCostTag,
  onSelectAlternativeCost,
  optionalCostOptions,
  optionalCostSelections,
  optionalCostErrors,
  onToggleOptionalCost,
  onUpdateOptionalCostCount,
  optionalCostEntries,
  optionalCostPayments,
  optionalCostPaymentDetails,
  optionalCostPaymentErrors,
  onUpdateOptionalCostPayment,
  onUpdateOptionalCostPaymentDetail,
  conspireEnabled,
  conspireOptions,
  conspireSelections,
  conspireError,
  onToggleConspire,
  spliceOptions,
  spliceSelections,
  onToggleSpliceCard,
  spliceCosts,
  splicePayments,
  splicePaymentDetails,
  spliceCostErrors,
  onUpdateSplicePayment,
  onUpdateSplicePaymentDetail,
  autoPayWard,
  onToggleAutoPayWard,
  wardTargets,
  wardPayments,
  wardPaymentDetails,
  wardPaymentErrors,
  onUpdateWardPayment,
  onUpdateWardPaymentDetail,
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
  effectTargetGroups,
  targetSelectionErrors,
  copyEffectTargetGroups,
  copyTargetSelections,
  searchChoiceEntries,
  searchChoiceErrors,
  onChangeCopyTarget,
}: ActionsPanelProps) {
  const selectedCastId = selectedCommandId ?? selectedHandId;
  return (
    <Card variant="bordered" className="p-4 space-y-4">
      <div className="text-sm font-semibold text-[color:var(--theme-text-primary)]">Actions</div>
      <div className="flex flex-wrap gap-2">
        <Button variant="outline" onClick={onPlayLand} disabled={!selectedHandId || !isMainPhase || !isPriorityActivePlayer || loading}>
          Play Land
        </Button>
        <Button variant="outline" onClick={onPrepareCast} disabled={!selectedCastId || loading}>
          Prepare Cast
        </Button>
        <Button
          variant="outline"
          onClick={onFinalizeCast}
          disabled={
            !preparedCast ||
            preparedCast.objectId !== selectedCastId ||
            enterChoiceErrors.length > 0 ||
            modalChoiceErrors.length > 0 ||
            manaPaymentErrors.length > 0 ||
            hasWardPaymentErrors ||
            hasActivationCostErrors ||
            hasAdditionalCastCostErrors ||
            hasOptionalCastCostErrors ||
            hasAlternativeExtraCostErrors ||
            (targetSelectionErrors?.length ?? 0) > 0 ||
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
          disabled={
            !selectedBattlefieldId ||
            !hasActivatedAbility ||
            hasActivationCostErrors ||
            modalChoiceErrors.length > 0 ||
            (targetSelectionErrors?.length ?? 0) > 0 ||
            loading
          }
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
      <ModalChoicePanel
        config={modalChoiceConfig}
        selectedModes={selectedModalModes}
        errors={modalChoiceErrors}
        onToggleMode={onToggleModalMode}
        disabled={modalChoiceDisabled}
      />
      <OptionalCostPanel
        options={optionalCostOptions}
        selections={optionalCostSelections}
        errors={optionalCostErrors}
        onToggle={onToggleOptionalCost}
        onChangeCount={onUpdateOptionalCostCount}
      />
      <ConspirePanel
        enabled={conspireEnabled}
        options={conspireOptions}
        selections={conspireSelections}
        onToggle={onToggleConspire}
        error={conspireError}
      />
      <SplicePanel
        options={spliceOptions}
        selections={spliceSelections}
        onToggle={onToggleSpliceCard}
      />

      <ManaPaymentPanel
        active={!!(preparedCast && preparedCast.objectId === selectedCastId)}
        cost={preparedCast?.cost}
        costLabel={costLabel}
        commanderTax={commanderTax}
        showCommanderTax={showCommanderTax}
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

      <WardPaymentPanel
        active={selectedTargetObjectIds.length > 0}
        autoPayWard={autoPayWard}
        onToggleAutoPayWard={onToggleAutoPayWard}
        wardTargets={wardTargets}
        manaPool={manaPool}
        wardPayments={wardPayments}
        wardPaymentDetails={wardPaymentDetails}
        wardPaymentErrors={wardPaymentErrors}
        onUpdateWardPayment={onUpdateWardPayment}
        onUpdateWardPaymentDetail={onUpdateWardPaymentDetail}
      />

      <ActivationCostPanel
        active={hasActivatedAbility && !!selectedBattlefieldId}
        title="Activation Costs"
        costEntries={activationCosts}
        manaPool={manaPool}
        payments={activationPayments}
        paymentDetails={activationPaymentDetails}
        errors={activationCostErrors}
        onUpdatePayment={onUpdateActivationPayment}
        onUpdatePaymentDetail={onUpdateActivationPaymentDetail}
      />

      <ActivationCostPanel
        active={!!selectedCastId}
        title="Additional Casting Costs"
        costEntries={additionalCastCosts}
        manaPool={manaPool}
        payments={additionalCastPayments}
        paymentDetails={additionalCastPaymentDetails}
        errors={additionalCastCostErrors}
        onUpdatePayment={onUpdateAdditionalCastPayment}
        onUpdatePaymentDetail={onUpdateAdditionalCastPaymentDetail}
      />
      <ActivationCostPanel
        active={Object.values(optionalCostSelections).some((count) => count > 0)}
        title="Optional Costs"
        costEntries={optionalCostEntries}
        manaPool={manaPool}
        payments={optionalCostPayments}
        paymentDetails={optionalCostPaymentDetails}
        errors={optionalCostPaymentErrors}
        onUpdatePayment={onUpdateOptionalCostPayment}
        onUpdatePaymentDetail={onUpdateOptionalCostPaymentDetail}
      />
      <ActivationCostPanel
        active={spliceSelections.length > 0}
        title="Splice Costs"
        costEntries={spliceCosts}
        manaPool={manaPool}
        payments={splicePayments}
        paymentDetails={splicePaymentDetails}
        errors={spliceCostErrors}
        onUpdatePayment={onUpdateSplicePayment}
        onUpdatePaymentDetail={onUpdateSplicePaymentDetail}
      />

      <ActivationCostPanel
        active={!!selectedCastId}
        title="Alternative Cost Extras"
        costEntries={alternativeExtraCosts}
        manaPool={manaPool}
        payments={alternativeExtraPayments}
        paymentDetails={alternativeExtraPaymentDetails}
        errors={alternativeExtraCostErrors}
        onUpdatePayment={onUpdateAlternativeExtraPayment}
        onUpdatePaymentDetail={onUpdateAlternativeExtraPaymentDetail}
      />

      {alternativeCostOptions.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Alternative Cost</div>
          <label className="flex items-center gap-2 text-xs">
            <input
              type="radio"
              name="alt-cost"
              checked={!selectedAlternativeCostTag}
              onChange={() => onSelectAlternativeCost(null)}
            />
            Use mana cost
          </label>
          {alternativeCostOptions.map((option) => (
            <label key={`alt-cost-${option.tag}`} className="flex items-center gap-2 text-xs">
              <input
                type="radio"
                name="alt-cost"
                checked={selectedAlternativeCostTag === option.tag}
                onChange={() => onSelectAlternativeCost(option.tag)}
              />
              {option.label}
            </label>
          ))}
        </div>
      )}

      {searchChoiceEntries && searchChoiceEntries.length > 0 && (
        <div className="space-y-2">
          <SearchChoicePanel entries={searchChoiceEntries} cardMap={cardMap} />
          {searchChoiceErrors && searchChoiceErrors.length > 0 && (
            <div className="text-xs text-[color:var(--theme-status-error)]">
              {searchChoiceErrors.join(' ')}
            </div>
          )}
        </div>
      )}

      {effectTargetGroups && effectTargetGroups.length > 0 ? (
        <div className="space-y-4">
          {effectTargetGroups.map((group) => (
            <div key={group.id} className="space-y-2">
              <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">{group.label}</div>
              <TargetSelector
                objects={group.objects}
                players={group.players}
                cardMap={cardMap}
                selectedObjectIds={group.selectedObjectIds}
                selectedPlayerIds={group.selectedPlayerIds}
                objectLabel={group.objectLabel || objectLabel}
                playerLabel={group.playerLabel || 'Players'}
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
                <div className="text-xs text-[color:var(--theme-status-error)]">
                  {group.errors.join(' ')}
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
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
      )}
      {copyEffectTargetGroups && copyEffectTargetGroups.length > 0 && (
        <div className="space-y-3">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Copy Targets</div>
          {Array.from(new Set(copyEffectTargetGroups.map((entry) => entry.copyIndex))).map((copyIndex) => {
            const groups = copyEffectTargetGroups.filter((entry) => entry.copyIndex === copyIndex);
            return (
              <div key={`copy-effect-${copyIndex}`} className="space-y-2">
                <div className="text-xs text-[color:var(--theme-text-secondary)]">Copy {copyIndex + 1}</div>
                {groups.map((group) => (
                  <div key={group.id} className="space-y-2">
                    <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">{group.label}</div>
                    <TargetSelector
                      objects={group.objects}
                      players={group.players}
                      cardMap={cardMap}
                      selectedObjectIds={group.selectedObjectIds}
                      selectedPlayerIds={group.selectedPlayerIds}
                      objectLabel={group.objectLabel || objectLabel}
                      playerLabel={group.playerLabel || 'Players'}
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
                      <div className="text-xs text-[color:var(--theme-status-error)]">{group.errors.join(' ')}</div>
                    )}
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      )}
      {(!copyEffectTargetGroups || copyEffectTargetGroups.length === 0) &&
        copyTargetSelections &&
        copyTargetSelections.length > 0 && (
        <div className="space-y-3">
          <div className="text-xs uppercase text-[color:var(--theme-text-secondary)]">Copy Targets</div>
          {copyTargetSelections.map((entry, index) => (
            <div key={`copy-target-${index}`} className="space-y-2">
              <div className="text-xs text-[color:var(--theme-text-secondary)]">Copy {index + 1}</div>
              <TargetSelector
                objects={targetObjects}
                players={targetPlayers}
                cardMap={cardMap}
                selectedObjectIds={entry.objectIds}
                selectedPlayerIds={entry.playerIds}
                objectLabel={objectLabel}
                playerLabel="Players"
                maxObjectTargets={maxObjectTargets}
                maxPlayerTargets={maxPlayerTargets}
                objectTargetStatus={objectTargetStatus}
                playerTargetStatus={playerTargetStatus}
                onChangeObjects={(ids) => onChangeCopyTarget(index, ids, entry.playerIds)}
                onChangePlayers={(ids) => onChangeCopyTarget(index, entry.objectIds, ids)}
                onClear={() => onChangeCopyTarget(index, [], [])}
              />
            </div>
          ))}
        </div>
      )}
      {targetSelectionErrors && targetSelectionErrors.length > 0 && (
        <div className="text-xs text-[color:var(--theme-status-error)]">
          {targetSelectionErrors.join(' ')}
        </div>
      )}
    </Card>
  );
}

