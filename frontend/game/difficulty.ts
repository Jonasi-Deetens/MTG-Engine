import { baseSpawnIntervalMs } from "@/game/config";

export const easeOutQuad = (t: number) => 1 - (1 - t) * (1 - t);

export const getDifficulty = (elapsedMs: number, targetMs = 6 * 60 * 1000) =>
  easeOutQuad(Math.min(elapsedMs / targetMs, 1));

export const getSpawnIntervalBase = (score: number) =>
  Math.max(
    450,
    baseSpawnIntervalMs - Math.min(350, Math.floor(score / 250) * 20)
  );

export const getLaserWindow = (difficulty: number) => {
  const min = 3500 + (1 - difficulty) * 2500;
  const max = 6000 + (1 - difficulty) * 4000;
  return { min, max };
};
