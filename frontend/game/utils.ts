import type { Vector2 } from "@/game/types";

export const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

export const normalize = (vec: Vector2): Vector2 => {
  const length = Math.hypot(vec.x, vec.y);
  if (!length) return { x: 0, y: 0 };
  return { x: vec.x / length, y: vec.y / length };
};

export const randomBetween = (min: number, max: number) =>
  min + Math.random() * (max - min);

export const weightedPick = <T extends string>(
  weights: Array<{ type: T; weight: number }>
) => {
  const total = weights.reduce((sum, item) => sum + item.weight, 0);
  const roll = Math.random() * total;
  let current = 0;
  for (const item of weights) {
    current += item.weight;
    if (roll <= current) return item.type;
  }
  return weights[0].type;
};
