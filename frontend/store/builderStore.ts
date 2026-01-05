// frontend/store/builderStore.ts

import { create } from 'zustand';

export interface CardData {
  card_id: string;
  name: string;
  mana_cost?: string;
  type_line?: string;
  oracle_text?: string;
  power?: string;
  toughness?: string;
  colors?: string[];
  image_uris?: {
    small?: string;
    normal?: string;
    large?: string;
  };
  set_code?: string;
  collector_number?: string;
}

// Ability Type Interfaces
export interface TriggeredAbility {
  id: string;
  event: string; // e.g., "enters_battlefield", "dies", "becomes_target"
  condition?: string;
  effects: Effect[];
}

export interface ActivatedAbility {
  id: string;
  cost: string; // e.g., "{T}", "{1}{R}", "Sacrifice a creature"
  effect: Effect;
}

export interface StaticAbility {
  id: string;
  appliesTo: string; // e.g., "self", "creatures_you_control", "enchanted_creature"
  effect: string; // Description of the static effect
}

export interface ContinuousAbility {
  id: string;
  appliesTo: string;
  effect: string; // Description of the continuous effect
}

export interface KeywordAbility {
  id: string;
  keyword: string; // Keyword name from database
  cost?: string; // For keywords with costs (e.g., Ward {2})
  number?: number; // For keywords with numbers (e.g., Annihilator 2)
  lifeCost?: number; // For keywords with life costs
  sacrificeCost?: boolean; // For keywords with sacrifice costs
}

// Re-export KeywordInfo from abilities for convenience
export type { KeywordInfo } from '@/lib/abilities';

export interface Effect {
  type: string; // e.g., "damage", "draw", "token", "counters", "life"
  amount?: number;
  target?: string;
  [key: string]: any; // Additional effect-specific data
}

// Graph format for API compatibility
export interface AbilityNode {
  id: string;
  type: 'TRIGGER' | 'CONDITION' | 'EFFECT' | 'TARGET' | 'MODIFIER' | 'ACTIVATED' | 'KEYWORD';
  data: Record<string, any>;
}

export interface AbilityEdge {
  from_: string;
  to: string;
}

export interface AbilityGraph {
  id?: string;
  rootNodeId: string;
  nodes: AbilityNode[];
  edges: AbilityEdge[];
  abilityType: 'triggered' | 'activated' | 'static' | 'keyword';
}

export interface ValidationError {
  type: 'error' | 'warning';
  message: string;
  nodeId?: string;
}

interface BuilderState {
  // Current card
  currentCard: CardData | null;
  
  // Ability lists
  triggeredAbilities: TriggeredAbility[];
  activatedAbilities: ActivatedAbility[];
  staticAbilities: StaticAbility[];
  continuousAbilities: ContinuousAbility[];
  keywords: KeywordAbility[];
  
  // Validation
  validationErrors: ValidationError[];
  validationWarnings: ValidationError[];
  isValid: boolean;
  
  // Actions
  setCurrentCard: (card: CardData | null) => void;
  
  // Ability management
  addTriggeredAbility: (ability: TriggeredAbility) => void;
  updateTriggeredAbility: (id: string, ability: Partial<TriggeredAbility>) => void;
  removeTriggeredAbility: (id: string) => void;
  
  addActivatedAbility: (ability: ActivatedAbility) => void;
  updateActivatedAbility: (id: string, ability: Partial<ActivatedAbility>) => void;
  removeActivatedAbility: (id: string) => void;
  
  addStaticAbility: (ability: StaticAbility) => void;
  updateStaticAbility: (id: string, ability: Partial<StaticAbility>) => void;
  removeStaticAbility: (id: string) => void;
  
  addContinuousAbility: (ability: ContinuousAbility) => void;
  updateContinuousAbility: (id: string, ability: Partial<ContinuousAbility>) => void;
  removeContinuousAbility: (id: string) => void;
  
  addKeyword: (keyword: KeywordAbility) => void;
  updateKeyword: (id: string, keyword: Partial<KeywordAbility>) => void;
  removeKeyword: (id: string) => void;
  
  // Validation
  setValidation: (errors: ValidationError[], warnings: ValidationError[], isValid: boolean) => void;
  
  // Graph conversion
  convertToGraph: () => AbilityGraph | null;
  
  // Clear all
  clearAll: () => void;
}

