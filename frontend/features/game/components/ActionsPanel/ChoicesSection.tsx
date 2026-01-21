'use client';

import { EnterChoicesPanel } from '../EnterChoicesPanel';
import { SearchChoicePanel } from '../SearchChoicePanel';
import { ModalChoicePanel } from '../ModalChoicePanel';
import { WardPaymentPanel } from '../WardPaymentPanel';
import { ReplacementChoicePanel } from '../ReplacementChoicePanel';
import { EnterChoiceConfig } from '@/lib/enterChoices';
import { ModalChoiceConfig } from '@/lib/modalChoices';
import { ManaPaymentDetail } from '@/lib/manaPayment';
import { ReplacementConflictEntry } from '../../hooks/useReplacementConflicts';
import { EngineCardMap } from '@/lib/engine';

/**
 * ChoicesSection - Modal, enter, search, and replacement choices UI
 * 
 * Responsible for:
 * - Modal choice selection (modes)
 * - Enter choice selection (ETB choices)
 * - Search choice selection (library/graveyard search)
 * - Ward payment UI
 * - Replacement conflict resolution
 */

interface ChoicesSectionProps {
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
  searchEntries: Array<{
    id: string;
    nodeId: string;
    label: string;
    playerId: number;
    zone: string;
    candidates: Array<{ id: string; label: string }>;
    selectedIds: string[];
    maxSelections?: number | null;
    onChange: (ids: string[]) => void;
  }>;
  searchErrors: string[];
  
  // Ward payments
  autoPayWard: boolean;
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
  wardPayments: Record<string, any>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  hasWardPaymentErrors: boolean;
  manaPool: Record<string, number>;
  onToggleAutoPayWard: (value: boolean) => void;
  onUpdateWardPayment: (objectId: string, costIndex: number, payment: any) => void;
  onUpdateWardPaymentDetail: (objectId: string, costIndex: number, detail: ManaPaymentDetail) => void;
  
  // Replacement conflicts
  replacementConflicts: ReplacementConflictEntry[];
  replacementChoices: Record<string, string>;
  highlightedReplacementKey: string | null;
  onResolveReplacement: (key: string, choice: string) => void;
  onHighlightReplacement: (key: string | null) => void;
  
  // Card info
  cardMap: EngineCardMap;
}

export function ChoicesSection({
  modalChoiceConfig,
  selectedModalModes,
  modalChoiceErrors,
  modalChoiceDisabled,
  onToggleModalMode,
  enterChoiceConfig,
  enterChoices,
  enterChoiceErrors,
  enterChoiceTargetOptions,
  onEnterChoiceChange,
  searchEntries,
  searchErrors,
  autoPayWard,
  wardTargets,
  wardPayments,
  wardPaymentDetails,
  wardPaymentErrors,
  hasWardPaymentErrors,
  manaPool,
  onToggleAutoPayWard,
  onUpdateWardPayment,
  onUpdateWardPaymentDetail,
  replacementConflicts,
  replacementChoices,
  highlightedReplacementKey,
  onResolveReplacement,
  onHighlightReplacement,
  cardMap,
}: ChoicesSectionProps) {
  const hasModalChoice = modalChoiceConfig && modalChoiceConfig.modes.length > 0;
  const hasEnterChoices = enterChoiceConfig.length > 0;
  const hasSearchChoices = searchEntries.length > 0;
  const hasWardTargets = wardTargets.length > 0;
  const hasReplacements = replacementConflicts.length > 0;

  if (!hasModalChoice && !hasEnterChoices && !hasSearchChoices && !hasWardTargets && !hasReplacements) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Modal choices */}
      {hasModalChoice && (
        <ModalChoicePanel
          config={modalChoiceConfig}
          selectedModes={selectedModalModes}
          errors={modalChoiceErrors}
          disabled={modalChoiceDisabled}
          onToggle={onToggleModalMode}
        />
      )}

      {/* Enter choices */}
      {hasEnterChoices && (
        <EnterChoicesPanel
          config={enterChoiceConfig}
          choices={enterChoices}
          errors={enterChoiceErrors}
          targetOptions={enterChoiceTargetOptions}
          onChange={onEnterChoiceChange}
        />
      )}

      {/* Search choices */}
      {hasSearchChoices && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold">Search Choices</h3>
          {searchEntries.map((entry) => (
            <SearchChoicePanel
              key={entry.id}
              label={entry.label}
              candidates={entry.candidates}
              selectedIds={entry.selectedIds}
              maxSelections={entry.maxSelections ?? undefined}
              onChange={entry.onChange}
            />
          ))}
          {searchErrors.length > 0 && (
            <ul className="text-sm text-destructive">
              {searchErrors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Ward payments */}
      {hasWardTargets && (
        <WardPaymentPanel
          targets={wardTargets}
          payments={wardPayments}
          paymentDetails={wardPaymentDetails}
          errors={wardPaymentErrors}
          manaPool={manaPool}
          autoPay={autoPayWard}
          onToggleAutoPay={onToggleAutoPayWard}
          onUpdatePayment={onUpdateWardPayment}
          onUpdatePaymentDetail={onUpdateWardPaymentDetail}
        />
      )}

      {/* Replacement conflicts */}
      {hasReplacements && (
        <ReplacementChoicePanel
          conflicts={replacementConflicts}
          choices={replacementChoices}
          highlightedKey={highlightedReplacementKey}
          cardMap={cardMap}
          onResolve={onResolveReplacement}
          onHighlight={onHighlightReplacement}
        />
      )}
    </div>
  );
}
