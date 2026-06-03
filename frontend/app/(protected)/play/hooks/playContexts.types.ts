import type { Dispatch, SetStateAction } from 'react';
import type { ManaPaymentDetail } from '@/lib/manaPayment';
import type { GameContextValue } from '@/features/game/contexts/GameContext';

// ============================================================================
// Setup Context
// ============================================================================

export interface SetupContextValue {
  deckList: any[];
  selectedDeckIds: (number | null)[];
  setupLoading: boolean;
  canStart: boolean;
  handleSelectDeck: (index: number, deckId: string) => void;
  startGame: () => void;
}

// ============================================================================
// Selection Context
// ============================================================================

export interface SelectionContextValue {
  selectedHandId: string | null;
  selectedCommandId: string | null;
  selectedBattlefieldId: string | null;
  selectedStackIndex: number | null;
  setSelectedHandId: Dispatch<SetStateAction<string | null>>;
  setSelectedCommandId: Dispatch<SetStateAction<string | null>>;
  setSelectedBattlefieldId: Dispatch<SetStateAction<string | null>>;
  setSelectedStackIndex: Dispatch<SetStateAction<number | null>>;
  loadEffectGraphForObject: (objectId: string) => void;
  effectGraphs: Record<string, any>;
  selectedGraph: any;
}

// ============================================================================
// Turn Context
// ============================================================================

export interface TurnContextValue {
  currentPriority: number | null;
  activePlayerIndex: number;
  isMainPhase: boolean;
  isDeclareAttackers: boolean;
  isDeclareBlockers: boolean;
  isCombatDamage: boolean;
  isPriorityActivePlayer: boolean;
  isPriorityDefender: boolean;
  objectMap: Map<string, any>;
}

// ============================================================================
// Combat Context
// ============================================================================

export interface PlayCombatContextValue {
  selectedAttackers: Set<string>;
  selectedBlockers: Record<string, Set<string>>;
  selectedBlockerOrder: Record<string, string[]>;
  activeAttackerId: string | null;
  selectedDefenderId: string | null;
  combatDamageAssignments: Record<string, Record<string, number>>;
  combatState: any;
  defenderOptions: Array<{ value: string; label: string }>;
  defendingPlayerId: number | null;
  defendingObjectId: string | null;
  hasFirstStrikeCombat: boolean;
  combatDamagePass: 'first_strike' | 'regular' | null;
  hasManualCombatChoices: boolean;
  blockerErrors: string[];
  blockerErrorMap: Record<string, string[]>;
  activeBlockerOrder: string[];
  blockersPayload: Record<string, string[]>;
  setActiveAttackerId: Dispatch<SetStateAction<string | null>>;
  setSelectedDefenderId: Dispatch<SetStateAction<string | null>>;
  toggleAttacker: (id: string) => void;
  toggleBlocker: (id: string) => void;
  setSelectedBlockerOrder: Dispatch<SetStateAction<Record<string, string[]>>>;
  setCombatDamageAssignments: Dispatch<SetStateAction<Record<string, Record<string, number>>>>;
}

// ============================================================================
// Choices Context
// ============================================================================

export interface PlayChoicesContextValue {
  modalChoiceConfig: any;
  selectedModalModes: string[];
  modalChoiceErrors: string[];
  modalChoicesForCast: string[];
  entwineSelected: boolean;
  handleToggleModalMode: (modeId: string) => void;
  setSelectedModalModes: Dispatch<SetStateAction<string[]>>;
  enterChoiceConfig: any[];
  enterChoices: Record<string, string>;
  enterChoiceErrors: string[];
  enterChoiceTargetOptions: Array<{ value: string; label: string }>;
  setEnterChoices: Dispatch<SetStateAction<Record<string, string>>>;
  onEnterChoiceChange: (type: string, value: string) => void;
  replacementChoices: Record<string, string>;
  replacementConflicts: any[];
  hasUnresolvedDamageReplacements: boolean;
  unresolvedDamageReplacements: any[];
  highlightedReplacementKey: string | null;
  setReplacementChoices: Dispatch<SetStateAction<Record<string, string>>>;
  setHighlightedReplacementKey: Dispatch<SetStateAction<string | null>>;
  wardTargets: any[];
  wardPayments: Record<string, any>;
  wardPaymentDetails: Record<string, ManaPaymentDetail>;
  wardPaymentErrors: Record<string, string[]>;
  wardPaymentsPayload: Record<string, any>;
  hasWardPaymentErrors: boolean;
  autoPayWard: boolean;
  setWardPayments: Dispatch<SetStateAction<Record<string, any>>>;
  setWardPaymentDetails: Dispatch<SetStateAction<Record<string, ManaPaymentDetail>>>;
  setAutoPayWard: Dispatch<SetStateAction<boolean>>;
}

// ============================================================================
// Targeting Context
// ============================================================================

