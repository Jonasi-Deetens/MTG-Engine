'use client';

import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';

import type { EffectStep, SourceKind, UnifiedEffect } from '@/lib/unifiedEffect';
import { Button } from '@/components/ui/Button';
import { formatEffect } from '@/lib/effectTypes';
import {
  getWizardStepKeys,
  WIZARD_STEP_LABELS,
  type WizardIntent,
  type WizardStepKey,
} from '@/lib/effectWizardSteps';
import { IntentStep } from './IntentStep';
import { TriggerConfig } from './TriggerConfig';
import { ActivatedConfig } from './ActivatedConfig';
import { ContinuousConfig } from './ContinuousConfig';
import { ReplacementConfig } from './ReplacementConfig';
import { ConditionsStep } from './ConditionsStep';
import { EffectCostStep } from './EffectCostStep';
import { EffectBodyStep } from './EffectBodyStep';
import { ReviewStep } from './ReviewStep';

type IntentType = WizardIntent;

interface EffectWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (effect: UnifiedEffect) => void;
  editingEffect?: UnifiedEffect | null;
  editingStepId?: string | null;
  steps?: EffectStep[];
  sourceKind?: SourceKind;
  onSourceKindChange?: (sourceKind: SourceKind) => void;
}

const createId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
};

const createDefaultEffect = (intent: IntentType): UnifiedEffect => {
  if (intent === 'triggered') {
    return {
      id: createId(),
      initiation: 'triggered',
      resolution: 'stack',
      persistence: 'instant',
      tags: [],
      trigger: { event: 'enters_battlefield', scope: 'self' },
      conditions: [],
      effect: {
        kind: 'one_shot',
        action: { type: 'damage', amount: 1, target: 'any' },
      },
    };
  }
  if (intent === 'activated') {
    return {
      id: createId(),
      initiation: 'activated',
      resolution: 'stack',
      persistence: 'instant',
      tags: [],
      cost: { items: [{ type: 'tap_self' }] },
      conditions: [],
      effect: {
        kind: 'one_shot',
        action: { type: 'draw', amount: 1 },
      },
    };
  }
  if (intent === 'always_on') {
    return {
      id: createId(),
      initiation: 'static',
      resolution: 'immediate',
      persistence: 'continuous',
      tags: [],
      conditions: [],
      effect: {
        kind: 'continuous',
        layer: 6,
        modifier: { type: 'add_keyword', keyword: 'flying' },
        appliesTo: { type: 'self' },
        duration: { type: 'while_in_zone', zone: 'battlefield' },
      },
    };
  }
  if (intent === 'spell') {
    return {
      id: createId(),
      initiation: 'static',
      resolution: 'stack',
      persistence: 'instant',
      tags: [],
      conditions: [],
      effect: {
        kind: 'one_shot',
        action: { type: 'damage', amount: 3, target: 'any' },
      },
    };
  }
  if (intent === 'replacement') {
    return {
      id: createId(),
      initiation: 'static',
      resolution: 'immediate',
      persistence: 'instant',
      tags: ['replacement'],
      conditions: [],
      effect: {
        kind: 'replacement',
        replaces: { event: 'replace_destroy' },
        with: { replacementZone: 'exile' },
      },
    };
  }
  if (intent === 'prevention') {
    return {
      id: createId(),
      initiation: 'static',
      resolution: 'immediate',
      persistence: 'instant',
      tags: ['prevention'],
      conditions: [],
      effect: {
        kind: 'prevention',
        prevents: { event: 'damage' },
        amount: 1,
      },
    };
  }
  return {
    id: createId(),
    initiation: 'static',
    resolution: 'immediate',
    persistence: 'continuous',
    tags: ['keyword'],
    conditions: [],
    effect: {
      kind: 'continuous',
      layer: 6,
      modifier: { type: 'add_keyword', keyword: 'flying' },
      appliesTo: { type: 'self' },
      duration: { type: 'while_in_zone', zone: 'battlefield' },
    },
  };
};

