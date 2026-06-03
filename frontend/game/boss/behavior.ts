import type { Bounds, Vector2 } from "@/game/types";
import type { BossAttackState, BossAttackType, BossEntity, BossPhase } from "@/game/boss/types";
import {
  ascendedBossConfig,
  ascendedPhaseAttacks,
  bossBaseConfig,
  bossDeathConfig,
  bossPhaseAttacks,
} from "@/game/boss/config";
import type { BossAttackPreset } from "@/game/boss/patterns";
import {
  getCircularVelocities,
  getCrossVelocities,
  getSpreadVelocities,
  getSpiralVelocities,
} from "@/game/boss/patterns";
import { bossShootConfig } from "@/game/config";
import { clamp, normalize, randomBetween } from "@/game/utils";

export type BossAttackEvent =
  | { type: "projectiles"; origin: Vector2; velocities: Vector2[] }
  | {
      type: "laser";
      axis: "horizontal" | "vertical";
      position: number;
      warningMs: number;
      firingMs: number;
    };

export const getBossProjectiles = (origin: Vector2, velocities: Vector2[]): BossAttackEvent => ({
  type: "projectiles",
  origin,
  velocities,
});

type ActiveBossPhase = Exclude<BossPhase, "transition" | "defeated" | "dying" | "ascending">;

const pickAttackPreset = (
  phase: ActiveBossPhase,
  current?: BossAttackType,
  isAscended = false
) => {
  const pool = isAscended ? ascendedPhaseAttacks[phase] : bossPhaseAttacks[phase];
  const options = pool.filter((preset) => preset.type !== current);
  return options.length ? options[Math.floor(Math.random() * options.length)] : pool[0];
};

const createAttackState = (
  phase: ActiveBossPhase,
  preferred?: BossAttackType,
  isAscended = false
): BossAttackState => {
  const pool = isAscended ? ascendedPhaseAttacks[phase] : bossPhaseAttacks[phase];
  const preset = pool.find((entry) => entry.type === preferred) ?? pickAttackPreset(phase, undefined, isAscended);
  const cooldownMs = randomBetween(preset.cooldown[0], preset.cooldown[1]);
  return {
    type: preset.type,
    cooldownMs,
    timerMs: randomBetween(500, 900),
    spiralAngle: 0,
    spiralStepDeg: preset.spiralStepDeg,
  };
};

const getPresetForType = (
  phase: ActiveBossPhase,
  type: BossAttackType,
  isAscended = false
) => (isAscended ? ascendedPhaseAttacks[phase] : bossPhaseAttacks[phase]).find((entry) => entry.type === type);

export const createBoss = (bounds: Bounds, wave: number): BossEntity => {
  const maxHp = bossBaseConfig.baseHp + bossBaseConfig.hpPerWave * (wave - 1);
  const targetY = bounds.height * 0.18;
  const position = { x: bounds.width * 0.5, y: -bossBaseConfig.radius * 1.6 };
  const velocity = {
    x: randomBetween(-bossBaseConfig.speed, bossBaseConfig.speed),
    y: randomBetween(14, 28),
  };
  return {
    id: wave,
    position,
    velocity,
    radius: bossBaseConfig.radius,
    hp: maxHp,
    maxHp,
    phase: "ascending",
    attackState: createAttackState("phase1", undefined, false),
    transitionMs: 0,
    isInvulnerable: true,
    isAscended: false,
    shotCooldownMs: randomBetween(bossShootConfig.cooldown[0], bossShootConfig.cooldown[1]),
    deathTimerMs: bossDeathConfig.deathDurationMs,
    ascendTimerMs: bossBaseConfig.entryInvulnerableMs,
    spawnTargetY: targetY,
    spinAngle: 0,
    name: bossBaseConfig.name,
    wave,
  };
};

export const checkPhaseTransition = (boss: BossEntity): BossEntity => {
  if (boss.phase !== "phase1") return boss;
  if (boss.hp > boss.maxHp * 0.5) return boss;
  return {
    ...boss,
    phase: "transition",
    transitionMs: bossBaseConfig.transitionMs,
    attackState: createAttackState("phase2", undefined, boss.isAscended),
    isInvulnerable: true,
  };
};

