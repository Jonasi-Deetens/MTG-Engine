import { isEffectActiveForModes, ModalChoiceConfig } from '@/lib/modalChoices';
import type { EffectGraph } from '@/lib/unifiedEffect';

export type TargetHints = {
  allowPlayers: boolean;
  allowObjects: boolean;
  objectTypes: Set<string>;
  maxObjectTargets: number | null;
  maxPlayerTargets: number | null;
  playerFilter: 'any' | 'opponent' | 'controller';
  objectFilter: 'any' | 'opponent' | 'controller';
};

const normalizeTarget = (value?: string) => (value || '').toLowerCase();

const ANY_TARGET_OBJECT_TYPES = new Set(['Creature', 'Planeswalker', 'Battle']);

const isGroupSelector = (target: string) =>
  target.startsWith('each_') ||
  (!target.startsWith('target_') && target.endsWith('_you_control')) ||
  (!target.startsWith('target_') && target.endsWith('_opponents_control')) ||
  target === 'you_control' ||
  target === 'opponent_control' ||
  target === 'each_player' ||
  target === 'each_opponent';

const mapTargetToType = (target: string) => {
  if (isGroupSelector(target)) return null;
  if (target.includes('creature')) return 'Creature';
  if (target.includes('artifact')) return 'Artifact';
  if (target.includes('enchantment')) return 'Enchantment';
  if (target.includes('planeswalker')) return 'Planeswalker';
  if (target.includes('land')) return 'Land';
  return null;
};

const parseLimit = (value: unknown): number | null => {
  if (typeof value === 'number' && Number.isFinite(value) && value > 0) return value;
  if (typeof value === 'string') {
    const parsed = parseInt(value, 10);
    if (!Number.isNaN(parsed) && parsed > 0) return parsed;
  }
  return null;
};

export type EffectTargetSpec = {
  key: string;
  label: string;
  target: string;
  maxTargets?: number | null;
  minTargets?: number | null;
  allowPlayers?: boolean;
  allowObjects?: boolean;
  useStackObjects?: boolean;
  required?: boolean;
  distinct?: boolean;
};

export const deriveTargetHintsForTarget = (
  target: string,
  maxTargets?: number | null,
  overrides?: { allowPlayers?: boolean; allowObjects?: boolean }
): TargetHints => {
  const normalized = normalizeTarget(target);
  const hints: TargetHints = {
    allowPlayers: false,
    allowObjects: false,
    objectTypes: new Set(),
    maxObjectTargets: null,
    maxPlayerTargets: null,
    playerFilter: 'any',
    objectFilter: 'any',
  };
  if (!normalized || isGroupSelector(normalized)) {
    return hints;
  }
  if (normalized === 'any' || normalized === 'target') {
    hints.allowObjects = true;
    hints.allowPlayers = true;
    ANY_TARGET_OBJECT_TYPES.forEach((type) => hints.objectTypes.add(type));
  } else if (normalized.includes('permanent')) {
    hints.allowObjects = true;
  }
  if (normalized.includes('spell')) {
    hints.allowObjects = true;
  }
  if (normalized === 'opponent') {
    hints.allowPlayers = true;
    hints.playerFilter = 'opponent';
  } else if (normalized.includes('player')) {
    hints.allowPlayers = true;
  }
  if (normalized.endsWith('_you_control') && normalized.startsWith('target_')) {
    hints.allowObjects = true;
    hints.objectFilter = 'controller';
  }
  if (normalized.endsWith('_opponents_control') && normalized.startsWith('target_')) {
    hints.allowObjects = true;
    hints.objectFilter = 'opponent';
  }
  const mapped = mapTargetToType(normalized);
  if (mapped) {
    hints.allowObjects = true;
    hints.objectTypes.add(mapped);
  }
  if (maxTargets && maxTargets > 0) {
    if (hints.allowObjects) {
      hints.maxObjectTargets = maxTargets;
    }
    if (hints.allowPlayers) {
      hints.maxPlayerTargets = maxTargets;
    }
  }
  if (overrides?.allowPlayers === false) {
    hints.allowPlayers = false;
    hints.maxPlayerTargets = null;
  }
  if (overrides?.allowObjects === false) {
    hints.allowObjects = false;
    hints.maxObjectTargets = null;
  }
  return hints;
};

