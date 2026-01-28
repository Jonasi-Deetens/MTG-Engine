import type { Bounds, OrbEntity, OrbType } from "@/game/types";
import { orbConfig, orbShootConfig, orbWeights } from "@/game/config";
import { normalize, randomBetween, weightedPick } from "@/game/utils";

export const getOrbWeights = (difficulty: number) =>
  orbWeights.map((entry) => {
    if (entry.type === "normal") {
      return { ...entry, weight: Math.max(15, entry.weight - difficulty * 20) };
    }
    if (entry.type === "phasing") {
      return { ...entry, weight: entry.weight + difficulty * 6 };
    }
    if (entry.type === "homing") {
      return { ...entry, weight: entry.weight + difficulty * 6 };
    }
    if (entry.type === "splitting") {
      return { ...entry, weight: entry.weight + difficulty * 4 };
    }
    if (entry.type === "fast") {
      return { ...entry, weight: entry.weight + difficulty * 4 };
    }
    if (entry.type === "slow") {
      return { ...entry, weight: entry.weight + difficulty * 2 };
    }
    return entry;
  });

export const spawnFromEdge = (bounds: Bounds, radius: number) => {
  const edge = Math.floor(Math.random() * 4);
  let position = { x: 0, y: 0 };
  let direction = { x: 0, y: 0 };

  if (edge === 0) {
    position = { x: Math.random() * bounds.width, y: -radius };
    direction = { x: randomBetween(-0.4, 0.4), y: 1 };
  } else if (edge === 1) {
    position = { x: bounds.width + radius, y: Math.random() * bounds.height };
    direction = { x: -1, y: randomBetween(-0.4, 0.4) };
  } else if (edge === 2) {
    position = { x: Math.random() * bounds.width, y: bounds.height + radius };
    direction = { x: randomBetween(-0.4, 0.4), y: -1 };
  } else {
    position = { x: -radius, y: Math.random() * bounds.height };
    direction = { x: 1, y: randomBetween(-0.4, 0.4) };
  }

  return { position, direction: normalize(direction) };
};

export const createOrb = (
  bounds: Bounds,
  id: number,
  weights: Array<{ type: OrbType; weight: number }> = orbWeights
): OrbEntity => {
  const type = weightedPick(weights);
  const config = orbConfig[type];
  const radius = randomBetween(config.radius[0], config.radius[1]);
  const { position, direction } = spawnFromEdge(bounds, radius);
  const speed = randomBetween(config.speed[0], config.speed[1]);

  return {
    id,
    type,
    position,
    velocity: { x: direction.x * speed, y: direction.y * speed },
    radius,
    hp: config.hp,
    maxHp: config.hp,
    damage: config.damage,
    isPhasing: type === "phasing" ? false : undefined,
    phaseTimerMs: type === "phasing" ? randomBetween(350, 650) : undefined,
    shootCooldownMs: orbShootConfig[type]
      ? randomBetween(
          orbShootConfig[type]?.cooldown[0] ?? 1800,
          orbShootConfig[type]?.cooldown[1] ?? 2600
        )
      : undefined,
  };
};

export const createSplitOrb = (source: OrbEntity, id: number): OrbEntity => {
  const radius = randomBetween(6, 9);
  const direction = normalize({
    x: randomBetween(-1, 1),
    y: randomBetween(-1, 1),
  });
  const speed = randomBetween(100, 160);
  return {
    id,
    type: "fast",
    position: { ...source.position },
    velocity: { x: direction.x * speed, y: direction.y * speed },
    radius,
    hp: 1,
    maxHp: 1,
    damage: 1,
  };
};