const applyAttack = (
  boss: BossEntity,
  phase: ActiveBossPhase,
  playerPosition: Vector2,
  bounds: Bounds
): { events: BossAttackEvent[]; nextState: BossAttackState } => {
  const preset = getPresetForType(phase, boss.attackState.type, boss.isAscended);
  if (!preset) {
    return {
      events: [],
      nextState: createAttackState(phase, undefined),
    };
  }

  const baseDirection = normalize({
    x: playerPosition.x - boss.position.x,
    y: playerPosition.y - boss.position.y,
  });
  const speed = preset.speed ?? 240;
  const count = preset.count ?? 1;
  const events: BossAttackEvent[] = [];

  if (preset.type === "spread") {
    events.push(
      getBossProjectiles(
        boss.position,
        getSpreadVelocities(baseDirection, count, preset.spreadDeg ?? 20, speed)
      )
    );
  } else if (preset.type === "circular") {
    events.push(getBossProjectiles(boss.position, getCircularVelocities(count, speed)));
  } else if (preset.type === "aimed_burst") {
    events.push(
      getBossProjectiles(boss.position, getSpreadVelocities(baseDirection, 1, 0, speed))
    );
  } else if (preset.type === "double_spread") {
    events.push(
      getBossProjectiles(
        boss.position,
        getSpreadVelocities(baseDirection, count, preset.spreadDeg ?? 30, speed)
      )
    );
  } else if (preset.type === "spiral") {
    const { velocities, nextAngle } = getSpiralVelocities(
      count,
      speed,
      boss.attackState.spiralAngle ?? 0,
      preset.spiralStepDeg ?? 16
    );
    events.push(getBossProjectiles(boss.position, velocities));
    return {
      events,
      nextState: {
        ...boss.attackState,
        spiralAngle: nextAngle,
      },
    };
  } else if (preset.type === "laser_sweep") {
    const gridCount = Math.max(2, Math.round(preset.count ?? 3));
    const minRatio = 0.18;
    const maxRatio = 0.82;
    const xPositions = Array.from({ length: gridCount }, (_, index) => {
      const ratio = (index + 1) / (gridCount + 1);
      return clamp(bounds.width * ratio, bounds.width * minRatio, bounds.width * maxRatio);
    });
    const yPositions = Array.from({ length: gridCount }, (_, index) => {
      const ratio = (index + 1) / (gridCount + 1);
      return clamp(bounds.height * ratio, bounds.height * minRatio, bounds.height * maxRatio);
    });
    const warningMs = preset.laserWarningMs ?? 900;
    const firingMs = preset.laserFiringMs ?? 320;
    xPositions.forEach((position) => {
      events.push({ type: "laser", axis: "vertical", position, warningMs, firingMs });
    });
    yPositions.forEach((position) => {
      events.push({ type: "laser", axis: "horizontal", position, warningMs, firingMs });
    });
  } else if (preset.type === "cross_burst") {
    const rotation = Math.atan2(baseDirection.y, baseDirection.x);
    const includeDiagonals = (preset.count ?? 4) > 4;
    events.push(
      getBossProjectiles(
        boss.position,
        getCrossVelocities(speed, rotation, includeDiagonals)
      )
    );
  } else if (preset.type === "ring_burst") {
    const offset = boss.attackState.spiralAngle ?? 0;
    const { velocities, nextAngle } = getSpiralVelocities(
      count,
      speed,
      offset,
      preset.spiralStepDeg ?? 16
    );
    events.push(getBossProjectiles(boss.position, velocities));
    return {
      events,
      nextState: {
        ...boss.attackState,
        spiralAngle: nextAngle,
      },
    };
  } else if (preset.type === "fan_burst") {
    const spread = preset.spreadDeg ?? 24;
    const first = getSpreadVelocities(baseDirection, count, spread, speed);
    const offsetAngle = (spread * Math.PI) / 360;
    const offsetDirection = {
      x: Math.cos(Math.atan2(baseDirection.y, baseDirection.x) + offsetAngle),
      y: Math.sin(Math.atan2(baseDirection.y, baseDirection.x) + offsetAngle),
    };
    const second = getSpreadVelocities(offsetDirection, count, spread, speed);
    events.push(getBossProjectiles(boss.position, [...first, ...second]));
  }

  return { events, nextState: boss.attackState };
};

