import type { OrbType } from "@/game/types";

export const baseSpawnIntervalMs = 850;
export const projectileSpeed = 500;
export const outOfBoundsMargin = 48;
export const playerRadius = 12;
export const laserWarningMs = 1700;
export const laserFiringMs = 350;

export const orbConfig: Record<
  OrbType,
  { speed: [number, number]; radius: [number, number]; damage: number; hp: number }
> = {
  normal: { speed: [45, 125], radius: [8, 16], damage: 1, hp: 1 },
  fast: { speed: [140, 200], radius: [5, 8], damage: 1, hp: 1 },
  slow: { speed: [28, 45], radius: [18, 28], damage: 2, hp: 3 },
  splitting: { speed: [55, 90], radius: [12, 16], damage: 1, hp: 2 },
  homing: { speed: [35, 60], radius: [10, 14], damage: 1, hp: 2 },
  phasing: { speed: [45, 80], radius: [10, 14], damage: 1, hp: 2 },
};

export const monsterColors: Record<OrbType, string> = {
  normal: "#cfa27d",
  fast: "#e2b385",
  slow: "#8b4049",
  splitting: "#6a8a85",
  homing: "#c27a7a",
  phasing: "#8f8876",
};

export const enemyProjectileColor = "#8b4049";
export const enemyProjectileSpeed = 110;
export const enemyProjectileRadius = 4.5;
export const enemyProjectileDamage = 1;

export const orbShootConfig: Partial<
  Record<
    OrbType,
    {
      cooldown: [number, number];
      mode: "single" | "spread";
      count: number;
      spreadDeg: number;
      projectileSpeed?: number;
    }
  >
> = {
  normal: { cooldown: [1800, 2600], mode: "single", count: 1, spreadDeg: 0 },
  slow: { cooldown: [2400, 3200], mode: "spread", count: 3, spreadDeg: 14 },
  splitting: { cooldown: [2200, 3000], mode: "spread", count: 2, spreadDeg: 10 },
  homing: { cooldown: [2000, 2800], mode: "single", count: 1, spreadDeg: 0, projectileSpeed: 200 },
  phasing: { cooldown: [2800, 3600], mode: "single", count: 1, spreadDeg: 0 },
};

export const bossShootConfig = {
  cooldown: [900, 1400],
  count: 1,
  spreadDeg: 0,
  speed: 300,
};

export const orbWeights: Array<{ type: OrbType; weight: number }> = [
  { type: "normal", weight: 40 },
  { type: "fast", weight: 20 },
  { type: "slow", weight: 15 },
  { type: "splitting", weight: 10 },
  { type: "homing", weight: 10 },
  { type: "phasing", weight: 5 },
];