export const deriveTargetSpecs = (effect: any): EffectTargetSpec[] => {
  if (!effect || !effect.type) return [];
  const specs: EffectTargetSpec[] = [];
  if (effect.type === 'search') {
    return specs;
  }
  const hasFromEffect = typeof effect.fromEffect === 'number';
  const minTargets = effect.minTargets;
  const maxTargets = effect.maxTargets;
  const shouldInferTargets = hasFromEffect && minTargets == null && maxTargets == null;
  if (effect.type === 'fight') {
    specs.push({
      key: 'yourCreature',
      label: 'Your creature',
      target: effect.yourCreature || 'creature',
      maxTargets: 1,
      allowPlayers: false,
      required: true,
      distinct: true,
    });
    specs.push({
      key: 'opponentCreature',
      label: 'Opponent creature',
      target: effect.opponentCreature || 'creature',
      maxTargets: 1,
      allowPlayers: false,
      required: true,
      distinct: true,
    });
    return specs;
  }
  if (effect.type === 'redirect_damage') {
    specs.push({
      key: 'sourceTarget',
      label: 'Source target',
      target: effect.sourceTarget || 'target',
      maxTargets: 1,
      allowPlayers: false,
      required: true,
    });
    specs.push({
      key: 'redirectTarget',
      label: 'Redirect target',
      target: effect.redirectTarget || 'target',
      maxTargets: 1,
      allowPlayers: true,
      required: true,
    });
    return specs;
  }
  if (effect.type === 'attach') {
    if (effect.attachTo === 'source' || effect.attachTo === 'self') {
      return specs;
    }
    specs.push({
      key: 'attach_to',
      label: 'Attach to',
      target: effect.attachTo || 'target_permanent',
      maxTargets: 1,
      minTargets: 1,
      allowPlayers: false,
      required: true,
    });
    return specs;
  }
  if (shouldInferTargets) {
    return specs;
  }
  const target = effect.target || effect.untapTarget;
  if (target) {
    const minTargets = typeof effect.minTargets === 'number' ? effect.minTargets : null;
    const maxTargets =
      parseLimit(effect.maxTargets) ??
      parseLimit(effect.max_targets) ??
      parseLimit(effect.target_count);
    const requiresTarget = minTargets === null || minTargets > 0;
    specs.push({
      key: 'target',
      label: 'Target',
      target,
      maxTargets,
      minTargets,
      useStackObjects: target === 'spell',
      required: requiresTarget,
      distinct: !!effect.distinctTargets,
    });
  }
  return specs;
};

const filterEffectSteps = (
  graph: EffectGraph | null,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
) => {
  if (!graph?.steps?.length) return [];
  return graph.steps.filter((step) => {
    if (!step?.effect) return false;
    return isEffectActiveForModes(step.effect, modalConfig ?? null, selectedModes);
  });
};

const filterEffectNodes = (
  graph: any,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
) => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  return graph.nodes.filter((node: any) => {
    if (!node?.data) return false;
    return isEffectActiveForModes(node.data, modalConfig ?? null, selectedModes);
  });
};

