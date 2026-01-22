// frontend/store/builderStore.ts

import { create } from 'zustand';
import type { CostEntry } from '@/lib/activationCosts';
import { parseManaCostSymbols } from '@/lib/wardCosts';

export interface CardData {
  card_id: string;
  oracle_id?: string;
  name: string;
  mana_cost?: string;
  mana_value?: number;
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
  rarity?: string;
  legalities?: Record<string, string>;
  prices?: {
    usd?: string;
    usd_foil?: string;
    eur?: string;
    tix?: string;
  };
  artist?: string;
  flavor_text?: string;
}

// Re-export condition types (must be before interfaces that use it)
import type { StructuredCondition } from '@/lib/conditionTypes';

// Ability Type Interfaces
export interface ModalChoiceConfig {
  min: number;
  max?: number | null;
  modes: Array<{ id: string; label: string }>;
}

export interface TriggeredAbility {
  id: string;
  event: string; // e.g., "enters_battlefield", "dies", "becomes_target", "card_enters"
  scope?: string; // "self", "any", "you_control", "opponent_control", "you", "opponent"
  condition?: StructuredCondition | string; // Structured condition or legacy string (ability-level gate)
  effects: Effect[];
  modal?: ModalChoiceConfig;
  usesStack?: boolean; // New: configurable stack behavior (default: true)
  // For card_enters event
  entersWhere?: string; // Zone where card enters (battlefield, graveyard, hand, etc.)
  entersFrom?: string; // Optional: zone card came from (hand, library, graveyard, etc.)
  cardType?: string; // Optional: card type filter (aura, creature, artifact, etc.)
}

// Re-export for convenience
export type { StructuredCondition };

export interface ActivatedAbility {
  id: string;
  costs: CostEntry[];
  effects: Effect[];
  modal?: ModalChoiceConfig;
  timing?: string;
  limit?: { scope: string; max: number };
  usesStack?: boolean; // New: configurable stack behavior (default: true, false for mana abilities)
}

export interface SpellAbility {
  id: string;
  effects: Effect[];
  modal?: ModalChoiceConfig;
}

export interface StaticAbility {
  id: string;
  appliesTo: string; // e.g., "self", "creatures_you_control", "enchanted_creature"
  effect: string; // Description of the static effect
  effectData?: Effect;
}

export interface ContinuousAbility {
  id: string;
  appliesTo: string;
  effect: string; // Description of the continuous effect
  effectData?: Effect;
}

export interface KeywordAbility {
  id: string;
  keyword: string; // Keyword name from database
  costs?: CostEntry[];
  number?: number; // For keywords with numbers (e.g., Annihilator 2)
  extraCosts?: CostEntry[];
}

// Re-export KeywordInfo from abilities for convenience
export type { KeywordInfo } from '@/lib/abilities';

// Per-effect condition for new refactored system
export interface EffectCondition {
  type: string; // 'was_cast', 'control_count', 'life_total', etc.
  target?: string; // 'triggering_aura', 'triggering_source', etc.
  comparison?: string; // '>=', '<=', '==', etc.
  value?: number | string;
  permanentType?: string;
  keyword?: string;
  counterType?: string;
  source?: string; // For mana_value_comparison
}

