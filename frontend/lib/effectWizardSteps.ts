import type { SourceKind, UnifiedEffect } from '@/lib/unifiedEffect';

export type WizardIntent =
  | 'triggered'
  | 'activated'
  | 'always_on'
  | 'spell'
  | 'replacement'
  | 'prevention'
  | 'keyword';

export type WizardStepKey =
  | 'intent'
  | 'config'
  | 'conditions'
  | 'costs'
  | 'effect'
  | 'review';

export const WIZARD_STEP_LABELS: Record<WizardStepKey, string> = {
  intent: 'Intent',
  config: 'Setup',
  conditions: 'Conditions',
  costs: 'Extra costs',
  effect: 'Effect',
  review: 'Review',
};

/** Spell effects and spell-source graphs may define kicker / additional costs. */
export function shouldShowCostsStep(
  intent: WizardIntent | null,
  sourceKind?: SourceKind
): boolean {
  if (intent === 'spell') return true;
  if (sourceKind === 'spell') return true;
  return false;
}

/** Config step is only needed when there is non-trivial setup beyond the effect body. */
export function shouldShowConfigStep(draft: UnifiedEffect | null, intent: WizardIntent | null): boolean {
  if (!draft) return false;
  if (intent === 'spell' && draft.effect.kind === 'one_shot') return false;
  if (draft.initiation === 'triggered') return true;
  if (draft.initiation === 'activated') return true;
  if (draft.effect.kind === 'continuous') return true;
  if (draft.effect.kind === 'replacement' || draft.effect.kind === 'prevention') return true;
  return false;
}

export function getWizardStepKeys(params: {
  draft: UnifiedEffect | null;
  intent: WizardIntent | null;
  sourceKind?: SourceKind;
}): WizardStepKey[] {
  const { draft, intent, sourceKind } = params;
  let keys: WizardStepKey[] = ['intent', 'config', 'conditions', 'costs', 'effect', 'review'];

  if (!shouldShowConfigStep(draft, intent)) {
    keys = keys.filter((key) => key !== 'config');
  }
  if (!shouldShowCostsStep(intent, sourceKind)) {
    keys = keys.filter((key) => key !== 'costs');
  }
  if (draft && draft.effect.kind !== 'one_shot') {
    keys = keys.filter((key) => key !== 'effect');
  }
  return keys;
}