const advanceAttackState = (
  boss: BossEntity,
  phase: ActiveBossPhase,
  deltaMs: number,
  playerPosition: Vector2,
  bounds: Bounds
): { events: BossAttackEvent[]; nextState: BossAttackState } => {
  let timerMs = boss.attackState.timerMs - deltaMs;
  const events: BossAttackEvent[] = [];
  let nextState: BossAttackState = { ...boss.attackState, timerMs };

  if (boss.attackState.burstRemaining && boss.attackState.burstRemaining > 0) {
    if (timerMs <= 0) {
      const { events: burstEvents } = applyAttack(boss, phase, playerPosition, bounds);
      events.push(...burstEvents);
      const remaining = boss.attackState.burstRemaining - 1;
      if (remaining > 0) {
        nextState = {
          ...boss.attackState,
          burstRemaining: remaining,
          timerMs: boss.attackState.burstSpacingMs ?? 160,
        };
      } else {
        const nextPreset = pickAttackPreset(phase, boss.attackState.type, boss.isAscended);
        nextState = createAttackState(phase, nextPreset.type, boss.isAscended);
        nextState.timerMs = randomBetween(nextPreset.cooldown[0], nextPreset.cooldown[1]);
      }
    }
    return { events, nextState };
  }

  if (timerMs > 0) {
    return { events, nextState };
  }

  const { events: attackEvents, nextState: updatedState } = applyAttack(
    boss,
    phase,
    playerPosition,
    bounds
  );
  events.push(...attackEvents);

  const preset = getPresetForType(phase, boss.attackState.type, boss.isAscended);
  if (preset?.type === "aimed_burst") {
    const remaining = (preset.count ?? 3) - 1;
    nextState = {
      ...boss.attackState,
      burstRemaining: Math.max(0, remaining),
      burstSpacingMs: preset.burstSpacingMs ?? 180,
      timerMs: preset.burstSpacingMs ?? 180,
    };
  } else if (preset?.type === "double_spread") {
    nextState = {
      ...boss.attackState,
      burstRemaining: 1,
      burstSpacingMs: preset.burstSpacingMs ?? 200,
      timerMs: preset.burstSpacingMs ?? 200,
    };
  } else {
    const nextPreset = pickAttackPreset(phase, boss.attackState.type, boss.isAscended);
    nextState = createAttackState(phase, nextPreset.type, boss.isAscended);
    nextState.timerMs = randomBetween(nextPreset.cooldown[0], nextPreset.cooldown[1]);
  }

  return { events, nextState: { ...updatedState, ...nextState } };
};

