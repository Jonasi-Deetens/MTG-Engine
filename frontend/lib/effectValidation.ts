import { z } from 'zod';

import type { EffectGraph, EffectStep } from './unifiedEffect';
import { CONDITION_TYPE_VALUES } from './conditionTypes';

const InitiationSchema = z.enum(['static', 'triggered', 'activated']);
const ResolutionSchema = z.enum(['stack', 'immediate']);
const PersistenceSchema = z.enum(['instant', 'continuous']);
const EffectTagSchema = z.enum(['mana', 'land', 'replacement', 'prevention', 'cda', 'keyword', 'loyalty']);
const SourceKindSchema = z.enum(['spell', 'permanent']);

const ConditionSchema = z.object({
  type: z.enum(CONDITION_TYPE_VALUES),
}).passthrough();

const TriggerSchema = z.object({
  event: z.string(),
  scope: z.string().optional(),
  cardType: z.union([z.string(), z.array(z.string())]).optional(),
  entersWhere: z.string().optional(),
  entersFrom: z.string().optional(),
}).passthrough();

const CostItemSchema = z.object({
  type: z.string(),
  amount: z.union([z.number(), z.string()]).optional(),
  manaType: z.string().optional(),
}).passthrough();

const OptionalCostSchema = z.object({
  kind: z.string(),
  tag: z.string().optional(),
  repeatable: z.boolean().optional(),
  costs: z.array(CostItemSchema).optional(),
}).passthrough();

const CostSpecSchema = z.object({
  items: z.array(CostItemSchema),
  timing: z.string().optional(),
  limit: z.record(z.string(), z.unknown()).optional(),
}).passthrough();

const DurationSchema = z.union([
  z.object({ type: z.literal('while_in_zone'), zone: z.string() }),
  z.object({ type: z.literal('until_end_of_turn') }),
  z.object({ type: z.literal('until_end_of_combat') }),
  z.object({ type: z.literal('until_your_next_turn') }),
  z.object({ type: z.literal('until_condition'), condition: ConditionSchema }),
]);

const OneShotActionSchema = z.object({
  type: z.string(),
}).passthrough();

const ModifierSchema = z.object({
  type: z.string(),
}).passthrough();

const OneShotEffectSchema = z.object({
  kind: z.literal('one_shot'),
  action: OneShotActionSchema,
});

const ContinuousEffectSchema = z.object({
  kind: z.literal('continuous'),
  layer: z.number(),
  modifier: ModifierSchema,
  appliesTo: z.union([z.string(), z.record(z.string(), z.unknown())]).optional(),
  duration: DurationSchema,
}).passthrough();

const ReplacementEffectSchema = z.object({
  kind: z.literal('replacement'),
  replaces: z.record(z.string(), z.unknown()),
  with: z.record(z.string(), z.unknown()),
}).passthrough();

const PreventionEffectSchema = z.object({
  kind: z.literal('prevention'),
  prevents: z.record(z.string(), z.unknown()),
  amount: z.union([z.number(), z.string(), z.record(z.string(), z.unknown())]).optional(),
}).passthrough();

const EffectBodySchema = z.union([
  OneShotEffectSchema,
  ContinuousEffectSchema,
  ReplacementEffectSchema,
  PreventionEffectSchema,
]);

const UnifiedEffectSchema = z.object({
  id: z.string(),
  initiation: InitiationSchema,
  resolution: ResolutionSchema,
  persistence: PersistenceSchema,
  tags: z.array(EffectTagSchema),
  trigger: TriggerSchema.optional(),
  cost: CostSpecSchema.optional(),
  conditions: z.array(ConditionSchema).optional(),
  effect: EffectBodySchema,
}).passthrough().superRefine((data, ctx) => {
  if (data.initiation === 'triggered' && !data.trigger) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "trigger is required when initiation is 'triggered'",
    });
  }
  if (data.initiation === 'activated' && !data.cost) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "cost is required when initiation is 'activated'",
    });
  }
  if (data.tags.includes('mana') && data.resolution !== 'immediate') {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "mana-tagged effects must resolve immediately",
    });
  }
  if (data.effect.kind === 'continuous' && data.persistence !== 'continuous') {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "continuous effects require persistence='continuous'",
    });
  }
});

const EffectStepSchema = z.object({
  id: z.string(),
  effect: UnifiedEffectSchema,
  next: z.array(z.string()).optional(),
  nextByMode: z.record(z.string(), z.string()).optional(),
});

const EffectGraphSchema = z.object({
  id: z.string(),
  sourceKind: SourceKindSchema,
  steps: z.array(EffectStepSchema),
  optionalCosts: z.array(OptionalCostSchema).optional(),
  modal: z.object({
    min: z.number(),
    max: z.number().nullable().optional(),
    modes: z.array(z.object({ id: z.string(), label: z.string() })),
  }).optional(),
});

const isPermanentRoot = (step: EffectStep) => {
  if (step.effect.initiation === 'triggered' && !!step.effect.trigger) return true;
  if (step.effect.initiation === 'activated' && !!step.effect.cost) return true;
  if (step.effect.effect.kind === 'continuous') return true;
  if (step.effect.effect.kind === 'replacement') return true;
  if (step.effect.effect.kind === 'prevention') return true;
  return false;
};

const isSpellRoot = (step: EffectStep) => {
  return (
    step.effect.initiation === 'static' &&
    step.effect.effect.kind === 'one_shot' &&
    !step.effect.trigger &&
    !step.effect.cost
  );
};

const getRootSteps = (steps: EffectStep[]) => {
  const referenced = new Set<string>();
  const addReferenced = (value: string | string[] | undefined) => {
    if (!value) return;
    if (Array.isArray(value)) {
      value.forEach((id) => referenced.add(id));
      return;
    }
    referenced.add(value);
  };
  steps.forEach((step) => {
    if (Array.isArray(step.next)) {
      step.next.forEach((id: string) => referenced.add(id));
    }
    if (step.nextByMode) {
      Object.values(step.nextByMode).forEach((nextId) => addReferenced(nextId as any));
    }
  });
  const roots = steps.filter((step) => !referenced.has(step.id));
  return roots.length ? roots : [steps[0]];
};

export function validateEffectGraph(graph: EffectGraph): { valid: boolean; errors: string[] } {
  const result = EffectGraphSchema.safeParse(graph);
  if (result.success) {
    return { valid: true, errors: [] };
  }
  const errors = result.error.issues.map((issue) => issue.message);
  return { valid: false, errors };
}

export function getEffectGraphWarnings(graph: EffectGraph | null): string[] {
  if (!graph?.steps?.length) return [];
  const roots = getRootSteps(graph.steps);
  const hasPermanentRoot = roots.some(isPermanentRoot);
  const hasSpellRoot = roots.some(isSpellRoot);
  if (hasPermanentRoot && hasSpellRoot) {
    return [
      'Graph mixes triggered/activated/continuous roots with spell roots. Split into separate graphs to avoid incorrect source kind.',
    ];
  }
  return [];
}
