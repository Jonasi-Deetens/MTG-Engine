'use client';

import { StylizedButton } from '@/components/ui/play/StylizedButton';
import { StylizedNativeSelect } from '@/components/ui/play/StylizedNativeSelect';
import { ManaPaymentPanel } from '../ManaPaymentPanel';
import { ActivationCostPanel } from '../ActivationCostPanel';
import { OptionalCostPanel } from '../OptionalCostPanel';
import { ConspirePanel } from '../ConspirePanel';
import { SplicePanel } from '../SplicePanel';
import { EngineCardMap } from '@/lib/engine';
import { ManaPaymentDetail } from '@/lib/manaPayment';
import { ActivationCostEntry } from '../../hooks/useActivationCosts';
import { AlternativeCostOption, OptionalCastCostOption } from '@/lib/graphCosts';

/**
 * CastingActions - Spell casting UI
 * 
 * Responsible for:
 * - Cast spell button
 * - Play land button
 * - Tap for mana button
 * - Mana payment panel
 * - Additional/alternative/optional cost panels
 * - Conspire and splice panels
 */

interface CastingActionsProps {
  loading: boolean;
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  preparedCast: { objectId: string; cost: any } | null;
  isMainPhase: boolean;
  isPriorityActivePlayer: boolean;
  hasActivatedAbility: boolean;
  
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
  
  // Activation costs
  activationCosts: ActivationCostEntry[];
  activationPayments: any[];
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  hasActivationCostErrors: boolean;
  onUpdateActivationPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateActivationPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  // Additional costs
  additionalCastCosts: ActivationCostEntry[];
  additionalCastPayments: any[];
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  hasAdditionalCastCostErrors: boolean;
  onUpdateAdditionalCastPayment: (index: number, updater: (prev: any) => any) => void;
  onUpdateAdditionalCastPaymentDetail: (index: number, updater: (prev: ManaPaymentDetail) => ManaPaymentDetail) => void;
  
  // Alternative costs
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
  
  // Optional costs
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
}