export const useBuilderStore = create<BuilderState>((set, get) => ({
  // Initial state
  currentCard: null,
  triggeredAbilities: [],
  activatedAbilities: [],
  staticAbilities: [],
  continuousAbilities: [],
  keywords: [],
  validationErrors: [],
  validationWarnings: [],
  isValid: false,
  
  // Actions
  setCurrentCard: (card) => set({ currentCard: card }),
  
  // Triggered Abilities
  addTriggeredAbility: (ability) => set((state) => ({
    triggeredAbilities: [...state.triggeredAbilities, ability],
  })),
  updateTriggeredAbility: (id, ability) => set((state) => ({
    triggeredAbilities: state.triggeredAbilities.map((a) =>
      a.id === id ? { ...a, ...ability } : a
    ),
  })),
  removeTriggeredAbility: (id) => set((state) => ({
    triggeredAbilities: state.triggeredAbilities.filter((a) => a.id !== id),
  })),
  
  // Activated Abilities
  addActivatedAbility: (ability) => set((state) => ({
    activatedAbilities: [...state.activatedAbilities, ability],
  })),
  updateActivatedAbility: (id, ability) => set((state) => ({
    activatedAbilities: state.activatedAbilities.map((a) =>
      a.id === id ? { ...a, ...ability } : a
    ),
  })),
  removeActivatedAbility: (id) => set((state) => ({
    activatedAbilities: state.activatedAbilities.filter((a) => a.id !== id),
  })),
  
  // Static Abilities
  addStaticAbility: (ability) => set((state) => ({
    staticAbilities: [...state.staticAbilities, ability],
  })),
  updateStaticAbility: (id, ability) => set((state) => ({
    staticAbilities: state.staticAbilities.map((a) =>
      a.id === id ? { ...a, ...ability } : a
    ),
  })),
  removeStaticAbility: (id) => set((state) => ({
    staticAbilities: state.staticAbilities.filter((a) => a.id !== id),
  })),
  
  // Continuous Abilities
  addContinuousAbility: (ability) => set((state) => ({
    continuousAbilities: [...state.continuousAbilities, ability],
  })),
  updateContinuousAbility: (id, ability) => set((state) => ({
    continuousAbilities: state.continuousAbilities.map((a) =>
      a.id === id ? { ...a, ...ability } : a
    ),
  })),
  removeContinuousAbility: (id) => set((state) => ({
    continuousAbilities: state.continuousAbilities.filter((a) => a.id !== id),
  })),
  
  // Keywords
  addKeyword: (keyword) => set((state) => ({
    keywords: [...state.keywords, keyword],
  })),
  updateKeyword: (id, keyword) => set((state) => ({
    keywords: state.keywords.map((k) =>
      k.id === id ? { ...k, ...keyword } : k
    ),
  })),
  removeKeyword: (id) => set((state) => ({
    keywords: state.keywords.filter((k) => k.id !== id),
  })),
  
  // Validation
  setValidation: (errors, warnings, isValid) => set({
    validationErrors: errors,
    validationWarnings: warnings,
    isValid,
  }),
  
  // Convert ability lists to graph format for API
  convertToGraph: () => {
    const state = get();
    const nodes: AbilityNode[] = [];
    const edges: AbilityEdge[] = [];
    let rootNodeId = '';
    let abilityType: 'triggered' | 'activated' | 'static' | 'keyword' = 'triggered';
    
    // Process triggered abilities
    state.triggeredAbilities.forEach((ability) => {
      const triggerId = `trigger-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = triggerId;
        abilityType = 'triggered';
      }
      
      nodes.push({
        id: triggerId,
        type: 'TRIGGER',
        data: { event: ability.event },
      });
      
      if (ability.condition) {
        const conditionId = `condition-${ability.id}`;
        nodes.push({
          id: conditionId,
          type: 'CONDITION',
          data: { condition: ability.condition },
        });
        edges.push({ from_: triggerId, to: conditionId });
        
        ability.effects.forEach((effect, idx) => {
          const effectId = `effect-${ability.id}-${idx}`;
          nodes.push({
            id: effectId,
            type: 'EFFECT',
            data: effect,
          });
          edges.push({ from_: conditionId, to: effectId });
        });
      } else {
        ability.effects.forEach((effect, idx) => {
          const effectId = `effect-${ability.id}-${idx}`;
          nodes.push({
            id: effectId,
            type: 'EFFECT',
            data: effect,
          });
          edges.push({ from_: triggerId, to: effectId });
        });
      }
    });
    
    // Process activated abilities
    state.activatedAbilities.forEach((ability) => {
      const activatedId = `activated-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = activatedId;
        abilityType = 'activated';
      }
      
      nodes.push({
        id: activatedId,
        type: 'ACTIVATED',
        data: { cost: ability.cost, effect: ability.effect },
      });
    });
    
    // Process keywords
    state.keywords.forEach((keyword) => {
      const keywordId = `keyword-${keyword.id}`;
      if (!rootNodeId) {
        rootNodeId = keywordId;
        abilityType = 'keyword';
      }
      
      nodes.push({
        id: keywordId,
        type: 'KEYWORD',
        data: {
          keyword: keyword.keyword,
          cost: keyword.cost,
          number: keyword.number,
          lifeCost: keyword.lifeCost,
          sacrificeCost: keyword.sacrificeCost,
        },
      });
    });
    
    // Process static abilities (simplified - just one node per ability)
    state.staticAbilities.forEach((ability) => {
      const staticId = `static-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = staticId;
        abilityType = 'static';
      }
      
      nodes.push({
        id: staticId,
        type: 'EFFECT',
        data: {
          appliesTo: ability.appliesTo,
          effect: ability.effect,
          abilityType: 'static',
        },
      });
    });
    
    // Process continuous abilities (similar to static)
    state.continuousAbilities.forEach((ability) => {
      const continuousId = `continuous-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = continuousId;
        abilityType = 'static'; // Continuous abilities are a type of static
      }
      
      nodes.push({
        id: continuousId,
        type: 'EFFECT',
        data: {
          appliesTo: ability.appliesTo,
          effect: ability.effect,
          abilityType: 'continuous',
        },
      });
    });
    
    if (nodes.length === 0) {
      return null;
    }
    
    return {
      rootNodeId,
      nodes,
      edges,
      abilityType,
    };
  },
  
  // Clear all abilities
  clearAll: () => set({
    triggeredAbilities: [],
    activatedAbilities: [],
    staticAbilities: [],
    continuousAbilities: [],
    keywords: [],
    validationErrors: [],
    validationWarnings: [],
    isValid: false,
  }),
}));