export interface PlayTargetingContextValue {
  targetHints: any;
  selectedTargetObjectIds: string[];
  selectedTargetPlayerIds: number[];
  objectTargetStatus: Record<string, boolean | null>;
  playerTargetStatus: Record<number, boolean | null>;
  stackTargetChecks: any[];
  stackSpellObjects: any[];
  filteredTargetableObjects: any[];
  filteredTargetPlayers: any[];
  shouldUseStackTargets: boolean;
  requiredTargetsGlobal: string[];
  distinctTargetsGlobal: string[];
  minTargetsGlobal: Record<string, number> | null;
  effectTargetGroups: any[];
  targetsByEffect: Record<string, Record<string, any>>;
  requiredTargetsByEffect: Record<string, string[]>;
  distinctTargetsByEffect: Record<string, string[]>;
  minTargetsByEffect: Record<string, Record<string, number>>;
  globalTargetErrors: string[];
  effectTargetObjectIds: string[];
  effectTargetPlayerIds: number[];
  hasEffectTargets: boolean;
  mergedTargetsByEffect: Record<string, Record<string, any>>;
  searchEntries: any[];
  searchTargetsByEffect: Record<string, Record<string, any>>;
  searchErrors: string[];
  hasPendingSearchChoices: boolean;
  copySpellConfig: { enabled: boolean; amount: number };
  copyTargetSelections: Array<{ objectIds: string[]; playerIds: number[] }>;
  copyTargetErrorsGlobal: string[];
  copyTargetsByEffectCount: number;
  copyEffectTargetGroups: any[];
  copyTargetsByEffectList: any[];
  copyRequiredTargetsByEffectList: any[];
  copyDistinctTargetsByEffectList: any[];
  copyMinTargetsByEffectList: any[];
  copyTargetErrors: string[];
  resolvedTargetObjectIds: string[];
  resolvedTargetPlayerIds: number[];
  targetSelectionErrors: string[];
  setSelectedTargetObjectIds: Dispatch<SetStateAction<string[]>>;
  setSelectedTargetPlayerIds: Dispatch<SetStateAction<number[]>>;
  setCopyTargetSelections: Dispatch<SetStateAction<Array<{ objectIds: string[]; playerIds: number[] }>>>;
  clearEffectTargets: () => void;
}

// ============================================================================
// Casting Context
// ============================================================================

export interface CastingContextValue {
  preparedCast: { objectId: string; cost: any } | null;
  manaPool: Record<string, number>;
  manaPayment: Record<string, number>;
  manaPaymentDetail: ManaPaymentDetail;
  manaPaymentStatus: { errors: string[] };
  costLabel: string;
  autoPayMana: boolean;
  isComplexCost: boolean;
  handlePrepareCast: () => void;
  handleFinalizeCast: () => void;
  setManaPayment: Dispatch<SetStateAction<Record<string, number>>>;
  setManaPaymentDetail: Dispatch<SetStateAction<ManaPaymentDetail>>;
  setAutoPayMana: Dispatch<SetStateAction<boolean>>;
  buildCastContext: (objectId?: string, options?: any) => any;
  // Activation costs
  activationCosts: any[];
  activationPayments: any[];
  activationPaymentDetails: Record<number, ManaPaymentDetail>;
  activationCostErrors: string[];
  hasActivationCostErrors: boolean;
  activationCostPaymentsPayload: any;
  setActivationPayments: Dispatch<SetStateAction<any[]>>;
  setActivationPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Additional costs
  additionalCastCosts: any[];
  additionalCastPayments: any[];
  additionalCastPaymentDetails: Record<number, ManaPaymentDetail>;
  additionalCastCostErrors: string[];
  hasAdditionalCastCostErrors: boolean;
  setAdditionalCastPayments: Dispatch<SetStateAction<any[]>>;
  setAdditionalCastPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Alternative costs
  alternativeCostOptions: any[];
  selectedAlternativeCostTag: string | null;
  alternativeExtraCostEntries: any[];
  alternativeExtraPayments: any[];
  alternativeExtraPaymentDetails: Record<number, ManaPaymentDetail>;
  alternativeExtraCostErrors: string[];
  hasAlternativeExtraCostErrors: boolean;
  setSelectedAlternativeCostTag: Dispatch<SetStateAction<string | null>>;
  setAlternativeExtraPayments: Dispatch<SetStateAction<any[]>>;
  setAlternativeExtraPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Optional costs
  optionalCostOptions: any[];
  optionalCostSelections: Record<string, number>;
  optionalCostEntries: any[];
  optionalCostPayments: any[];
  optionalCostPaymentDetails: Record<number, ManaPaymentDetail>;
  optionalCostErrors: string[];
  optionalCostPaymentErrors: string[];
  hasOptionalCostErrors: boolean;
  handleToggleOptionalCost: (tag: string) => void;
  handleUpdateOptionalCostCount: (tag: string, count: number) => void;
  setOptionalCostPayments: Dispatch<SetStateAction<any[]>>;
  setOptionalCostPaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
  // Conspire
  conspireSelected: boolean;
  conspireOptions: any[];
  conspireTaps: string[];
  conspireError: string | null;
  handleToggleConspireTap: (value: string) => void;
  // Splice
  spliceOptions: any[];
  spliceSelections: string[];
  spliceCosts: any[];
  splicePayments: any[];
  splicePaymentDetails: Record<number, ManaPaymentDetail>;
  spliceCostErrors: string[];
  handleToggleSpliceCard: (cardId: string) => void;
  setSplicePayments: Dispatch<SetStateAction<any[]>>;
  setSplicePaymentDetails: Dispatch<SetStateAction<Record<number, ManaPaymentDetail>>>;
}

// ============================================================================
// Re-export GameContextValue for convenience
// ============================================================================

export type { GameContextValue };
