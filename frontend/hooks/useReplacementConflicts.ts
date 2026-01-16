import { useMemo } from 'react';
import { EngineGameStateSnapshot } from '@/lib/engine';
import { hasFirstStrikeCombat, isEligibleForCombatPass } from '@/lib/combatDamage';

const ZONE_LABELS: Record<string, string> = {
  battlefield: 'Battlefield',
  graveyard: 'Graveyard',
  hand: 'Hand',
  library: 'Library',
  exile: 'Exile',
  command: 'Command',
  stack: 'Stack',
};

export interface ReplacementConflictEntry {
  key: string;
  label: string;
  options: Array<Record<string, any>>;
}

const formatPlayerLabel = (playerId?: number | null) =>
  typeof playerId === 'number' ? `Player ${playerId}` : 'Player';

const getPower = (obj: any) => Number(obj?.power ?? 0);

const hasKeyword = (obj: any, keyword: string) => Array.isArray(obj?.keywords) && obj.keywords.includes(keyword);

const lethalDamageRequired = (defender: any, deathtouch: boolean) => {
  if (defender?.toughness == null) return 0;
  if (deathtouch) return 1;
  const toughness = Number(defender.toughness ?? 0);
  const damage = Number(defender.damage ?? 0);
  return Math.max(0, toughness - damage);
};

const getNodePayload = (node: any) => {
  if (node?.type === 'ACTIVATED' && node?.data?.effect) return node.data.effect;
  return node?.data;
};

const graphHasDamageEffect = (graph: any) => {
  if (!graph?.nodes) return false;
  return graph.nodes.some((node: any) => getNodePayload(node)?.type === 'damage');
};

