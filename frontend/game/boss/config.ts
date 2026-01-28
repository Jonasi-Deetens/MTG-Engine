import type { BossAttackPreset } from "@/game/boss/patterns";
import type { BossPhase } from "@/game/boss/types";

export const bossBaseConfig = {
  name: "UNIT-01",
  baseHp: 140,
  hpPerWave: 40,
  radius: 56,
  speed: 72,
  chaseSpeed: 62,
  spinSpeed: 6.5,
  entrySpeed: 120,
  entryInvulnerableMs: 2000,
  minYRatio: 0.12,
  maxYRatio: 0.48,
  transitionMs: 1400,
};

export const bossDeathConfig = {
  deathDurationMs: 1200,
  ascendDurationMs: 1600,
  rewardRadius: 18,
};

export const ascendedBossConfig = {
  hpMultiplier: 1.5,
  speedMultiplier: 1.2,
  attackSpeedMultiplier: 1.3,
};

export const bossProjectileConfig = {
  radius: 4.5,
  damage: 1,
};

export const bossPhaseAttacks: Record<
  Exclude<BossPhase, "transition" | "defeated" | "dying" | "ascending">,
  BossAttackPreset[]
> = {
  phase1: [
    {
      type: "spread",
      cooldown: [1600, 2300],
      count: 7,
      spreadDeg: 28,
      speed: 260,
    },
    {
      type: "circular",
      cooldown: [2700, 3600],
      count: 14,
      speed: 220,
    },
    {
      type: "aimed_burst",
      cooldown: [2200, 3100],
      count: 3,
      burstSpacingMs: 140,
      speed: 300,
    },
  ],
  phase2: [
    {
      type: "spiral",
      cooldown: [2200, 3000],
      count: 16,
      spiralStepDeg: 18,
      speed: 230,
    },
    {
      type: "double_spread",
      cooldown: [1600, 2300],
      count: 6,
      spreadDeg: 34,
      burstSpacingMs: 150,
      speed: 280,
    },
    {
      type: "laser_sweep",
      cooldown: [3400, 4800],
      count: 3,
      laserWarningMs: 800,
      laserFiringMs: 320,
    },
    {
      type: "aimed_burst",
      cooldown: [1800, 2500],
      count: 5,
      burstSpacingMs: 110,
      speed: 320,
    },
  ],
  phase3: [
    {
      type: "spiral",
      cooldown: [2000, 2800],
      count: 18,
      spiralStepDeg: 16,
      speed: 250,
    },
    {
      type: "double_spread",
      cooldown: [1500, 2100],
      count: 7,
      spreadDeg: 36,
      burstSpacingMs: 140,
      speed: 300,
    },
    {
      type: "laser_sweep",
      cooldown: [3000, 4200],
      count: 4,
      laserWarningMs: 700,
      laserFiringMs: 300,
    },
    {
      type: "aimed_burst",
      cooldown: [1700, 2300],
      count: 6,
      burstSpacingMs: 100,
      speed: 340,
    },
  ],
};

export const ascendedPhaseAttacks: Record<
  Exclude<BossPhase, "transition" | "defeated" | "dying" | "ascending">,
  BossAttackPreset[]
> = {
  phase1: [
    {
      type: "fan_burst",
      cooldown: [1200, 1800],
      count: 5,
      spreadDeg: 38,
      speed: 320,
    },
    {
      type: "ring_burst",
      cooldown: [2100, 2900],
      count: 16,
      spiralStepDeg: 14,
      speed: 290,
    },
    {
      type: "cross_burst",
      cooldown: [1700, 2400],
      count: 8,
      speed: 340,
    },
  ],
  phase2: [
    {
      type: "ring_burst",
      cooldown: [1700, 2500],
      count: 18,
      spiralStepDeg: 12,
      speed: 310,
    },
    {
      type: "fan_burst",
      cooldown: [1200, 1900],
      count: 6,
      spreadDeg: 40,
      speed: 330,
    },
    {
      type: "laser_sweep",
      cooldown: [2500, 3600],
      count: 6,
      laserWarningMs: 600,
      laserFiringMs: 260,
    },
    {
      type: "cross_burst",
      cooldown: [1400, 2000],
      count: 8,
      speed: 360,
    },
  ],
  phase3: [
    {
      type: "ring_burst",
      cooldown: [1500, 2200],
      count: 20,
      spiralStepDeg: 10,
      speed: 330,
    },
    {
      type: "fan_burst",
      cooldown: [1100, 1700],
      count: 7,
      spreadDeg: 46,
      speed: 350,
    },
    {
      type: "laser_sweep",
      cooldown: [2200, 3200],
      count: 7,
      laserWarningMs: 520,
      laserFiringMs: 240,
    },
    {
      type: "cross_burst",
      cooldown: [1200, 1800],
      count: 8,
      speed: 380,
    },
  ],
};
