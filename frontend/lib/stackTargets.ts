import { EngineGameObjectSnapshot, EngineStackItemSnapshot } from '@/lib/engine';

const stableStringify = (value: unknown): string => {
  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(',')}]`;
  }
  if (value && typeof value === 'object') {
    const entries = Object.entries(value as Record<string, unknown>).sort(([a], [b]) => a.localeCompare(b));
    return `{${entries.map(([key, val]) => `${key}:${stableStringify(val)}`).join(',')}}`;
  }
  return JSON.stringify(value);
};

export const buildStackTargetHash = (
  item: EngineStackItemSnapshot,
  objectMap: Map<string, EngineGameObjectSnapshot>,
  stack: EngineStackItemSnapshot[]
): string => {
  const context = item.payload?.context as Record<string, unknown> | undefined;
  const targets = (context?.targets as Record<string, unknown>) || {};
  const targetIds = [
    ...(Array.isArray(targets.targets) ? targets.targets : targets.target ? [targets.target] : []),
    ...(Array.isArray(targets.spell_targets) ? targets.spell_targets : targets.spell_target ? [targets.spell_target] : []),
  ].filter(Boolean) as string[];
  const targetZones = targetIds.map((id) => ({ id, zone: objectMap.get(id)?.zone ?? 'unknown' }));
  const stackSpellIds = stack
    .filter((entry) => entry.kind === 'spell')
    .map((entry) => entry.payload?.object_id)
    .filter((id): id is string => Boolean(id));

  return stableStringify({
    kind: item.kind,
    controller: item.controller_id ?? null,
    targets: context?.targets ?? null,
    choices: context?.choices ?? null,
    source_id: context?.source_id ?? null,
    targetZones,
    stackSpellIds,
  });
};

