export type Initiation = 'static' | 'triggered' | 'activated';
export type Resolution = 'stack' | 'immediate';
export type Persistence = 'instant' | 'continuous';

export type EffectTag =
  | 'mana'
  | 'land'
  | 'replacement'
  | 'prevention'
  | 'cda'
  | 'keyword'
  | 'loyalty';

export type SourceKind = 'spell' | 'permanent';

export interface ConditionSpec {
  type: string;
  [key: string]: unknown;
}

export interface TriggerSpec {
  event: string;
  scope?: string;
  cardType?: string;
  entersWhere?: string;
  entersFrom?: string;
  [key: string]: unknown;
}

export interface CostItem {
  type: string;
  amount?: number | string;
  manaType?: string;
  [key: string]: unknown;
}

export interface CostSpec {
  items: CostItem[];
  timing?: string;
  limit?: Record<string, unknown>;
  [key: string]: unknown;
}

export type Duration =
  | { type: 'while_in_zone'; zone: string }
  | { type: 'until_end_of_turn' }
  | { type: 'until_end_of_combat' }
  | { type: 'until_your_next_turn' }
  | { type: 'until_condition'; condition: ConditionSpec };

export interface OneShotAction {
  type: string;
  [key: string]: unknown;
}

export interface ModifierSpec {
  type: string;
  [key: string]: unknown;
}

export interface OneShotEffect {
  kind: 'one_shot';
  action: OneShotAction;
}

export interface ContinuousEffect {
  kind: 'continuous';
  layer: number;
  modifier: ModifierSpec;
  appliesTo?: Record<string, unknown> | string;
  duration: Duration;
  [key: string]: unknown;
}

export interface ReplacementEffect {
  kind: 'replacement';
  replaces: Record<string, unknown>;
  with: Record<string, unknown>;
  [key: string]: unknown;
}

export interface PreventionEffect {
  kind: 'prevention';
  prevents: Record<string, unknown>;
  amount?: number | string | Record<string, unknown>;
  [key: string]: unknown;
}

export type EffectBody =
  | OneShotEffect
  | ContinuousEffect
  | ReplacementEffect
  | PreventionEffect;

export interface UnifiedEffect {
  id: string;
  initiation: Initiation;
  resolution: Resolution;
  persistence: Persistence;
  tags: EffectTag[];
  trigger?: TriggerSpec;
  cost?: CostSpec;
  conditions?: ConditionSpec[];
  effect: EffectBody;
  [key: string]: unknown;
}

export interface EffectStep {
  id: string;
  effect: UnifiedEffect;
  next?: string[];
  nextByMode?: Record<string, string>;
}

export interface EffectGraph {
  id: string;
  sourceKind: SourceKind;
  steps: EffectStep[];
  modal?: {
    min: number;
    max?: number | null;
    modes: Array<{ id: string; label: string }>;
  };
}
