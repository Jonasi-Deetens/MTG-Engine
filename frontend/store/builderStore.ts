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

// Re-export condition types (must be before interfaces that use it)
import type { StructuredCondition } from '@/lib/conditionTypes';

// Ability Type Interfaces
export interface TriggeredAbility {
  id: string;
  event: string; // e.g., "enters_battlefield", "dies", "becomes_target", "card_enters"
  condition?: StructuredCondition | string; // Structured condition or legacy string
  effects: Effect[];
  // For card_enters event
  entersWhere?: string; // Zone where card enters (battlefield, graveyard, hand, etc.)
  entersFrom?: string; // Optional: zone card came from (hand, library, graveyard, etc.)
  cardType?: string; // Optional: card type filter (aura, creature, artifact, etc.)
}

// Re-export for convenience
export type { StructuredCondition };

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
  type: string; // e.g., "damage", "draw", "token", "counters", "life", "search", "put_onto_battlefield", "attach", "shuffle"
  amount?: number;
  target?: string;
  manaType?: string;
  untapTarget?: string;
  zone?: string; // For search (library, graveyard, hand, exile)
  cardType?: string; // For search
  manaValueComparison?: string; // For search (e.g., "<=", ">=")
  manaValueComparisonValue?: number; // For search (fixed value)
  manaValueComparisonSource?: string; // For search (triggering_source, triggering_aura, etc.)
  differentName?: boolean | { // For search - can be boolean (legacy) or object with parameters
    enabled: boolean;
    compareAgainstType?: string; // e.g., "aura", "creature", "artifact" - if not set, means "any card"
    compareAgainstZone?: string; // e.g., "controlled", "battlefield", "graveyard" - defaults to "controlled"
  };
  attachTo?: string; // For attach effect
  fromEffect?: number; // Index of previous effect to reference (0-based, e.g., 0 = first effect, 1 = second effect)
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
  loadFromGraph: (graph: AbilityGraph) => void;
  
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
    // Helper function to create effect nodes and chain them based on fromEffect references
    const createEffectChain = (
      effects: Effect[],
      abilityId: string,
      startNodeId: string, // The node to connect the first effect to (condition or trigger)
      nodes: AbilityNode[],
      edges: AbilityEdge[]
    ): void => {
      if (effects.length === 0) return;
      
      // Create all effect nodes first
      const effectIds: string[] = [];
      effects.forEach((effect, idx) => {
        const effectId = `effect-${abilityId}-${idx}`;
        effectIds.push(effectId);
        nodes.push({
          id: effectId,
          type: 'EFFECT',
          data: effect,
        });
      });
      
      // Build edges: chain effects based on fromEffect, or connect to startNode
      effects.forEach((effect, idx) => {
        const effectId = effectIds[idx];
        
        if (effect.fromEffect !== undefined && effect.fromEffect >= 0 && effect.fromEffect < idx) {
          // This effect references a previous effect - chain it
          const previousEffectId = effectIds[effect.fromEffect];
          edges.push({ from_: previousEffectId, to: effectId });
        } else {
          // This effect doesn't reference a previous effect - connect to start node
          edges.push({ from_: startNodeId, to: effectId });
        }
      });
    };
    
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
        data: { 
          event: ability.event,
          ...(ability.event === 'card_enters' && {
            entersWhere: ability.entersWhere,
            entersFrom: ability.entersFrom,
            cardType: ability.cardType,
          }),
        },
      });
      
      if (ability.condition) {
        const conditionId = `condition-${ability.id}`;
        // Handle both structured and legacy string conditions
        const conditionData = typeof ability.condition === 'string' 
          ? { condition: ability.condition, isStructured: false }
          : { ...ability.condition, isStructured: true };
        
        nodes.push({
          id: conditionId,
          type: 'CONDITION',
          data: conditionData,
        });
        edges.push({ from_: triggerId, to: conditionId });
        
        // Create effect chain starting from condition
        createEffectChain(ability.effects, ability.id, conditionId, nodes, edges);
      } else {
        // Create effect chain starting from trigger
        createEffectChain(ability.effects, ability.id, triggerId, nodes, edges);
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
  
  // Load abilities from graph (reverse of convertToGraph)
  loadFromGraph: (graph: AbilityGraph) => {
    const triggeredAbilities: TriggeredAbility[] = [];
    const activatedAbilities: ActivatedAbility[] = [];
    const staticAbilities: StaticAbility[] = [];
    const continuousAbilities: ContinuousAbility[] = [];
    const keywords: KeywordAbility[] = [];
    
    // Build adjacency map for easier traversal
    const adjacency: Record<string, string[]> = {};
    graph.edges.forEach(edge => {
      if (!adjacency[edge.from_]) {
        adjacency[edge.from_] = [];
      }
      adjacency[edge.from_].push(edge.to);
    });
    
    // Group nodes by their prefix to identify ability groups
    const nodeMap = new Map(graph.nodes.map(node => [node.id, node]));
    const processedNodes = new Set<string>();
    
    // Process triggered abilities (trigger-* nodes)
    graph.nodes
      .filter(node => node.id.startsWith('trigger-'))
      .forEach(triggerNode => {
        if (processedNodes.has(triggerNode.id)) return;
        
        const abilityId = triggerNode.id.replace('trigger-', '');
        const event = triggerNode.data.event || '';
        
        // Find connected nodes
        const connectedIds = adjacency[triggerNode.id] || [];
        const conditionNode = connectedIds
          .map(id => nodeMap.get(id))
          .find(node => node?.type === 'CONDITION');
        
        const effectNodes = connectedIds
          .map(id => nodeMap.get(id))
          .filter(node => node?.type === 'EFFECT');
        
        // Find the start node for effects (condition or trigger)
        const effectStartNodeId = conditionNode ? conditionNode.id : triggerNode.id;
        
        // Reconstruct effects by following the chain from the start node
        // Effects can be chained: startNode → effect0 → effect1 → effect2
        const effects: Effect[] = [];
        const effectNodeMap = new Map<string, { node: AbilityNode; index: number }>();
        
        // First, find all effect nodes and map them by their ID
        graph.nodes
          .filter(node => node.id.startsWith(`effect-${abilityId}-`))
          .forEach((node, idx) => {
            effectNodeMap.set(node.id, { node, index: idx });
          });
        
        // Build effect chain by following edges from start node
        const visitedEffects = new Set<string>();
        const buildEffectChain = (currentNodeId: string): void => {
          const nextEffectIds = adjacency[currentNodeId] || [];
          
          for (const nextId of nextEffectIds) {
            const effectInfo = effectNodeMap.get(nextId);
            if (effectInfo && !visitedEffects.has(nextId)) {
              visitedEffects.add(nextId);
              effects.push(effectInfo.node.data as Effect);
              // Continue following the chain
              buildEffectChain(nextId);
            }
          }
        };
        
        // Start building chain from the start node
        buildEffectChain(effectStartNodeId);
        
        // Reconstruct condition
        let condition: StructuredCondition | string | undefined = undefined;
        if (conditionNode) {
          const conditionData = conditionNode.data;
          if (conditionData.isStructured) {
            // Remove the isStructured flag
            const { isStructured, ...rest } = conditionData;
            condition = rest as StructuredCondition;
          } else {
            condition = conditionData.condition as string;
          }
        }
        
        // Extract card_enters specific fields from trigger data
        const triggeredAbility: TriggeredAbility = {
          id: abilityId,
          event,
          condition,
          effects,
          ...(event === 'card_enters' && {
            entersWhere: triggerNode.data.entersWhere,
            entersFrom: triggerNode.data.entersFrom,
            cardType: triggerNode.data.cardType,
          }),
        };
        
        triggeredAbilities.push(triggeredAbility);
        processedNodes.add(triggerNode.id);
        if (conditionNode) processedNodes.add(conditionNode.id);
        // Mark all effect nodes as processed
        effectNodeMap.forEach((_, effectId) => {
          processedNodes.add(effectId);
        });
      });
    
    // Process activated abilities (activated-* nodes)
    graph.nodes
      .filter(node => node.id.startsWith('activated-'))
      .forEach(activatedNode => {
        if (processedNodes.has(activatedNode.id)) return;
        
        const abilityId = activatedNode.id.replace('activated-', '');
        const cost = activatedNode.data.cost || '';
        const effect = activatedNode.data.effect as Effect;
        
        activatedAbilities.push({
          id: abilityId,
          cost,
          effect,
        });
        
        processedNodes.add(activatedNode.id);
      });
    
    // Process keywords (keyword-* nodes)
    graph.nodes
      .filter(node => node.id.startsWith('keyword-'))
      .forEach(keywordNode => {
        if (processedNodes.has(keywordNode.id)) return;
        
        const abilityId = keywordNode.id.replace('keyword-', '');
        const data = keywordNode.data;
        
        keywords.push({
          id: abilityId,
          keyword: data.keyword || '',
          cost: data.cost,
          number: data.number,
          lifeCost: data.lifeCost,
          sacrificeCost: data.sacrificeCost,
        });
        
        processedNodes.add(keywordNode.id);
      });
    
    // Process static abilities (static-* nodes with EFFECT type and abilityType: 'static')
    graph.nodes
      .filter(node => node.id.startsWith('static-'))
      .forEach(staticNode => {
        if (processedNodes.has(staticNode.id)) return;
        
        const abilityId = staticNode.id.replace('static-', '');
        const data = staticNode.data;
        
        if (data.abilityType === 'static') {
          staticAbilities.push({
            id: abilityId,
            appliesTo: data.appliesTo || '',
            effect: data.effect || '',
          });
          processedNodes.add(staticNode.id);
        }
      });
    
    // Process continuous abilities (continuous-* nodes with EFFECT type and abilityType: 'continuous')
    graph.nodes
      .filter(node => node.id.startsWith('continuous-'))
      .forEach(continuousNode => {
        if (processedNodes.has(continuousNode.id)) return;
        
        const abilityId = continuousNode.id.replace('continuous-', '');
        const data = continuousNode.data;
        
        if (data.abilityType === 'continuous') {
          continuousAbilities.push({
            id: abilityId,
            appliesTo: data.appliesTo || '',
            effect: data.effect || '',
          });
          processedNodes.add(continuousNode.id);
        }
      });
    
    // Update store with loaded abilities
    set({
      triggeredAbilities,
      activatedAbilities,
      staticAbilities,
      continuousAbilities,
      keywords,
    });
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

