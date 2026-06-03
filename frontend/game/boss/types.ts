import type { Vector2 } from "@/game/types";

export type BossPhase =
  | "phase1"
  | "phase2"
  | "phase3"
  | "transition"
  | "dying"
  | "ascending"
  | "defeated";

export type BossAttackType =
  | "spread"
  | "circular"
  | "aimed_burst"
  | "spiral"
  | "double_spread"
  | "laser_sweep"
  | "cross_burst"
  | "ring_burst"
  | "fan_burst";

export type BossAttackState = {
  type: BossAttackType;
  cooldownMs: number;
  timerMs: number;
  burstRemaining?: number;
  burstSpacingMs?: number;
  spiralAngle?: number;
  spiralStepDeg?: number;
  spiralShotsRemaining?: number;
};

export type BossEntity = {
  id: number;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  hp: number;
  maxHp: number;
  phase: BossPhase;
  attackState: BossAttackState;
  transitionMs: number;
  isInvulnerable: boolean;
  isAscended: boolean;
  shotCooldownMs: number;
  deathTimerMs: number;
  ascendTimerMs: number;
  spawnTargetY: number;
  spinAngle: number;
  name: string;
  wave: number;
};