export const useReplacementConflicts = (gameState: EngineGameStateSnapshot | null) => {
  return useMemo(() => {
    if (!gameState) return [];
    const objectById = new Map(gameState.objects.map((obj) => [obj.id, obj]));
    const globalEffects = (gameState.replacement_effects ?? []).filter(
      (effect) => effect?.type === 'replace_zone_change'
    );
    const getZoneLabel = (zone?: string) => (zone ? ZONE_LABELS[zone] ?? zone : 'Any');
    const zoneConflicts = gameState.objects
      .map((obj) => {
        const localEffects = (obj as any).temporary_effects || [];
        const all = [...localEffects, ...globalEffects].filter((effect) => {
          if (effect?.type !== 'replace_zone_change') return false;
          if (effect.object_id && effect.object_id !== obj.id) return false;
          if (!effect.from_zone || !effect.to_zone) return false;
          return true;
        });
        if (all.length < 2) return null;
        const byKey = new Map<string, { key: string; fromZone: string; toZone: string; options: any[] }>();
        all.forEach((effect) => {
          const fromZone = effect.from_zone;
          const toZone = effect.to_zone;
          const key = `${obj.id}:${fromZone}:${toZone}`;
          const entry = byKey.get(key) || { key, fromZone, toZone, options: [] as any[] };
          entry.options.push(effect);
          byKey.set(key, entry);
        });
        return Array.from(byKey.values()).map((entry) => ({
          key: entry.key,
          label: `${obj.name || obj.id} (${getZoneLabel(entry.fromZone)} → ${getZoneLabel(entry.toZone)})`,
          options: entry.options.map((effect) => ({
            ...effect,
            label: effect.replacement_zone || 'Replacement',
          })),
        }));
      })
      .flat()
      .filter(Boolean) as ReplacementConflictEntry[];

    const redirectEffects = (gameState.replacement_effects ?? []).filter(
      (effect) => effect?.type === 'redirect_damage'
    );
    const redirectConflicts = redirectEffects
      .reduce((acc, effect) => {
        const sourceId = effect.source;
        if (!sourceId) return acc;
        const key = `damage:redirect:${sourceId}`;
        const entry = acc.get(key) || { key, sourceId, options: [] as any[] };
        entry.options.push(effect);
        acc.set(key, entry);
        return acc;
      }, new Map<string, { key: string; sourceId: string; options: any[] }>())
      .values();

    const preventPlayerConflicts = (gameState.replacement_effects ?? [])
      .filter((effect) => effect?.type === 'prevent_damage' && effect.player_id != null)
      .reduce((acc, effect) => {
        const playerId = effect.player_id;
        const key = `damage:prevent:player:${playerId}`;
        const entry = acc.get(key) || { key, playerId, options: [] as any[] };
        entry.options.push(effect);
        acc.set(key, entry);
        return acc;
      }, new Map<string, { key: string; playerId: number; options: any[] }>())
      .values();

    const preventObjectConflicts = gameState.objects
      .map((obj) => {
        const effects = (obj as any).temporary_effects || [];
        const preventEffects = effects.filter((effect: any) => effect?.prevent_damage != null);
        if (preventEffects.length < 2) return null;
        return {
          key: `damage:prevent:object:${obj.id}`,
          objectId: obj.id,
          options: preventEffects,
        };
      })
      .filter(Boolean) as Array<{ key: string; objectId: string; options: any[] }>;

    const damageConflicts: ReplacementConflictEntry[] = [];
    for (const entry of Array.from(redirectConflicts)) {
      if (entry.options.length < 2) continue;
      const source = objectById.get(entry.sourceId);
      damageConflicts.push({
        key: entry.key,
        label: `Redirect damage from ${source?.name || entry.sourceId}`,
        options: entry.options.map((effect) => {
          const redirectId = effect.redirect;
          const redirectPlayerId = effect.redirect_player_id;
          const redirectObject = redirectId ? objectById.get(redirectId) : null;
          const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
          return {
            ...effect,
            label: `→ ${targetLabel}`,
          };
        }),
      });
    }

    for (const entry of Array.from(preventPlayerConflicts)) {
      if (entry.options.length < 2) continue;
      damageConflicts.push({
        key: entry.key,
        label: `Prevent damage to ${formatPlayerLabel(entry.playerId)}`,
        options: entry.options.map((effect) => ({
          ...effect,
          label: `Prevent ${effect.amount ?? effect.prevent_damage ?? 'damage'}`,
        })),
      });
    }

    for (const entry of preventObjectConflicts) {
      if (entry.options.length < 2) continue;
      const obj = objectById.get(entry.objectId);
      damageConflicts.push({
        key: entry.key,
        label: `Prevent damage to ${obj?.name || entry.objectId}`,
        options: entry.options.map((effect) => ({
          ...effect,
          label: `Prevent ${effect.prevent_damage ?? effect.amount ?? 'damage'}`,
        })),
      });
    }

    const stackDamageConflicts: ReplacementConflictEntry[] = [];
    (gameState.stack ?? []).forEach((item: any) => {
      if (item.kind !== 'ability_graph') return;
      const graph = item.payload?.graph;
      if (!graphHasDamageEffect(graph)) return;
      const context = item.payload?.context || {};
      const targets = context.targets || {};
      const sourceId = item.payload?.source_object_id || context.source_id;
      if (!sourceId) return;
      const source = objectById.get(sourceId);
      const redirectOptions = redirectEffects.filter((effect) => effect.source === sourceId);
      const targetObjects: string[] = [];
      const targetPlayers: number[] = [];
      if (targets.target) targetObjects.push(targets.target);
      if (Array.isArray(targets.targets)) targetObjects.push(...targets.targets);
      if (typeof targets.target_player === 'number') targetPlayers.push(targets.target_player);
      if (Array.isArray(targets.target_players)) targetPlayers.push(...targets.target_players);

      targetObjects.forEach((targetId) => {
        const target = objectById.get(targetId);
        const preventOptions = (target as any)?.temporary_effects?.filter(
          (effect: any) => effect?.prevent_damage != null
        ) ?? [];
        const options = [
          ...redirectOptions.map((effect) => {
            const redirectId = effect.redirect;
            const redirectPlayerId = effect.redirect_player_id;
            const redirectObject = redirectId ? objectById.get(redirectId) : null;
            const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
            return { ...effect, label: `Redirect → ${targetLabel}` };
          }),
          ...preventOptions.map((effect: any) => ({
            ...effect,
            label: `Prevent ${effect.prevent_damage ?? effect.amount ?? 'damage'}`,
          })),
        ];
        if (options.length < 2) return;
        stackDamageConflicts.push({
          key: `damage:event:${sourceId}:object:${targetId}`,
          label: `Damage from ${source?.name || sourceId} to ${target?.name || targetId}`,
          options,
        });
      });

      targetPlayers.forEach((playerId) => {
        const preventOptions = (gameState.replacement_effects ?? []).filter(
          (effect) => effect?.type === 'prevent_damage' && effect.player_id === playerId
        );
        const options = [
          ...redirectOptions.map((effect) => {
            const redirectId = effect.redirect;
            const redirectPlayerId = effect.redirect_player_id;
            const redirectObject = redirectId ? objectById.get(redirectId) : null;
            const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
            return { ...effect, label: `Redirect → ${targetLabel}` };
          }),
          ...preventOptions.map((effect) => ({
            ...effect,
            label: `Prevent ${effect.amount ?? effect.prevent_damage ?? 'damage'}`,
          })),
        ];
        if (options.length < 2) return;
        stackDamageConflicts.push({
          key: `damage:event:${sourceId}:player:${playerId}`,
          label: `Damage from ${source?.name || sourceId} to ${formatPlayerLabel(playerId)}`,
          options,
        });
      });
    });

    const combatDamageConflicts: ReplacementConflictEntry[] = [];
    if (gameState.turn?.step === 'combat_damage' && gameState.turn?.combat_state) {
      const combatState = gameState.turn.combat_state;
      const defendingPlayerId = combatState.defending_player_id;
      const combatPass = hasFirstStrikeCombat(gameState)
        ? combatState.first_strike_resolved
          ? 'regular'
          : 'first_strike'
        : null;
      (combatState.attackers || []).forEach((attackerId: string) => {
        const attacker = objectById.get(attackerId);
        if (!attacker) return;
        if (!isEligibleForCombatPass(attacker.keywords, combatPass ?? undefined)) return;
        const blockers = (combatState.blockers?.[attackerId] || [])
          .map((blockerId: string) => objectById.get(blockerId))
          .filter(Boolean) as any[];
        if (blockers.length === 0 && typeof defendingPlayerId === 'number') {
          const redirectOptions = redirectEffects.filter((effect) => effect.source === attackerId);
          const preventOptions = (gameState.replacement_effects ?? []).filter(
            (effect) => effect?.type === 'prevent_damage' && effect.player_id === defendingPlayerId
          );
          const options = [
            ...redirectOptions.map((effect) => {
              const redirectId = effect.redirect;
              const redirectPlayerId = effect.redirect_player_id;
              const redirectObject = redirectId ? objectById.get(redirectId) : null;
              const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
              return { ...effect, label: `Redirect → ${targetLabel}` };
            }),
            ...preventOptions.map((effect) => ({
              ...effect,
              label: `Prevent ${effect.amount ?? effect.prevent_damage ?? 'damage'}`,
            })),
          ];
          if (options.length >= 2) {
            combatDamageConflicts.push({
              key: `damage:event:${attackerId}:player:${defendingPlayerId}`,
              label: `Combat damage: ${attacker.name || attackerId} → ${formatPlayerLabel(defendingPlayerId)}`,
              options,
            });
          }
        } else {
          const redirectOptions = redirectEffects.filter((effect) => effect.source === attackerId);
          const attackerDeathtouch = hasKeyword(attacker, 'Deathtouch');
          let remaining = getPower(attacker);
          blockers.forEach((blocker: any, index: number) => {
            if (!isEligibleForCombatPass(blocker?.keywords, combatPass ?? undefined)) return;
            const preventOptions =
              (blocker as any)?.temporary_effects?.filter((effect: any) => effect?.prevent_damage != null) ?? [];
            const options = [
              ...redirectOptions.map((effect) => {
                const redirectId = effect.redirect;
                const redirectPlayerId = effect.redirect_player_id;
                const redirectObject = redirectId ? objectById.get(redirectId) : null;
                const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
                return { ...effect, label: `Redirect → ${targetLabel}` };
              }),
              ...preventOptions.map((effect: any) => ({
                ...effect,
                label: `Prevent ${effect.prevent_damage ?? effect.amount ?? 'damage'}`,
              })),
            ];
            if (options.length >= 2) {
              combatDamageConflicts.push({
                key: `damage:event:${attackerId}:object:${blocker.id}`,
                label: `Combat damage (order ${index + 1}): ${attacker.name || attackerId} → ${blocker.name || blocker.id}`,
                options,
              });
            }

            const lethal = lethalDamageRequired(blocker, attackerDeathtouch);
            const assign = lethal === 0 ? remaining : Math.min(remaining, lethal);
            remaining -= Math.max(0, assign);
          });

          if (hasKeyword(attacker, 'Trample') && remaining > 0 && typeof defendingPlayerId === 'number') {
            const preventOptions = (gameState.replacement_effects ?? []).filter(
              (effect) => effect?.type === 'prevent_damage' && effect.player_id === defendingPlayerId
            );
            const options = [
              ...redirectOptions.map((effect) => {
                const redirectId = effect.redirect;
                const redirectPlayerId = effect.redirect_player_id;
                const redirectObject = redirectId ? objectById.get(redirectId) : null;
                const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
                return { ...effect, label: `Redirect → ${targetLabel}` };
              }),
              ...preventOptions.map((effect) => ({
                ...effect,
                label: `Prevent ${effect.amount ?? effect.prevent_damage ?? 'damage'}`,
              })),
            ];
            if (options.length >= 2) {
              combatDamageConflicts.push({
                key: `damage:event:${attackerId}:player:${defendingPlayerId}`,
                label: `Combat damage (trample): ${attacker.name || attackerId} → ${formatPlayerLabel(
                  defendingPlayerId
                )}`,
                options,
              });
            }
          }

          blockers.forEach((blocker: any) => {
            if (!isEligibleForCombatPass(blocker?.keywords, combatPass ?? undefined)) return;
            const blockerRedirectOptions = redirectEffects.filter((effect) => effect.source === blocker.id);
            const attackerPreventOptions =
              (attacker as any)?.temporary_effects?.filter((effect: any) => effect?.prevent_damage != null) ?? [];
            const blockerOptions = [
              ...blockerRedirectOptions.map((effect) => {
                const redirectId = effect.redirect;
                const redirectPlayerId = effect.redirect_player_id;
                const redirectObject = redirectId ? objectById.get(redirectId) : null;
                const targetLabel = redirectObject?.name || formatPlayerLabel(redirectPlayerId);
                return { ...effect, label: `Redirect → ${targetLabel}` };
              }),
              ...attackerPreventOptions.map((effect: any) => ({
                ...effect,
                label: `Prevent ${effect.prevent_damage ?? effect.amount ?? 'damage'}`,
              })),
            ];
            if (blockerOptions.length >= 2) {
              combatDamageConflicts.push({
                key: `damage:event:${blocker.id}:object:${attackerId}`,
                label: `Combat damage (blocker): ${blocker.name || blocker.id} → ${attacker.name || attackerId}`,
                options: blockerOptions,
              });
            }
          });
        }
      });
    }

    return [...zoneConflicts, ...damageConflicts, ...stackDamageConflicts, ...combatDamageConflicts];
  }, [gameState]);
};