export function CastingActions({
  loading,
  selectedHandId,
  selectedCommandId,
  selectedBattlefieldId,
  preparedCast,
  isMainPhase,
  isPriorityActivePlayer,
  hasActivatedAbility,
  isComplexCost,
  manaPool,
  manaPayment,
  manaPaymentDetail,
  costLabel,
  commanderTax,
  showCommanderTax,
  autoPayMana,
  manaPaymentErrors,
  onToggleAutoPay,
  onUpdatePaymentDetail,
  onUpdateManaPayment,
  activationCosts,
  activationPayments,
  activationPaymentDetails,
  activationCostErrors,
  hasActivationCostErrors,
  onUpdateActivationPayment,
  onUpdateActivationPaymentDetail,
  additionalCastCosts,
  additionalCastPayments,
  additionalCastPaymentDetails,
  additionalCastCostErrors,
  hasAdditionalCastCostErrors,
  onUpdateAdditionalCastPayment,
  onUpdateAdditionalCastPaymentDetail,
  alternativeCostOptions,
  selectedAlternativeCostTag,
  alternativeExtraCosts,
  alternativeExtraPayments,
  alternativeExtraPaymentDetails,
  alternativeExtraCostErrors,
  hasAlternativeExtraCostErrors,
  onSelectAlternativeCost,
  onUpdateAlternativeExtraPayment,
  onUpdateAlternativeExtraPaymentDetail,
  optionalCostOptions,
  optionalCostSelections,
  optionalCostErrors,
  hasOptionalCostErrors,
  optionalCostEntries,
  optionalCostPayments,
  optionalCostPaymentDetails,
  optionalCostPaymentErrors,
  onToggleOptionalCost,
  onUpdateOptionalCostCount,
  onUpdateOptionalCostPayment,
  onUpdateOptionalCostPaymentDetail,
  conspireEnabled,
  conspireOptions,
  conspireSelections,
  conspireError,
  onToggleConspire,
  spliceOptions,
  spliceSelections,
  spliceCosts,
  splicePayments,
  splicePaymentDetails,
  spliceCostErrors,
  onToggleSpliceCard,
  onUpdateSplicePayment,
  onUpdateSplicePaymentDetail,
  cardMap,
  onPlayLand,
  onPrepareCast,
  onFinalizeCast,
  onTapForMana,
  onActivateAbility,
}: CastingActionsProps) {
  const selectedCastId = selectedCommandId ?? selectedHandId;
  const showLandButton = selectedHandId && isMainPhase && isPriorityActivePlayer;
  const showCastButton = selectedCastId && isMainPhase && isPriorityActivePlayer;
  const showTapButton = selectedBattlefieldId && isPriorityActivePlayer;
  const showActivateButton = selectedBattlefieldId && hasActivatedAbility && isPriorityActivePlayer;

  const isPrepared = preparedCast && preparedCast.objectId === selectedCastId;
  const canFinalize = isPrepared && manaPaymentErrors.length === 0;

  return (
    <div className="space-y-4">
      {/* Play Land Button */}
      {showLandButton && (
        <StylizedButton onClick={onPlayLand} disabled={loading} variant="secondary" className="w-full">
          Play Land
        </StylizedButton>
      )}

      {/* Cast Spell Section */}
      {showCastButton && (
        <div className="space-y-3">
          {/* Alternative Cost Selection */}
          {alternativeCostOptions.length > 0 && !isPrepared && (
            <div className="space-y-2">
              <label className="text-sm font-medium">Cost Option</label>
              <StylizedNativeSelect
                value={selectedAlternativeCostTag ?? ''}
                onChange={(e) => onSelectAlternativeCost(e.target.value || null)}
              >
                <option value="">Normal Cost</option>
                {alternativeCostOptions.map((option) => (
                  <option key={option.tag} value={option.tag}>
                    {option.label}
                  </option>
                ))}
              </StylizedNativeSelect>
            </div>
          )}

          {/* Optional Costs */}
          {optionalCostOptions.length > 0 && !isPrepared && (
            <OptionalCostPanel
              options={optionalCostOptions}
              selections={optionalCostSelections}
              onToggle={onToggleOptionalCost}
              onUpdateCount={onUpdateOptionalCostCount}
            />
          )}

          {/* Conspire */}
          {conspireEnabled && !isPrepared && (
            <ConspirePanel
              options={conspireOptions}
              selections={conspireSelections}
              onToggle={onToggleConspire}
              error={conspireError}
            />
          )}

          {/* Splice */}
          {spliceOptions.length > 0 && !isPrepared && (
            <SplicePanel
              options={spliceOptions}
              selections={spliceSelections}
              onToggle={onToggleSpliceCard}
            />
          )}

          {/* Prepare Cast Button */}
          {!isPrepared && (
            <StylizedButton onClick={onPrepareCast} disabled={loading} className="w-full">
              Prepare Cast
            </StylizedButton>
          )}

          {/* Mana Payment */}
          {isPrepared && (
            <>
              <ManaPaymentPanel
                cost={preparedCast.cost}
                manaPool={manaPool}
                payment={manaPayment}
                paymentDetail={manaPaymentDetail}
                isComplexCost={isComplexCost}
                autoPay={autoPayMana}
                costLabel={costLabel}
                commanderTax={commanderTax}
                showCommanderTax={showCommanderTax}
                errors={manaPaymentErrors}
                onToggleAutoPay={onToggleAutoPay}
                onUpdatePayment={onUpdateManaPayment}
                onUpdatePaymentDetail={onUpdatePaymentDetail}
              />

              {/* Additional Costs */}
              {additionalCastCosts.length > 0 && (
                <ActivationCostPanel
                  title="Additional Costs"
                  costs={additionalCastCosts}
                  payments={additionalCastPayments}
                  paymentDetails={additionalCastPaymentDetails}
                  manaPool={manaPool}
                  cardMap={cardMap}
                  errors={additionalCastCostErrors}
                  onUpdatePayment={onUpdateAdditionalCastPayment}
                  onUpdatePaymentDetail={onUpdateAdditionalCastPaymentDetail}
                />
              )}

              {/* Alternative Extra Costs */}
              {alternativeExtraCosts.length > 0 && (
                <ActivationCostPanel
                  title="Alternative Cost Requirements"
                  costs={alternativeExtraCosts}
                  payments={alternativeExtraPayments}
                  paymentDetails={alternativeExtraPaymentDetails}
                  manaPool={manaPool}
                  cardMap={cardMap}
                  errors={alternativeExtraCostErrors}
                  onUpdatePayment={onUpdateAlternativeExtraPayment}
                  onUpdatePaymentDetail={onUpdateAlternativeExtraPaymentDetail}
                />
              )}

              {/* Optional Cost Payments */}
              {optionalCostEntries.length > 0 && (
                <ActivationCostPanel
                  title="Optional Cost Payments"
                  costs={optionalCostEntries}
                  payments={optionalCostPayments}
                  paymentDetails={optionalCostPaymentDetails}
                  manaPool={manaPool}
                  cardMap={cardMap}
                  errors={optionalCostPaymentErrors}
                  onUpdatePayment={onUpdateOptionalCostPayment}
                  onUpdatePaymentDetail={onUpdateOptionalCostPaymentDetail}
                />
              )}

              {/* Splice Payments */}
              {spliceCosts.length > 0 && (
                <ActivationCostPanel
                  title="Splice Costs"
                  costs={spliceCosts}
                  payments={splicePayments}
                  paymentDetails={splicePaymentDetails}
                  manaPool={manaPool}
                  cardMap={cardMap}
                  errors={spliceCostErrors}
                  onUpdatePayment={onUpdateSplicePayment}
                  onUpdatePaymentDetail={onUpdateSplicePaymentDetail}
                />
              )}

              <StylizedButton
                onClick={onFinalizeCast}
                disabled={loading || !canFinalize}
                className="w-full"
              >
                Cast Spell
              </StylizedButton>
            </>
          )}
        </div>
      )}

      {/* Tap for Mana */}
      {showTapButton && (
        <StylizedButton onClick={onTapForMana} disabled={loading} variant="secondary" className="w-full">
          Tap for Mana
        </StylizedButton>
      )}

      {/* Activate Ability */}
      {showActivateButton && (
        <div className="space-y-3">
          {activationCosts.length > 0 && (
            <ActivationCostPanel
              title="Activation Costs"
              costs={activationCosts}
              payments={activationPayments}
              paymentDetails={activationPaymentDetails}
              manaPool={manaPool}
              cardMap={cardMap}
              errors={activationCostErrors}
              onUpdatePayment={onUpdateActivationPayment}
              onUpdatePaymentDetail={onUpdateActivationPaymentDetail}
            />
          )}
          <StylizedButton
            onClick={onActivateAbility}
            disabled={loading || hasActivationCostErrors}
            className="w-full"
          >
            Activate Ability
          </StylizedButton>
        </div>
      )}
    </div>
  );
}
