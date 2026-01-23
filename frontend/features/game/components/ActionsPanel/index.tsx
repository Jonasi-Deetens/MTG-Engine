'use client';

import { Card } from '@/components/ui/Card';
import { CastingActions } from './CastingActions';
import { CombatActions } from './CombatActions';
import { TargetingSection } from './TargetingSection';
import { ChoicesSection } from './ChoicesSection';
import { EngineCardMap, EngineCombatStateSnapshot } from '@/lib/engine';
import { EffectTargetGroup } from '../../hooks/useEffectTargeting';
import { ReplacementConflictEntry } from '../../hooks/useReplacementConflicts';
import { EnterChoiceConfig } from '@/lib/enterChoices';
import { ModalChoiceConfig } from '@/lib/modalChoices';
import { ManaPaymentDetail } from '@/lib/manaPayment';
import { ActivationCostEntry } from '../../hooks/useActivationCosts';
import { AlternativeCostOption, OptionalCastCostOption } from '@/lib/graphCosts';

/**
 * ActionsPanel - Coordinator component for game actions
 * 
 * This component orchestrates the sub-components:
 * - CastingActions: Spell casting, mana payment, costs
 * - CombatActions: Attackers, blockers, damage
 * - TargetingSection: Target selection
 * - ChoicesSection: Modal, enter, search, replacement choices
 */

// Re-export sub-components for direct usage if needed
export { CastingActions } from './CastingActions';
export { CombatActions } from './CombatActions';
export { TargetingSection } from './TargetingSection';
export { ChoicesSection } from './ChoicesSection';

interface ActionsPanelProps {
  loading: boolean;
  
  // Selection state
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  
  // Casting state
  preparedCast: { objectId: string; cost: any } | null;
  isMainPhase: boolean;
  isPriorityActivePlayer: boolean;
  hasActivatedAbility: boolean;
  
  // Combat state
  isDeclareAttackers: boolean;
  isDeclareBlockers: boolean;
  isCombatDamage: boolean;
  isPriorityDefender: boolean;
  selectedAttackers: Set<string>;
  activeAttackerId: string | null;
  activeBlockerOrder: string[];
  selectedDefenderId: string | null;
  defenderOptions: Array<{ value: string; label: string }>;
  combatState: EngineCombatStateSnapshot | null | undefined;
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: ReplacementConflictEntry[];
  