export const updateBoss = (
  boss: BossEntity,
  deltaMs: number,
  bounds: Bounds,
  playerPosition: Vector2
): { boss: BossEntity; events: BossAttackEvent[] } => {
  const deltaSec = deltaMs / 1000;
  const hpRatio = boss.maxHp ? boss.hp / boss.maxHp : 1;
  const isDesperation = hpRatio <= 0.25;
  const baseAttackSpeedFactor = hpRatio <= 0.25 ? 1.8 : hpRatio <= 0.5 ? 1.35 : 1;
  const attackSpeedFactor = boss.isAscended
    ? baseAttackSpeedFactor * ascendedBossConfig.attackSpeedMultiplier
    : baseAttackSpeedFactor;
  const minY = bounds.height * bossBaseConfig.minYRatio;
  const maxY = bounds.height * bossBaseConfig.maxYRatio;
  const phaseSpeedFactor = boss.phase === "phase3" ? 1.75 : boss.phase === "phase2" ? 1.35 : 1;
  const baseSpeedFactor = boss.phase === "transition" ? 0.35 : phaseSpeedFactor;
  const speedFactor = boss.isAscended ? baseSpeedFactor * ascendedBossConfig.speedMultiplier : baseSpeedFactor;

  let nextVelocity = { ...boss.velocity };
  if (boss.phase === "phase3") {
    const toPlayer = normalize({
      x: playerPosition.x - boss.position.x,
      y: playerPosition.y - boss.position.y,
    });
    nextVelocity = {
      x: toPlayer.x * bossBaseConfig.chaseSpeed,
      y: toPlayer.y * bossBaseConfig.chaseSpeed,
    };
  }
  let nextPosition = {
    x: boss.position.x + nextVelocity.x * deltaSec * speedFactor,
    y: boss.position.y + nextVelocity.y * deltaSec * speedFactor,
  };

  if (nextPosition.x < boss.radius || nextPosition.x > bounds.width - boss.radius) {
    if (boss.phase !== "phase3") {
      nextVelocity.x *= -1;
    }
    nextPosition = {
      x: clamp(nextPosition.x, boss.radius, bounds.width - boss.radius),
      y: nextPosition.y,
    };
  }
  if (nextPosition.y < boss.radius + minY || nextPosition.y > maxY) {
    if (boss.phase !== "phase3") {
      nextVelocity.y *= -1;
    }
    nextPosition = {
      x: nextPosition.x,
      y: clamp(nextPosition.y, boss.radius + minY, maxY),
    };
  }

  let nextPhase = boss.phase;
  let transitionMs = boss.transitionMs;
  let attackState = boss.attackState;
  let isInvulnerable = boss.isInvulnerable;
  let shotCooldownMs = Number.isFinite(boss.shotCooldownMs)
    ? boss.shotCooldownMs - deltaMs * attackSpeedFactor
    : 0;
  let deathTimerMs = boss.deathTimerMs;
  let ascendTimerMs = boss.ascendTimerMs;
  let spinAngle = boss.spinAngle;
  const events: BossAttackEvent[] = [];

  if (boss.phase === "dying") {
    deathTimerMs = Math.max(0, boss.deathTimerMs - deltaMs);
    return {
      boss: {
        ...boss,
        position: nextPosition,
        velocity: nextVelocity,
        deathTimerMs,
      },
      events,
    };
  }

  if (boss.phase === "ascending") {
    if (boss.position.y < boss.spawnTargetY) {
      nextVelocity = { x: 0, y: bossBaseConfig.entrySpeed };
      nextPosition = {
        x: boss.position.x + nextVelocity.x * deltaSec,
        y: boss.position.y + nextVelocity.y * deltaSec,
      };
      if (nextPosition.y >= boss.spawnTargetY) {
        nextPosition.y = boss.spawnTargetY;
      }
    } else {
      ascendTimerMs = Math.max(0, boss.ascendTimerMs - deltaMs);
      if (ascendTimerMs === 0) {
        nextPhase = "phase1";
        attackState = createAttackState("phase1");
        isInvulnerable = false;
        nextVelocity = {
          x: randomBetween(-bossBaseConfig.speed, bossBaseConfig.speed),
          y: randomBetween(14, 28),
        };
      }
    }
    return {
      boss: {
        ...boss,
        position: nextPosition,
        velocity: nextVelocity,
        phase: nextPhase,
        attackState,
        isInvulnerable,
        ascendTimerMs,
      },
      events,
    };
  }

  if (boss.phase === "transition") {
    transitionMs = Math.max(0, boss.transitionMs - deltaMs);
    if (transitionMs === 0) {
      nextPhase = "phase2";
      attackState = createAttackState("phase2", boss.attackState.type);
      isInvulnerable = false;
      shotCooldownMs = randomBetween(
        bossShootConfig.cooldown[0],
        bossShootConfig.cooldown[1]
      );
    }
  } else if (boss.phase === "phase1" || boss.phase === "phase2" || boss.phase === "phase3") {
    const { events: attackEvents, nextState } = advanceAttackState(
      boss,
      boss.phase,
      deltaMs * attackSpeedFactor,
      playerPosition,
      bounds
    );
    events.push(...attackEvents);
    attackState = nextState;
  }

  if (nextPhase !== "transition" && nextPhase !== "phase3" && hpRatio <= 0.25) {
    nextPhase = "phase3";
    attackState = createAttackState("phase3", attackState.type);
  }

  if (boss.phase === "phase3") {
    spinAngle = (spinAngle + deltaSec * bossBaseConfig.spinSpeed) % (Math.PI * 2);
  }

  if (boss.phase !== "transition" && shotCooldownMs <= 0) {
    const baseDirection = normalize({
      x: playerPosition.x - boss.position.x,
      y: playerPosition.y - boss.position.y,
    });
    events.push(
      getBossProjectiles(
        boss.position,
        getSpreadVelocities(
          baseDirection,
          bossShootConfig.count,
          bossShootConfig.spreadDeg,
          bossShootConfig.speed
        )
      )
    );
    shotCooldownMs = randomBetween(
      bossShootConfig.cooldown[0],
      bossShootConfig.cooldown[1]
    );
  }

  return {
    boss: {
      ...boss,
      position: nextPosition,
      velocity: nextVelocity,
      phase: nextPhase,
      transitionMs,
      attackState,
      isInvulnerable,
      shotCooldownMs,
      deathTimerMs,
      ascendTimerMs,
      spinAngle,
    },
    events,
  };
};
