import { EngineGameObjectSnapshot, EngineGameStateSnapshot } from '@/lib/engine';

type SearchEffect = {
  cardType?: string;
  manaValueComparison?: string;
  manaValueComparisonSource?: string;
  manaValueComparisonValue?: number;
  differentName?: boolean | {
    enabled: boolean;
    compareAgainstType?: string;
    compareAgainstZone?: string;
    compareAgainstSource?: string;
  };
};

const normalizeCardType = (value?: string) => {
  if (!value) return undefined;
  const lowered = value.trim().toLowerCase();
  const mapping: Record<string, string> = {
    creature: 'Creature',
    artifact: 'Artifact',
    enchantment: 'Enchantment',
    aura: 'Aura',
    equipment: 'Equipment',
    land: 'Land',
    planeswalker: 'Planeswalker',
    instant: 'Instant',
    sorcery: 'Sorcery',
    battle: 'Battle',
    tribal: 'Tribal',
    legendary: 'Legendary',
  };
  return mapping[lowered] ?? value;
};

/**
 * Check if object matches card type (including subtypes like Aura, Equipment).
 * "Aura" is a subtype found in type_line (e.g., "Enchantment — Aura"), not in types.
 */
const matchesCardTypeOrSubtype = (obj: EngineGameObjectSnapshot, cardType: string) => {
  // Check types array first
  if ((obj.types ?? []).includes(cardType)) return true;
  
  // Check type_line for subtypes (e.g., "Enchantment — Aura")
  if (obj.type_line) {
    const typeLine = obj.type_line.toLowerCase();
    const cardTypeLower = cardType.toLowerCase();
    // Parse type_line, split by em-dash or regular dash
    const parts = typeLine.replace(/—/g, '-').replace(/–/g, '-').split('-');
    for (const part of parts) {
      for (const word of part.trim().split(/\s+/)) {
        if (word === cardTypeLower) return true;
      }
    }
  }
  return false;
};

const compareManaValue = (value: number | null | undefined, op?: string, compareValue?: number | null) => {
  if (!op || compareValue === null || compareValue === undefined) return true;
  if (value === null || value === undefined) return false;
  if (op === '<=') return value <= compareValue;
  if (op === '<') return value < compareValue;
  if (op === '>=') return value >= compareValue;
  if (op === '>') return value > compareValue;
  if (op === '==') return value === compareValue;
  return true;
};

const getCompareNames = (
  gameState: EngineGameStateSnapshot,
  playerId: number,
  compareAgainstType?: string,
  compareAgainstZone?: string,
  compareAgainstSource?: string,
  context?: {
    sourceId?: string | null;
    triggeringSourceId?: string | null;
    triggeringAuraId?: string | null;
    triggeringSpellId?: string | null;
    targetId?: string | null;
  }
) => {
  const names = new Set<string>();
  const normalizedType = compareAgainstType && compareAgainstType !== 'any' ? normalizeCardType(compareAgainstType) : undefined;
  const player = gameState.players.find((entry) => entry.id === playerId);
  if (!player) return names;
  let candidates: string[] = [];
  if (compareAgainstSource) {
    const resolved =
      compareAgainstSource === 'triggering_source'
        ? context?.triggeringSourceId
        : compareAgainstSource === 'triggering_aura'
          ? context?.triggeringAuraId ?? context?.triggeringSourceId
          : compareAgainstSource === 'triggering_spell'
            ? context?.triggeringSpellId ?? context?.triggeringSourceId
            : compareAgainstSource === 'source'
              ? context?.sourceId
              : compareAgainstSource === 'target'
                ? context?.targetId
                : undefined;
    if (resolved) {
      candidates = [resolved];
    }
  }
  if (candidates.length === 0 && compareAgainstZone === 'controlled') {
    candidates = gameState.objects
      .filter((obj) => obj.zone === 'battlefield' && obj.controller_id === playerId)
      .map((obj) => obj.id);
  } else if (candidates.length === 0 && compareAgainstZone === 'battlefield') {
    candidates = gameState.objects.filter((obj) => obj.zone === 'battlefield').map((obj) => obj.id);
  } else if (candidates.length === 0 && compareAgainstZone && compareAgainstZone !== 'controlled') {
    const zoneList = (player as any)[compareAgainstZone] as string[] | undefined;
    if (Array.isArray(zoneList)) candidates = zoneList;
  }
  candidates.forEach((id) => {
    const obj = gameState.objects.find((entry) => entry.id === id);
    if (!obj) return;
    if (normalizedType && !matchesCardTypeOrSubtype(obj, normalizedType)) return;
    if (obj.name) names.add(obj.name);
  });
  return names;
};

export const filterSearchCandidates = (
  gameState: EngineGameStateSnapshot,
  effect: SearchEffect,
  playerId: number,
  pool: string[],
  context?: {
    sourceId?: string | null;
    triggeringSourceId?: string | null;
    triggeringAuraId?: string | null;
    triggeringSpellId?: string | null;
    targetId?: string | null;
  }
) => {
  const cardType = effect.cardType && effect.cardType !== 'any' ? normalizeCardType(effect.cardType) : undefined;
  const compareOp = effect.manaValueComparison;
  const compareSource = effect.manaValueComparisonSource;
  const compareValue =
    compareSource && compareSource !== 'fixed_value' ? null : effect.manaValueComparisonValue ?? null;

  const differentName = effect.differentName;
  const differentConfig =
    typeof differentName === 'object'
      ? differentName.enabled
        ? differentName
        : null
      : differentName
      ? { enabled: true }
      : null;
  const compareNames = differentConfig
    ? getCompareNames(
        gameState,
        playerId,
        differentConfig.compareAgainstType,
        differentConfig.compareAgainstZone ?? 'controlled',
        differentConfig.compareAgainstSource,
        context
      )
    : new Set<string>();

  return pool.filter((id) => {
    const obj = gameState.objects.find((entry) => entry.id === id);
    if (!obj) return false;
    if (cardType && !matchesCardTypeOrSubtype(obj, cardType)) return false;
    if (!compareManaValue(obj.mana_value ?? null, compareOp, compareValue)) return false;
    if (compareNames.size > 0 && obj.name && compareNames.has(obj.name)) return false;
    return true;
  });
};

export const resolvePlayerIdsForEffect = (
  effectTarget: string | undefined,
  gameState: EngineGameStateSnapshot,
  controllerId: number | null
) => {
  const target = (effectTarget ?? 'player').toLowerCase();
  const all = gameState.players.map((player) => player.id);
  if (target === 'each_player' || target === 'all_players') return all;
  if (target === 'each_opponent' || target === 'opponents') {
    return controllerId === null ? all : all.filter((id) => id !== controllerId);
  }
  if (target === 'opponent') {
    return controllerId === null ? all : all.filter((id) => id !== controllerId);
  }
  return controllerId === null ? [] : [controllerId];
};