export interface Effect {
  type: string; // e.g., "damage", "draw", "token", "counters", "life", "search", "put_onto_battlefield", "attach", "shuffle"
  // New per-effect flags for refactored system
  optional?: boolean; // Per-effect optional flag ("may")
  condition?: EffectCondition; // Per-effect condition (was_cast, etc.)
  amount?: number;
  target?: string;
  maxTargets?: number;
  minTargets?: number;
  modeId?: string;
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
    compareAgainstSource?: string; // e.g., "triggering_source", "triggering_aura", "source"
  };
  attachTo?: string; // For attach effect
  attachSource?: boolean; // For attach effect (attach source to target)
  fromEffect?: number; // Index of previous effect to reference (0-based, e.g., 0 = first effect, 1 = second effect)
  // New fields for additional effect types
  duration?: string; // For temporary effects (until_end_of_turn, permanent, etc.)
  choice?: string; // For effects requiring player choice (color, creature_type, etc.)
  choiceValue?: string; // Optional fixed choice value
  protectionType?: string; // For protection effects
  keyword?: string; // For gain keyword effects
  powerChange?: number; // For change power/toughness effects
  toughnessChange?: number; // For change power/toughness effects
  yourCreature?: string; // For fight effects
  opponentCreature?: string; // For fight effects
  discardType?: string; // For discard effects
  position?: string; // For look at effects (top, bottom, random)
  returnUnderOwner?: boolean; // For flicker effects
  sourceTarget?: string; // For redirect damage effects
  redirectTarget?: string; // For redirect damage effects
  cdaSource?: string;
  cdaType?: string;
  cdaZone?: string;
  cdaSet?: string;
  fromZone?: string;
  toZone?: string;
  replacementZone?: string;
  uses?: number;
  distinctTargets?: boolean;
  chooseNewTargets?: boolean;
  [key: string]: any; // Additional effect-specific data
}

// Graph format for API compatibility
export interface AbilityNode {
  id: string;
  type: 'TRIGGER' | 'CONDITION' | 'EFFECT' | 'TARGET' | 'MODIFIER' | 'ACTIVATED' | 'KEYWORD' | 'SPELL';
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
  abilityType: 'triggered' | 'activated' | 'static' | 'keyword' | 'spell';
  // New fields for refactored system
  abilityId?: string; // e.g., "triggered-0", "activated-1"
  usesStack?: boolean; // Configurable stack behavior
}

export interface ValidationError {
  type: 'error' | 'warning';
  message: string;
  nodeId?: string;
}

export interface ValidationResponse {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}

export interface NormalizedAbility {
  trigger?: string;
  cost?: string;
  costs?: Array<Record<string, any>>;
  keyword?: string;
  conditions: Array<Record<string, any>>;
  effects: Array<Record<string, any>>;
  abilityType: string;
}

interface BuilderState {
  // Current card
  currentCard: CardData | null;
  
  // Ability lists
  triggeredAbilities: TriggeredAbility[];
  activatedAbilities: ActivatedAbility[];
  spellAbilities: SpellAbility[];
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
  
  addSpellAbility: (ability: SpellAbility) => void;
  updateSpellAbility: (id: string, ability: Partial<SpellAbility>) => void;
  removeSpellAbility: (id: string) => void;

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
  spellAbilities: [],
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
  
