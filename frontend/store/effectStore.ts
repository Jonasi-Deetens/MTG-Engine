import { create } from 'zustand';

import type { CardData } from '@/store/builderStore';
import type { EffectGraph, EffectStep, SourceKind, UnifiedEffect } from '@/lib/unifiedEffect';
import type { CostEntry } from '@/lib/activationCosts';
import type { OptionalCostEntry } from '@/lib/optionalCosts';
import { normalizeOptionalCostEntry } from '@/lib/optionalCosts';

export interface EffectValidation {
  errors: string[];
  warnings: string[];
  isValid: boolean;
}

interface EffectStoreState {
  currentCard: CardData | null;
  sourceKind: SourceKind;
  steps: EffectStep[];
  validation: EffectValidation;

  setCurrentCard: (card: CardData | null) => void;
  setSourceKind: (sourceKind: SourceKind) => void;

  addStep: (effect: UnifiedEffect) => void;
  updateStep: (id: string, effect: Partial<UnifiedEffect>) => void;
  removeStep: (id: string) => void;
  reorderSteps: (fromIndex: number, toIndex: number) => void;
  setSteps: (steps: EffectStep[]) => void;

  toEffectGraph: () => EffectGraph | null;
  fromEffectGraph: (graph: EffectGraph) => void;
  setValidation: (errors: string[], warnings: string[], isValid: boolean) => void;
  clearAll: () => void;
}

const createId = () => {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
};

const extractAdditionalCosts = (steps: EffectStep[]) =>
  steps.flatMap((step) =>
    Array.isArray(step.effect.additionalCosts) ? (step.effect.additionalCosts as CostEntry[]) : []
  );

const extractOptionalCosts = (steps: EffectStep[]) =>
  steps.flatMap((step) =>
    Array.isArray(step.effect.optionalCosts)
      ? (step.effect.optionalCosts as OptionalCostEntry[]).map(normalizeOptionalCostEntry)
      : []
  );

export const useEffectStore = create<EffectStoreState>((set, get) => ({
  currentCard: null,
  sourceKind: 'permanent',
  steps: [],
  validation: {
    errors: [],
    warnings: [],
    isValid: false,
  },

  setCurrentCard: (card) => set({ currentCard: card }),
  setSourceKind: (sourceKind) => set({ sourceKind }),

  addStep: (effect) =>
    set((state) => ({
      steps: [...state.steps, { id: createId(), effect }],
    })),

  updateStep: (id, effect) =>
    set((state) => ({
      steps: state.steps.map((step) =>
        step.id === id ? { ...step, effect: { ...step.effect, ...effect } } : step
      ),
    })),

  removeStep: (id) =>
    set((state) => ({
      steps: state.steps.filter((step) => step.id !== id),
    })),

  reorderSteps: (fromIndex, toIndex) =>
    set((state) => {
      const steps = [...state.steps];
      const [moved] = steps.splice(fromIndex, 1);
      steps.splice(toIndex, 0, moved);
      return { steps };
    }),

  setSteps: (steps) => set({ steps }),

  toEffectGraph: () => {
    const { currentCard, sourceKind, steps } = get();
    if (!steps.length) {
      return null;
    }
    const additionalCosts = extractAdditionalCosts(steps);
    const optionalCosts = extractOptionalCosts(steps);
    const graphId = currentCard?.card_id ? `graph-${currentCard.card_id}` : createId();
    const linkedSteps = steps.map((step, index) => {
      if (step.next || step.nextByMode) {
        return step;
      }
      const nextStep = steps[index + 1];
      return nextStep ? { ...step, next: [nextStep.id] } : step;
    });
    return {
      id: graphId,
      sourceKind,
      steps: linkedSteps,
      ...(sourceKind === 'spell' && additionalCosts.length ? { additionalCosts } : {}),
      ...(sourceKind === 'spell' && optionalCosts.length ? { optionalCosts } : {}),
    };
  },

  fromEffectGraph: (graph) => {
    set({
      sourceKind: graph.sourceKind ?? 'permanent',
      steps: graph.steps ?? [],
    });
  },

  setValidation: (errors, warnings, isValid) =>
    set({
      validation: { errors, warnings, isValid },
    }),

  clearAll: () =>
    set({
      steps: [],
      sourceKind: 'permanent',
      validation: { errors: [], warnings: [], isValid: false },
    }),
}));
