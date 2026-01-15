type TargetHints = {
  allowPlayers: boolean;
  allowObjects: boolean;
  objectTypes: Set<string>;
  maxObjectTargets: number | null;
  maxPlayerTargets: number | null;
};

const normalizeTarget = (value?: string) => (value || '').toLowerCase();

const mapTargetToType = (target: string) => {
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

export const deriveTargetHints = (graph?: any): TargetHints => {
  if (!graph || !Array.isArray(graph.nodes)) {
    return {
      allowPlayers: true,
      allowObjects: true,
      objectTypes: new Set(),
      maxObjectTargets: null,
      maxPlayerTargets: null,
    };
  }

  const hints: TargetHints = {
    allowPlayers: false,
    allowObjects: false,
    objectTypes: new Set(),
    maxObjectTargets: null,
    maxPlayerTargets: null,
  };
  const effectNodes = graph.nodes.filter((node: any) => node?.type === 'EFFECT');

  effectNodes.forEach((node: any) => {
    const target = normalizeTarget(node?.data?.target || node?.data?.targetType || '');
    const limit =
      parseLimit(node?.data?.maxTargets) ??
      parseLimit(node?.data?.max_targets) ??
      parseLimit(node?.data?.target_count);
    if (!target) return;

    if (target === 'any' || target === 'target' || target.includes('permanent')) {
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
    if (target.includes('player')) {
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
    };
  }

  return hints;
};