  // Spell Abilities
  addSpellAbility: (ability) => set((state) => ({
    spellAbilities: [...state.spellAbilities, ability],
  })),
  updateSpellAbility: (id, ability) => set((state) => ({
    spellAbilities: state.spellAbilities.map((a) =>
      a.id === id ? { ...a, ...ability } : a
    ),
  })),
  removeSpellAbility: (id) => set((state) => ({
    spellAbilities: state.spellAbilities.filter((a) => a.id !== id),
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
    let abilityType: 'triggered' | 'activated' | 'static' | 'keyword' | 'spell' = 'triggered';
    let abilityId = ''; // New: indexed ability ID
    let usesStack = true; // New: stack behavior flag
    
    // Process triggered abilities (with indexing)
    state.triggeredAbilities.forEach((ability, index) => {
      const indexedId = `triggered-${index}`;
      const triggerId = `trigger-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = triggerId;
        abilityType = 'triggered';
        abilityId = indexedId;
        usesStack = ability.usesStack !== false; // Default to true
      }
      
      nodes.push({
        id: triggerId,
        type: 'TRIGGER',
        data: { 
          event: ability.event,
          scope: ability.scope || 'self',
          usesStack: ability.usesStack !== false, // Include in trigger data
          ...(ability.modal && {
            modal: ability.modal,
          }),
          ...(ability.event === 'card_enters' && {
            entersWhere: ability.entersWhere,
            entersFrom: ability.entersFrom,
          }),
          ...(ability.cardType && ability.cardType !== '' && {
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
    
    // Process activated abilities (with indexing)
    state.activatedAbilities.forEach((ability, index) => {
      const indexedId = `activated-${index}`;
      const activatedId = `activated-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = activatedId;
        abilityType = 'activated';
        abilityId = indexedId;
        usesStack = ability.usesStack !== false; // Default to true
      }
      
      nodes.push({
        id: activatedId,
        type: 'ACTIVATED',
        data: {
          costs: ability.costs,
          timing: ability.timing,
          limit: ability.limit,
          usesStack: ability.usesStack !== false, // Include in ability data
          ...(ability.modal ? { modal: ability.modal } : {}),
        },
      });
      createEffectChain(ability.effects ?? [], ability.id, activatedId, nodes, edges);
    });

    // Process spell abilities (with indexing)
    state.spellAbilities.forEach((ability, index) => {
      const indexedId = `spell-${index}`;
      const spellId = `spell-${ability.id}`;
      if (!rootNodeId) {
        rootNodeId = spellId;
        abilityType = 'spell';
        abilityId = indexedId;
        usesStack = true; // Spells always use stack
      }

      nodes.push({
        id: spellId,
        type: 'SPELL',
        data: {
          ...(ability.modal ? { modal: ability.modal } : {}),
        },
      });
      createEffectChain(ability.effects ?? [], ability.id, spellId, nodes, edges);
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
          costs: keyword.costs,
          number: keyword.number,
          extraCosts: keyword.extraCosts,
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
      
      const effectPayload = ability.effectData ?? ability.effect;
      nodes.push({
        id: staticId,
        type: 'EFFECT',
        data: {
          appliesTo: ability.appliesTo,
          effect: effectPayload,
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
      
      const effectPayload = ability.effectData ?? ability.effect;
      nodes.push({
        id: continuousId,
        type: 'EFFECT',
        data: {
          appliesTo: ability.appliesTo,
          effect: effectPayload,
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
      // New fields for refactored system
      abilityId: abilityId || `${abilityType}-0`,
      usesStack,
    };
  },
  
  // Load abilities from graph (reverse of convertToGraph)
  loadFromGraph: (graph: AbilityGraph) => {
    const triggeredAbilities: TriggeredAbility[] = [];
    const activatedAbilities: ActivatedAbility[] = [];
    const spellAbilities: SpellAbility[] = [];
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
        const modal = triggerNode.data.modal || (graph as any).modal;
        const usesStack = triggerNode.data.usesStack !== false; // Default to true
        const triggeredAbility: TriggeredAbility = {
          id: abilityId,
          event,
          scope: triggerNode.data.scope || 'self',
          condition,
          effects,
          usesStack,
          ...(modal ? { modal } : {}),
          ...(event === 'card_enters' && {
            entersWhere: triggerNode.data.entersWhere,
            entersFrom: triggerNode.data.entersFrom,
          }),
          ...(triggerNode.data.cardType && { cardType: triggerNode.data.cardType }),
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
        let costs = Array.isArray(activatedNode.data.costs) ? activatedNode.data.costs : [];
        if (costs.length === 0 && typeof activatedNode.data.cost === 'string') {
          const raw = activatedNode.data.cost.trim();
          if (raw === '{T}' || raw.toLowerCase() === 'tap') {
            costs = [{ type: 'tap_self' }];
          } else if (raw.includes('{')) {
            costs = [{ type: 'mana', cost: parseManaCostSymbols(raw) }];
          }
        }
        const modal = activatedNode.data.modal || (graph as any).modal;
        const effectNodeMap = new Map<string, { node: AbilityNode; index: number }>();
        graph.nodes
          .filter(node => node.id.startsWith(`effect-${abilityId}-`))
          .forEach((node, idx) => {
            effectNodeMap.set(node.id, { node, index: idx });
          });
        const effects: Effect[] = [];
        const visitedEffects = new Set<string>();
        const buildEffectChain = (currentNodeId: string): void => {
          const nextEffectIds = adjacency[currentNodeId] || [];
          for (const nextId of nextEffectIds) {
            const effectInfo = effectNodeMap.get(nextId);
            if (effectInfo && !visitedEffects.has(nextId)) {
              visitedEffects.add(nextId);
              effects.push(effectInfo.node.data as Effect);
              buildEffectChain(nextId);
            }
          }
        };
        buildEffectChain(activatedNode.id);
        if (effects.length === 0 && activatedNode.data.effect) {
          effects.push(activatedNode.data.effect as Effect);
        }
        
        const usesStack = activatedNode.data.usesStack !== false; // Default to true
        activatedAbilities.push({
          id: abilityId,
          costs,
          effects,
          usesStack,
          ...(modal ? { modal } : {}),
          timing: activatedNode.data.timing,
          limit: activatedNode.data.limit,
        });
        
        processedNodes.add(activatedNode.id);
      });

    // Process spell abilities (spell-* nodes)
    graph.nodes
      .filter(node => node.id.startsWith('spell-'))
      .forEach(spellNode => {
        if (processedNodes.has(spellNode.id)) return;

        const abilityId = spellNode.id.replace('spell-', '');
        const modal = spellNode.data.modal || (graph as any).modal;
        const effectNodeMap = new Map<string, { node: AbilityNode; index: number }>();
        graph.nodes
          .filter(node => node.id.startsWith(`effect-${abilityId}-`))
          .forEach((node, idx) => {
            effectNodeMap.set(node.id, { node, index: idx });
          });
        const effects: Effect[] = [];
        const visitedEffects = new Set<string>();
        const buildEffectChain = (currentNodeId: string): void => {
          const nextEffectIds = adjacency[currentNodeId] || [];
          for (const nextId of nextEffectIds) {
            const effectInfo = effectNodeMap.get(nextId);
            if (effectInfo && !visitedEffects.has(nextId)) {
              visitedEffects.add(nextId);
              effects.push(effectInfo.node.data as Effect);
              buildEffectChain(nextId);
            }
          }
        };
        buildEffectChain(spellNode.id);
        if (effects.length === 0 && spellNode.data.effect) {
          effects.push(spellNode.data.effect as Effect);
        }

        spellAbilities.push({
          id: abilityId,
          effects,
          ...(modal ? { modal } : {}),
        });

        processedNodes.add(spellNode.id);
      });
    
    // Process keywords (keyword-* nodes)
    graph.nodes
      .filter(node => node.id.startsWith('keyword-'))
      .forEach(keywordNode => {
        if (processedNodes.has(keywordNode.id)) return;
        
        const abilityId = keywordNode.id.replace('keyword-', '');
        const data = keywordNode.data;
        
        let keywordCosts = Array.isArray(data.costs) ? data.costs : [];
        if (keywordCosts.length === 0 && typeof data.cost === 'string' && data.cost.includes('{')) {
          keywordCosts = [{ type: 'mana', cost: parseManaCostSymbols(data.cost) }];
        }
        keywords.push({
          id: abilityId,
          keyword: data.keyword || '',
          costs: keywordCosts,
          number: data.number,
          extraCosts: Array.isArray(data.extraCosts) ? data.extraCosts : [],
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
            effect: typeof data.effect === 'string' ? data.effect : '',
            effectData: typeof data.effect === 'object' ? data.effect : undefined,
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
            effect: typeof data.effect === 'string' ? data.effect : '',
            effectData: typeof data.effect === 'object' ? data.effect : undefined,
          });
          processedNodes.add(continuousNode.id);
        }
      });
    
    // Update store with loaded abilities
    set({
      triggeredAbilities,
      activatedAbilities,
      spellAbilities,
      staticAbilities,
      continuousAbilities,
      keywords,
    });
  },
  
  // Clear all abilities
  clearAll: () => set({
    triggeredAbilities: [],
    activatedAbilities: [],
    spellAbilities: [],
    staticAbilities: [],
    continuousAbilities: [],
    keywords: [],
    validationErrors: [],
    validationWarnings: [],
    isValid: false,
  }),
}));

