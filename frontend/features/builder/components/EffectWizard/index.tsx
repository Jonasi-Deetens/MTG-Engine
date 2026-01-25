'use client';

import { useEffect, useMemo, useState } from 'react';

import type { EffectStep, SourceKind, UnifiedEffect } from '@/lib/unifiedEffect';
import { Button } from '@/components/ui/Button';
import { formatEffect } from '@/lib/effectTypes';
import { IntentStep } from './IntentStep';
import { TriggerConfig } from './TriggerConfig';
import { ActivatedConfig } from './ActivatedConfig';
import { ContinuousConfig } from './ContinuousConfig';
import { ReplacementConfig } from './ReplacementConfig';
import { ConditionsStep } from './ConditionsStep';
import { EffectCostStep } from './EffectCostStep';
import { EffectBodyStep } from './EffectBodyStep';
import { ReviewStep } from './ReviewStep';

type IntentType =
  | 'triggered'
  | 'activated'
  | 'always_on'
  | 'spell'
  | 'replacement'
  | 'prevention'
  | 'keyword';

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

  const stepKeys = useMemo(() => {
    const keys = ['intent', 'config', 'conditions', 'costs', 'effect', 'review'];
    if (draft && draft.effect.kind !== 'one_shot') {
      return keys.filter((key) => key !== 'effect');
    }
    return keys;
  }, [draft]);
  const previousSteps = useMemo(() => {
    if (!steps.length) return [];
    const currentIndex =
      editingStepId ? steps.findIndex((step) => step.id === editingStepId) : steps.length;
    const sliceIndex = currentIndex >= 0 ? currentIndex : steps.length;
    return steps.slice(0, sliceIndex).map((step, index) => ({
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

  if (!isOpen) {
    return null;
  }

  const currentKey = stepKeys[stepIndex];
  const handleIntentSelect = (nextIntent: IntentType) => {
    setIntent(nextIntent);
    setDraft(createDefaultEffect(nextIntent));
    if (onSourceKindChange) {
      onSourceKindChange(nextIntent === 'spell' ? 'spell' : 'permanent');
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] rounded-lg w-full max-w-2xl">
        <div className="px-6 py-4 border-b border-[color:var(--theme-card-border)]">
          <h3 className="text-lg font-semibold text-[color:var(--theme-text-primary)]">
            {editingEffect ? 'Edit Effect' : 'Add Effect'}
          </h3>
        </div>
        <div className="px-6 py-4 space-y-4">
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
              {draft.initiation === 'static' && draft.effect.kind === 'one_shot' && (
                <div className="text-sm text-[color:var(--theme-text-secondary)]">
                  No extra configuration required for this intent.
                </div>
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
        <div className="px-6 py-4 border-t border-[color:var(--theme-card-border)] flex items-center justify-between">
          <div className="text-xs text-[color:var(--theme-text-secondary)]">
            Step {stepIndex + 1} of {stepKeys.length}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            {stepIndex > 0 && (
              <Button variant="outline" size="sm" onClick={handleBack}>
                Back
              </Button>
            )}
            {currentKey !== 'review' && (
              <Button variant="primary" size="sm" onClick={handleNext} disabled={!draft}>
                Next
              </Button>
            )}
            {currentKey === 'review' && (
              <Button variant="primary" size="sm" onClick={handleSave} disabled={!draft}>
                Save Effect
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