  // Mana payment
  isComplexCost: boolean;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  costLabel: string;
  commanderTax: number;
  showCommanderTax: boolean;
  autoPayMana: boolean;
  manaPaymentErrors: string[];
  onToggleAutoPay: (value: boolean) => void;
  onUpdatePaymentDetail: (updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  onUpdateManaPayment: (updater: (prev: Record<string, number>) => Record<string, number>) => void;
  
  // Targeting
  effectTargetGroups: EffectTargetGroup[];
  hasEffectTargets: boolean;
  filteredTargetableObjects: any[];
  filteredTargetPlayers: any[];
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  objectTargetStatus: Record<string, boolean | null>;
  playerTargetStatus: Record<number, boolean | null>;
  targetSelectionErrors: string[];
  globalTargetErrors: string[];
  
  // Copy targets
  copyTargetsEnabled: boolean;
  copyTargetsCount: number;
  copyTargetSelections: Array<{ objectIds: string[]; playerIds: number[] }>;
  copyTargetErrors: string[];
  
  // Modal choices
  modalChoiceConfig: ModalChoiceConfig | null;
  selectedModalModes: string[];
  modalChoiceErrors: string[];
  modalChoiceDisabled?: boolean;
  onToggleModalMode: (modeId: string) => void;
  
  // Enter choices
  enterChoiceConfig: EnterChoiceConfig[];
  enterChoices: Record<string, string>;
  enterChoiceErrors: string[];
  enterChoiceTargetOptions: Array<{ value: string; label: string }>;
  onEnterChoiceChange: (choiceType: string, value: string) => void;
  
  // Search choices
  searchEntries: any[];
  searchErrors: string[];
  
  // Ward payments
  autoPayWard: boolean;
  wardTargets: any[];
  wardPayments: Record<string, any>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  hasWardPaymentErrors: boolean;
  onToggleAutoPayWard: (value: boolean) => void;
  onUpdateWardPayment: (objectId: string, costIndex: number, payment: any) => void;
  onUpdateWardPaymentDetail: (objectId: string, costIndex: number, detail: ManaPaymentDetail) => void;
  
  // Replacement conflicts
  replacementConflicts: ReplacementConflictEntry[];
  replacementChoices: Record<string, string>;
  highlightedReplacementKey: string | null;
  onResolveReplacement: (key: string, choice: string) => void;
  onHighlightReplacement: (key: string | null) => void;
  
  // Costs (activation, additional, alternative, optional)
  activationCosts: ActivationCostEntry[];
  activationPayments: any[];
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  hasActivationCostErrors: boolean;
  onUpdateActivationPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateActivationPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  additionalCastCosts: ActivationCostEntry[];
  additionalCastPayments: any[];
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  hasAdditionalCastCostErrors: boolean;
  onUpdateAdditionalCastPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateAdditionalCastPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  alternativeCostOptions: AlternativeCostOption[];
  selectedAlternativeCostTag: string | null;
  alternativeExtraCosts: ActivationCostEntry[];
  alternativeExtraPayments: any[];
  alternativeExtraPaymentDetails: Record<number, ManaPaymentDetail>;
  alternativeExtraCostErrors: string[];
  hasAlternativeExtraCostErrors: boolean;
  onSelectAlternativeCost: (value: string | null) => void;
  onUpdateAlternativeExtraPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateAlternativeExtraPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  optionalCostOptions: OptionalCastCostOption[];
  optionalCostSelections: Record<string, number>;
  optionalCostErrors: string[];
  hasOptionalCostErrors: boolean;
  optionalCostEntries: ActivationCostEntry[];
  optionalCostPayments: any[];
  optionalCostPaymentDetails: Record<number, ManaPaymentDetail>;
  optionalCostPaymentErrors: string[];
  onToggleOptionalCost: (tag: string) => void;
  onUpdateOptionalCostCount: (tag: string, count: number) => void;
  onUpdateOptionalCostPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateOptionalCostPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  // Conspire
  conspireEnabled: boolean;
  conspireOptions: Array<{ value: string; label: string }>;
  conspireSelections: string[];
  conspireError?: string | null;
  onToggleConspire: (value: string) => void;
  
  // Splice
  spliceOptions: Array<{ cardId: string; label: string; costs: any[] }>;
  spliceSelections: string[];
  spliceCosts: ActivationCostEntry[];
  splicePayments: any[];
  splicePaymentDetails: Record<number, ManaPaymentDetail>;
  spliceCostErrors: string[];
  onToggleSpliceCard: (cardId: string) => void;
  onUpdateSplicePayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateSplicePaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  // Card info
  cardMap: EngineCardMap;
  
  // Actions
  onPlayLand: () => void;
  onPrepareCast: () => void;
  onFinalizeCast: () => void;
  onTapForMana: () => void;
  onActivateAbility: () => void;
  onDeclareAttackers: () => void;
  onDeclareBlockers: () => void;
  onAssignCombatDamage: () => void;
  onSelectDefender: (value: string | null) => void;
  onSelectActiveAttacker: (attackerId: string) => void;
  onReorderBlockerUp: (index: number) => void;
  onReorderBlockerDown: (index: number) => void;
  onChangeTargetObjects: (ids: string[]) => void;
  onChangeTargetPlayers: (ids: number[]) => void;
  onChangeCopyTargetSelection: (index: number, selection: { objectIds: string[]; playerIds: number[] }) => void;
}

export function ActionsPanel(props: ActionsPanelProps) {
  const {
    loading,
    selectedHandId,
    selectedCommandId,
    selectedBattlefieldId,
    preparedCast,
    isMainPhase,
    isPriorityActivePlayer,
    hasActivatedAbility,
    isDeclareAttackers,
    isDeclareBlockers,
    isCombatDamage,
    isPriorityDefender,
    selectedAttackers,
    activeAttackerId,
    activeBlockerOrder,
    selectedDefenderId,
    defenderOptions,
    combatState,
    blockerErrors,
    blockerErrorMap,
    hasUnresolvedDamageReplacements,
    unresolvedDamageReplacements,
    cardMap,
    ...rest
  } = props;

  const showCombatActions = isDeclareAttackers || isDeclareBlockers || isCombatDamage;
  const showCastingActions = (selectedHandId || selectedCommandId || selectedBattlefieldId) && !showCombatActions;

  return (
    <Card className="p-4 space-y-6">
      {/* Choices Section - Always visible when needed */}
      <ChoicesSection
        modalChoiceConfig={rest.modalChoiceConfig}
        selectedModalModes={rest.selectedModalModes}
        modalChoiceErrors={rest.modalChoiceErrors}
        modalChoiceDisabled={rest.modalChoiceDisabled}
        onToggleModalMode={rest.onToggleModalMode}
        enterChoiceConfig={rest.enterChoiceConfig}
        enterChoices={rest.enterChoices}
        enterChoiceErrors={rest.enterChoiceErrors}
        enterChoiceTargetOptions={rest.enterChoiceTargetOptions}
        onEnterChoiceChange={rest.onEnterChoiceChange}
        searchEntries={rest.searchEntries}
        searchErrors={rest.searchErrors}
        autoPayWard={rest.autoPayWard}
        wardTargets={rest.wardTargets}
        wardPayments={rest.wardPayments}
        wardPaymentDetails={rest.wardPaymentDetails}
        wardPaymentErrors={rest.wardPaymentErrors}
        hasWardPaymentErrors={rest.hasWardPaymentErrors}
        manaPool={rest.manaPool}
        onToggleAutoPayWard={rest.onToggleAutoPayWard}
        onUpdateWardPayment={rest.onUpdateWardPayment}
        onUpdateWardPaymentDetail={rest.onUpdateWardPaymentDetail}
        replacementConflicts={rest.replacementConflicts}
        replacementChoices={rest.replacementChoices}
        highlightedReplacementKey={rest.highlightedReplacementKey}
        onResolveReplacement={rest.onResolveReplacement}
        onHighlightReplacement={rest.onHighlightReplacement}
        cardMap={cardMap}
      />

      {/* Targeting Section */}
      <TargetingSection
        effectTargetGroups={rest.effectTargetGroups}
        hasEffectTargets={rest.hasEffectTargets}
        filteredTargetableObjects={rest.filteredTargetableObjects}
        filteredTargetPlayers={rest.filteredTargetPlayers}
        selectedTargetObjectIds={rest.selectedTargetObjectIds}
        selectedTargetPlayerIds={rest.selectedTargetPlayerIds}
        objectTargetStatus={rest.objectTargetStatus}
        playerTargetStatus={rest.playerTargetStatus}
        copyTargetsEnabled={rest.copyTargetsEnabled}
        copyTargetsCount={rest.copyTargetsCount}
        copyTargetSelections={rest.copyTargetSelections}
        copyTargetErrors={rest.copyTargetErrors}
        targetSelectionErrors={rest.targetSelectionErrors}
        globalTargetErrors={rest.globalTargetErrors}
        cardMap={cardMap}
        onChangeTargetObjects={rest.onChangeTargetObjects}
        onChangeTargetPlayers={rest.onChangeTargetPlayers}
        onChangeCopyTargetSelection={rest.onChangeCopyTargetSelection}
      />

      {/* Combat Actions */}
      {showCombatActions && (
        <CombatActions
          loading={loading}
          isDeclareAttackers={isDeclareAttackers}
          isDeclareBlockers={isDeclareBlockers}
          isCombatDamage={isCombatDamage}
          isPriorityActivePlayer={isPriorityActivePlayer}
          isPriorityDefender={isPriorityDefender}
          selectedAttackers={selectedAttackers}
          selectedDefenderId={selectedDefenderId}
          defenderOptions={defenderOptions}
          activeAttackerId={activeAttackerId}
          activeBlockerOrder={activeBlockerOrder}
          blockerErrors={blockerErrors}
          blockerErrorMap={blockerErrorMap}
          combatState={combatState}
          cardMap={cardMap}
          hasUnresolvedDamageReplacements={hasUnresolvedDamageReplacements}
          unresolvedDamageReplacements={unresolvedDamageReplacements}
          onSelectDefender={rest.onSelectDefender}
          onSelectActiveAttacker={rest.onSelectActiveAttacker}
          onReorderBlockerUp={rest.onReorderBlockerUp}
          onReorderBlockerDown={rest.onReorderBlockerDown}
          onDeclareAttackers={rest.onDeclareAttackers}
          onDeclareBlockers={rest.onDeclareBlockers}
          onAssignCombatDamage={rest.onAssignCombatDamage}
        />
      )}

      {/* Casting Actions */}
      {showCastingActions && (
        <CastingActions
          loading={loading}
          selectedHandId={selectedHandId}
          selectedCommandId={selectedCommandId}
          selectedBattlefieldId={selectedBattlefieldId}
          preparedCast={preparedCast}
          isMainPhase={isMainPhase}
          isPriorityActivePlayer={isPriorityActivePlayer}
          hasActivatedAbility={hasActivatedAbility}
          isComplexCost={rest.isComplexCost}
          manaPool={rest.manaPool}
          manaPayment={rest.manaPayment}
          manaPaymentDetail={rest.manaPaymentDetail}
          costLabel={rest.costLabel}
          commanderTax={rest.commanderTax}
          showCommanderTax={rest.showCommanderTax}
          autoPayMana={rest.autoPayMana}
          manaPaymentErrors={rest.manaPaymentErrors}
          onToggleAutoPay={rest.onToggleAutoPay}
          onUpdatePaymentDetail={rest.onUpdatePaymentDetail}
          onUpdateManaPayment={rest.onUpdateManaPayment}
          activationCosts={rest.activationCosts}
          activationPayments={rest.activationPayments}
          activationPaymentDetails={rest.activationPaymentDetails}
          activationCostErrors={rest.activationCostErrors}
          hasActivationCostErrors={rest.hasActivationCostErrors}
          onUpdateActivationPayment={rest.onUpdateActivationPayment}
          onUpdateActivationPaymentDetail={rest.onUpdateActivationPaymentDetail}
          additionalCastCosts={rest.additionalCastCosts}
          additionalCastPayments={rest.additionalCastPayments}
          additionalCastPaymentDetails={rest.additionalCastPaymentDetails}
          additionalCastCostErrors={rest.additionalCastCostErrors}
          hasAdditionalCastCostErrors={rest.hasAdditionalCastCostErrors}
          onUpdateAdditionalCastPayment={rest.onUpdateAdditionalCastPayment}
          onUpdateAdditionalCastPaymentDetail={rest.onUpdateAdditionalCastPaymentDetail}
          alternativeCostOptions={rest.alternativeCostOptions}
          selectedAlternativeCostTag={rest.selectedAlternativeCostTag}
          alternativeExtraCosts={rest.alternativeExtraCosts}
          alternativeExtraPayments={rest.alternativeExtraPayments}
          alternativeExtraPaymentDetails={rest.alternativeExtraPaymentDetails}
          alternativeExtraCostErrors={rest.alternativeExtraCostErrors}
          hasAlternativeExtraCostErrors={rest.hasAlternativeExtraCostErrors}
          onSelectAlternativeCost={rest.onSelectAlternativeCost}
          onUpdateAlternativeExtraPayment={rest.onUpdateAlternativeExtraPayment}
          onUpdateAlternativeExtraPaymentDetail={rest.onUpdateAlternativeExtraPaymentDetail}
          optionalCostOptions={rest.optionalCostOptions}
          optionalCostSelections={rest.optionalCostSelections}
          optionalCostErrors={rest.optionalCostErrors}
          hasOptionalCostErrors={rest.hasOptionalCostErrors}
          optionalCostEntries={rest.optionalCostEntries}
          optionalCostPayments={rest.optionalCostPayments}
          optionalCostPaymentDetails={rest.optionalCostPaymentDetails}
          optionalCostPaymentErrors={rest.optionalCostPaymentErrors}
          onToggleOptionalCost={rest.onToggleOptionalCost}
          onUpdateOptionalCostCount={rest.onUpdateOptionalCostCount}
          onUpdateOptionalCostPayment={rest.onUpdateOptionalCostPayment}
          onUpdateOptionalCostPaymentDetail={rest.onUpdateOptionalCostPaymentDetail}
          conspireEnabled={rest.conspireEnabled}
          conspireOptions={rest.conspireOptions}
          conspireSelections={rest.conspireSelections}
          conspireError={rest.conspireError}
          onToggleConspire={rest.onToggleConspire}
          spliceOptions={rest.spliceOptions}
          spliceSelections={rest.spliceSelections}
          spliceCosts={rest.spliceCosts}
          splicePayments={rest.splicePayments}
          splicePaymentDetails={rest.splicePaymentDetails}
          spliceCostErrors={rest.spliceCostErrors}
          onToggleSpliceCard={rest.onToggleSpliceCard}
          onUpdateSplicePayment={rest.onUpdateSplicePayment}
          onUpdateSplicePaymentDetail={rest.onUpdateSplicePaymentDetail}
          cardMap={cardMap}
          onPlayLand={rest.onPlayLand}
          onPrepareCast={rest.onPrepareCast}
          onFinalizeCast={rest.onFinalizeCast}
          onTapForMana={rest.onTapForMana}
          onActivateAbility={rest.onActivateAbility}
        />
      )}
    </Card>
  );
}