export const deriveTargetHints = (
  graph?: EffectGraph | null,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
): TargetHints => {
  if (!graph?.steps?.length) {
    return {
      allowPlayers: true,
      allowObjects: true,
      objectTypes: new Set(),
      maxObjectTargets: null,
      maxPlayerTargets: null,
      playerFilter: 'any',
      objectFilter: 'any',
    };
  }

  const hints: TargetHints = {
    allowPlayers: false,
    allowObjects: false,
    objectTypes: new Set(),
    maxObjectTargets: null,
    maxPlayerTargets: null,
    playerFilter: 'any',
    objectFilter: 'any',
  };
  const effectSteps = filterEffectSteps(graph, modalConfig, selectedModes);

  effectSteps.forEach((step: any) => {
    const effectBody = step?.effect?.effect;
    if (effectBody?.kind !== 'one_shot') return;
    const action = effectBody?.action ?? {};
    const target = normalizeTarget(action?.target || action?.targetType || '');
    const limit =
      parseLimit(action?.maxTargets) ??
      parseLimit(action?.max_targets) ??
      parseLimit(action?.target_count);
    if (!target) return;
    if (isGroupSelector(target)) {
      return;
    }

    if (target === 'any' || target === 'target') {
      hints.allowObjects = true;
      hints.allowPlayers = true;
      ANY_TARGET_OBJECT_TYPES.forEach((type) => hints.objectTypes.add(type));
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
        hints.maxPlayerTargets = hints.maxPlayerTargets ? Math.min(hints.maxPlayerTargets, limit) : limit;
      }
    } else if (target.includes('permanent')) {
      hints.allowObjects = true;
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
      }
    }
    if (target.includes('spell')) {
      hints.allowObjects = true;
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
      }
    }
    if (target.endsWith('_you_control') && target.startsWith('target_')) {
      hints.allowObjects = true;
      hints.objectFilter = 'controller';
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
      }
    } else if (target.endsWith('_opponents_control') && target.startsWith('target_')) {
      hints.allowObjects = true;
      hints.objectFilter = 'opponent';
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
      }
    } else if (target === 'opponent') {
      hints.allowPlayers = true;
      hints.playerFilter = 'opponent';
      if (limit) {
        hints.maxPlayerTargets = hints.maxPlayerTargets ? Math.min(hints.maxPlayerTargets, limit) : limit;
      }
    } else if (target.includes('player')) {
      hints.allowPlayers = true;
      if (limit) {
        hints.maxPlayerTargets = hints.maxPlayerTargets ? Math.min(hints.maxPlayerTargets, limit) : limit;
      }
    }
    const mapped = mapTargetToType(target);
    if (mapped) {
      hints.allowObjects = true;
      hints.objectTypes.add(mapped);
      if (limit) {
        hints.maxObjectTargets = hints.maxObjectTargets ? Math.min(hints.maxObjectTargets, limit) : limit;
      }
    }
  });

  if (!hints.allowPlayers && !hints.allowObjects) {
    return {
      allowPlayers: true,
      allowObjects: true,
      objectTypes: new Set(),
      maxObjectTargets: null,
      maxPlayerTargets: null,
      playerFilter: 'any',
      objectFilter: 'any',
    };
  }

  return hints;
};

export const deriveGlobalRequiredTargets = (
  graph?: any,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
): string[] => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  const effectNodes = filterEffectNodes(graph, modalConfig, selectedModes);
  const required = new Set<string>();
  effectNodes.forEach((node: any) => {
    deriveTargetSpecs(node?.data ?? {}).forEach((spec) => {
      if (spec.required && spec.key === 'target') {
        required.add('target');
      }
    });
  });
  return Array.from(required);
};

export const deriveGlobalDistinctTargets = (
  graph?: any,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
): string[] => {
  if (!graph || !Array.isArray(graph.nodes)) return [];
  const effectNodes = filterEffectNodes(graph, modalConfig, selectedModes);
  const distinct = new Set<string>();
  effectNodes.forEach((node: any) => {
    deriveTargetSpecs(node?.data ?? {}).forEach((spec) => {
      if (spec.distinct && spec.key === 'target') {
        distinct.add('target');
      }
    });
  });
  return Array.from(distinct);
};

export const deriveGlobalMinTargets = (
  graph?: any,
  modalConfig?: ModalChoiceConfig | null,
  selectedModes: string[] = []
): Record<string, number> => {
  if (!graph || !Array.isArray(graph.nodes)) return {};
  const effectNodes = filterEffectNodes(graph, modalConfig, selectedModes);
  const minTargets: Record<string, number> = {};
  effectNodes.forEach((node: any) => {
    deriveTargetSpecs(node?.data ?? {}).forEach((spec) => {
      if (spec.key === 'target' && typeof spec.minTargets === 'number') {
        minTargets.target = Math.max(minTargets.target ?? 0, spec.minTargets);
      }
    });
  });
  return minTargets;
};

