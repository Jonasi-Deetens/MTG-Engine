import { EngineGameStateSnapshot } from '@/lib/engine';

const getPower = (value?: number | null) => Number(value ?? 0);

const hasKeyword = (keywords: string[] | undefined, keyword: string) => Boolean(keywords?.includes(keyword));

export const isEligibleForCombatPass = (
  keywords: string[] | undefined,
  passType?: 'first_strike' | 'regular'
) => {
  if (!passType) return true;
  const hasFirst = hasKeyword(keywords, 'First strike');
  const hasDouble = hasKeyword(keywords, 'Double strike');
  if (passType === 'first_strike') return hasFirst || hasDouble;
  return !hasFirst || hasDouble;
};

const lethalDamageRequired = (toughness?: number | null, damage?: number | null, deathtouch?: boolean) => {
  if (toughness == null) return 0;
  if (deathtouch) return 1;
  return Math.max(0, Number(toughness) - Number(damage ?? 0));
};

export const hasFirstStrikeCombat = (gameState: EngineGameStateSnapshot | null) => {
  if (!gameState?.turn?.combat_state) return false;
  const combatState = gameState.turn.combat_state;
  const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
  return combatState.attackers.some((attackerId) => {
    const attacker = objectMap.get(attackerId);
    if (hasKeyword(attacker?.keywords, 'First strike') || hasKeyword(attacker?.keywords, 'Double strike')) {
      return true;
    }
    return (combatState.blockers?.[attackerId] || []).some((blockerId) => {
      const blocker = objectMap.get(blockerId);
      return hasKeyword(blocker?.keywords, 'First strike') || hasKeyword(blocker?.keywords, 'Double strike');
    });
  });
};

export const buildDefaultCombatAssignments = (
  gameState: EngineGameStateSnapshot,
  passType?: 'first_strike' | 'regular'
) => {
  const combatState = gameState.turn.combat_state;
  if (!combatState) return {};
  const objectMap = new Map(gameState.objects.map((obj) => [obj.id, obj]));
  const assignments: Record<string, Record<string, number>> = {};
  const defendingPlayerId = combatState.defending_player_id;
  const defendingObjectId = combatState.defending_object_id;

  combatState.attackers.forEach((attackerId) => {
    const attacker = objectMap.get(attackerId);
    if (!attacker) return;
    if (attacker.zone !== 'battlefield' || !attacker.is_attacking) return;
    if (!isEligibleForCombatPass(attacker.keywords, passType)) return;
    const blockers = (combatState.blockers?.[attackerId] || [])
      .map((blockerId) => objectMap.get(blockerId))
      .filter(Boolean);
    const attackerPower = getPower(attacker.power);
    const perAttacker: Record<string, number> = {};

    if (blockers.length === 0) {
      if (attackerPower > 0) {
        if (defendingObjectId) {
          perAttacker.defender = attackerPower;
        } else if (typeof defendingPlayerId === 'number') {
          perAttacker.player = attackerPower;
        }
      }
    } else {
      let remaining = attackerPower;
      const deathtouch = hasKeyword(attacker.keywords, 'Deathtouch');
      blockers.forEach((blocker) => {
        if (!blocker || remaining <= 0) return;
        const lethal = lethalDamageRequired(blocker.toughness, blocker.damage, deathtouch);
        const assign = lethal === 0 ? remaining : Math.min(remaining, lethal);
        if (assign > 0) {
          perAttacker[blocker.id] = assign;
          remaining -= assign;
        }
      });
      if (remaining > 0 && hasKeyword(attacker.keywords, 'Trample')) {
        if (defendingObjectId) {
          perAttacker.defender = remaining;
        } else if (typeof defendingPlayerId === 'number') {
          perAttacker.player = remaining;
        }
      }
    }

    if (Object.keys(perAttacker).length > 0) {
      assignments[attackerId] = perAttacker;
    }
  });

  return assignments;
};

