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
    const referenced = new Set<string>();
    const addReferenced = (value: string | string[] | undefined) => {
      if (!value) return;
      if (Array.isArray(value)) {
        value.forEach((id) => referenced.add(id));
        return;
      }
      referenced.add(value);
    };
    for (const step of steps) {
      if (Array.isArray(step.next)) {
        step.next.forEach((id) => referenced.add(id));
      }
      if (step.nextByMode) {
        Object.values(step.nextByMode).forEach((nextId) => addReferenced(nextId));
      }
    }
    const rootSteps = steps.filter((step) => !referenced.has(step.id));
    const sourceRoots = rootSteps.length ? rootSteps : [steps[0]];
    const hasPermanentRoot = sourceRoots.some((step) => {
      if (step.effect.initiation === 'triggered' && !!step.effect.trigger) return true;
      if (step.effect.initiation === 'activated' && !!step.effect.cost) return true;
      if (step.effect.effect.kind === 'continuous') return true;
      if (step.effect.effect.kind === 'replacement') return true;
      if (step.effect.effect.kind === 'prevention') return true;
      return false;
    });
    const effectiveSourceKind = hasPermanentRoot ? 'permanent' : sourceKind;
    const additionalCosts = extractAdditionalCosts(steps);
    const optionalCosts = extractOptionalCosts(steps);
    const graphId = currentCard?.card_id ? `graph-${currentCard.card_id}` : createId();
    const stepIds = new Set(steps.map((step) => step.id));
    const sanitizeNext = (value: string[] | undefined) => {
      if (!Array.isArray(value)) return undefined;
      const cleaned = value.filter((id) => stepIds.has(id));
      return cleaned.length > 0 ? cleaned : undefined;
    };
    const sanitizeNextByMode = (value: Record<string, string> | undefined) => {
      if (!value) return undefined;
      const cleaned: Record<string, string> = {};
      Object.entries(value).forEach(([mode, nextId]) => {
        if (stepIds.has(nextId)) {
          cleaned[mode] = nextId;
        }
      });
      return Object.keys(cleaned).length > 0 ? cleaned : undefined;
    };
    const indexById = new Map(steps.map((step, index) => [step.id, index]));
    const normalizeConditions = (conditions: EffectStep['effect']['conditions']) => {
      if (!Array.isArray(conditions)) return conditions;
      return conditions.map((condition) => {
        if (!condition || typeof condition !== 'object') return condition;
        const type = (condition as any).type;
        if (
          type !== 'previous_effect_has_result' &&
          type !== 'previous_effect_result_count'
        ) {
          return condition;
        }
        const linkedTo = (condition as any).linkedToStepId;
        if (!linkedTo || !indexById.has(linkedTo)) return condition;
        return { ...condition, fromEffect: indexById.get(linkedTo) };
      });
    };

    const linkedSteps = steps.map((step) => {
      const next = sanitizeNext(step.next);
      const nextByMode = sanitizeNextByMode(step.nextByMode);
      const conditions = normalizeConditions(step.effect.conditions);
      const effect = conditions ? { ...step.effect, conditions } : step.effect;
      return {
        ...step,
        effect,
        ...(next ? { next } : { next: undefined }),
        ...(nextByMode ? { nextByMode } : { nextByMode: undefined }),
      };
    });
    return {
      id: graphId,
      sourceKind: effectiveSourceKind,
      steps: linkedSteps,
      ...(effectiveSourceKind === 'spell' && additionalCosts.length ? { additionalCosts } : {}),
      ...(effectiveSourceKind === 'spell' && optionalCosts.length ? { optionalCosts } : {}),
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
