import type { Vector2 } from "@/game/types";

export type BossAttackPreset = {
  type:
    | "spread"
    | "circular"
    | "aimed_burst"
    | "spiral"
    | "double_spread"
    | "laser_sweep"
    | "cross_burst"
    | "ring_burst"
    | "fan_burst";
  cooldown: [number, number];
  count?: number;
  spreadDeg?: number;
  speed?: number;
  burstSpacingMs?: number;
  spiralStepDeg?: number;
  laserWarningMs?: number;
  laserFiringMs?: number;
};

const toRadians = (deg: number) => (deg * Math.PI) / 180;

export const getSpreadVelocities = (
  direction: Vector2,
  count: number,
  spreadDeg: number,
  speed: number
) => {
  const baseAngle = Math.atan2(direction.y, direction.x);
  const angleStep = count > 1 ? toRadians(spreadDeg) / (count - 1) : 0;
  const startAngle = baseAngle - angleStep * (count - 1) * 0.5;
  const velocities: Vector2[] = [];
  for (let i = 0; i < count; i += 1) {
    const angle = startAngle + angleStep * i;
    velocities.push({ x: Math.cos(angle) * speed, y: Math.sin(angle) * speed });
  }
  return velocities;
};

export const getCircularVelocities = (count: number, speed: number, offset = 0) => {
  const velocities: Vector2[] = [];
  const step = (Math.PI * 2) / count;
  for (let i = 0; i < count; i += 1) {
    const angle = offset + step * i;
    velocities.push({ x: Math.cos(angle) * speed, y: Math.sin(angle) * speed });
  }
  return velocities;
};

export const getSpiralVelocities = (
  count: number,
  speed: number,
  startAngle: number,
  stepDeg: number
) => {
  const velocities: Vector2[] = [];
  const step = toRadians(stepDeg);
  for (let i = 0; i < count; i += 1) {
    const angle = startAngle + step * i;
    velocities.push({ x: Math.cos(angle) * speed, y: Math.sin(angle) * speed });
  }
  return { velocities, nextAngle: startAngle + step * count };
};

export const getCrossVelocities = (
  speed: number,
  rotation = 0,
  includeDiagonals = false
) => {
  const baseAngles = includeDiagonals
    ? [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2, Math.PI / 4, (3 * Math.PI) / 4, (5 * Math.PI) / 4, (7 * Math.PI) / 4]
    : [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2];
  return baseAngles.map((angle) => ({
    x: Math.cos(angle + rotation) * speed,
    y: Math.sin(angle + rotation) * speed,
  }));
};