const describeStep = (step: EffectStep): string => {
  const body = step.effect.effect;
  if (body.kind === 'one_shot') {
    return formatEffect(body.action as any);
  }
  if (body.kind === 'continuous') {
    const modifier = body.modifier as any;
    if (modifier?.type === 'add_keyword' && modifier.keyword) {
      return `Grant ${modifier.keyword}`;
    }
    return `Continuous (${modifier?.type || 'modifier'})`;
  }
  if (body.kind === 'replacement') {
    return 'Replacement effect';
  }
  if (body.kind === 'prevention') {
    return 'Prevention effect';
  }
  return 'Effect';
};

export function EffectWizard({
  isOpen,
  onClose,
  onSave,
  editingEffect,
  editingStepId,
  steps = [],
  sourceKind,
  onSourceKindChange,
}: EffectWizardProps) {
  const [intent, setIntent] = useState<IntentType | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [draft, setDraft] = useState<UnifiedEffect | null>(null);

  const inferIntent = (effect: UnifiedEffect): IntentType => {
    if (effect.effect.kind === 'replacement') {
      return 'replacement';
    }
    if (effect.effect.kind === 'prevention') {
      return 'prevention';
    }
    if (effect.effect.kind === 'continuous') {
      return effect.tags.includes('keyword') ? 'keyword' : 'always_on';
    }
    if (effect.initiation === 'activated') {
      return 'activated';
    }
    if (effect.initiation === 'triggered') {
      return 'triggered';
    }
    return 'spell';
  };

  useEffect(() => {
    if (editingEffect) {
      setDraft(editingEffect);
      setIntent(inferIntent(editingEffect));
      setStepIndex(1);
    } else {
      setDraft(null);
      setIntent(null);
      setStepIndex(0);
    }
  }, [editingEffect, isOpen]);

  const stepKeys = useMemo(
    () =>
      getWizardStepKeys({
        draft,
        intent,
        sourceKind,
      }),
    [draft, intent, sourceKind]
  );

  useEffect(() => {
    setStepIndex((prev) => Math.min(prev, Math.max(stepKeys.length - 1, 0)));
  }, [stepKeys.length]);
  const previousSteps = useMemo(() => {
    if (!steps.length) return [];
    const currentIndex =
      editingStepId ? steps.findIndex((step) => step.id === editingStepId) : steps.length;
    const sliceIndex = currentIndex >= 0 ? currentIndex : steps.length;
    return steps.slice(0, sliceIndex).map((step, index) => ({
      id: step.id,
      index,
      label: describeStep(step),
    }));
  }, [steps, editingStepId]);
  const intentOptions: Array<{ id: IntentType; label: string; description: string }> = useMemo(
    () => [
      { id: 'triggered', label: 'Triggered', description: 'When/Whenever/At...' },
      { id: 'activated', label: 'Activated', description: 'Pay a cost to...' },
      { id: 'always_on', label: 'Always On', description: 'Static/continuous modifier' },
      { id: 'spell', label: 'Spell Effect', description: 'Resolves when a spell resolves' },
      { id: 'replacement', label: 'Replacement', description: 'Instead of...' },
      { id: 'prevention', label: 'Prevention', description: 'Prevent damage or events' },
      { id: 'keyword', label: 'Keyword', description: 'Add keyword ability' },
    ],
    []
  );

  const currentKey = stepKeys[stepIndex] as WizardStepKey | undefined;
  const handleIntentSelect = (nextIntent: IntentType) => {
    setIntent(nextIntent);
    setDraft(createDefaultEffect(nextIntent));
    if (onSourceKindChange) {
      const isChainedStep = steps.length > 0 && sourceKind === 'permanent';
      if (!(isChainedStep && nextIntent === 'spell')) {
        onSourceKindChange(nextIntent === 'spell' ? 'spell' : 'permanent');
      }
    }
    setStepIndex(1);
  };

  const handleNext = () => {
    setStepIndex((prev) => Math.min(prev + 1, stepKeys.length - 1));
  };

  const handleBack = () => {
    setStepIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleSave = () => {
    if (!draft) {
      return;
    }
    onSave(draft);
    onClose();
  };

  if (!isOpen || typeof document === 'undefined') {
    return null;
  }

  return createPortal(
    <div
      className="fixed inset-0 z-[9999] flex items-start sm:items-center justify-center bg-[color:var(--theme-overlay-strong)]/70 backdrop-blur-sm p-4 sm:p-8 overflow-y-auto"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Effect wizard"
    >
      <div
        className="ui-card relative w-full max-w-2xl max-h-[calc(100vh-2rem)] sm:max-h-[90vh] overflow-y-auto"
        data-variant="default"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="w-full p-4 sm:p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[color:var(--theme-border-default)] pb-2 lg:pb-3">
            <div className="text-xs font-mono tracking-[0.3em] text-[color:var(--theme-text-secondary)]">
              EFFECT_WIZARD
            </div>
            <div className="flex w-full justify-end sm:w-auto">
              <Button
                type="button"
                variant="frame"
                size="xs"
                onClick={onClose}
                aria-label="Close effect wizard"
                className="w-8 p-0"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </Button>
            </div>
          </div>
          <h3
            className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)] nier-glitch"
            data-text={editingEffect ? 'Edit Effect' : 'Add Effect'}
          >
            {editingEffect ? 'Edit Effect' : 'Add Effect'}
          </h3>
          {currentKey === 'intent' && (
            <IntentStep onSelect={handleIntentSelect} intents={intentOptions} />
          )}
          {currentKey === 'config' && draft && (
            <>
              {draft.initiation === 'triggered' && (
                <TriggerConfig effect={draft} onChange={setDraft} />
              )}
              {draft.initiation === 'activated' && (
                <ActivatedConfig effect={draft} onChange={setDraft} />
              )}
              {draft.effect.kind === 'continuous' && (
                <ContinuousConfig effect={draft} onChange={setDraft} />
              )}
              {draft.effect.kind === 'replacement' && (
                <ReplacementConfig effect={draft} onChange={setDraft} kind="replacement" />
              )}
              {draft.effect.kind === 'prevention' && (
                <ReplacementConfig effect={draft} onChange={setDraft} kind="prevention" />
              )}
            </>
          )}
          {currentKey === 'conditions' && draft && (
            <ConditionsStep effect={draft} onChange={setDraft} previousSteps={previousSteps} />
          )}
          {currentKey === 'costs' && draft && (
            <EffectCostStep effect={draft} onChange={setDraft} />
          )}
          {currentKey === 'effect' && draft && (
            <EffectBodyStep effect={draft} onChange={setDraft} previousSteps={previousSteps} />
          )}
          {currentKey === 'review' && draft && <ReviewStep effect={draft} />}
        </div>
          <div className="border-t border-[color:var(--theme-border-default)] pt-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between px-4 sm:px-6 pb-4 sm:pb-6">
            <div className="text-xs text-[color:var(--theme-text-secondary)]">
              Step {stepIndex + 1} of {stepKeys.length}
              {currentKey ? ` — ${WIZARD_STEP_LABELS[currentKey]}` : ''}
            </div>
            <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
              <Button variant="outline" size="sm" onClick={onClose} className="w-full sm:w-auto">
                Cancel
              </Button>
              {stepIndex > 0 && (
                <Button variant="outline" size="sm" onClick={handleBack} className="w-full sm:w-auto">
                  Back
                </Button>
              )}
              {currentKey !== 'review' && (
                <Button variant="primary" size="sm" onClick={handleNext} disabled={!draft} className="w-full sm:w-auto">
                  Next
                </Button>
              )}
              {currentKey === 'review' && (
                <Button variant="primary" size="sm" onClick={handleSave} disabled={!draft} className="w-full sm:w-auto">
                  Save Effect
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>,
    document.body
  );
}
