import type { UpgradeId, UpgradeOption } from "@/game/types";

export const upgradePool: UpgradeOption[] = [
  {
    id: "damage",
    title: "Damage +1",
    description: "Increase projectile damage by 1.",
  },
  {
    id: "fire_rate",
    title: "Fire Rate +15%",
    description: "Shoot faster by reducing cooldown.",
  },
  {
    id: "move_speed",
    title: "Move Speed +15%",
    description: "Move faster across the arena.",
  },
  {
    id: "heal",
    title: "Repair +1",
    description: "Restore 1 life immediately.",
  },
  {
    id: "max_lives",
    title: "Max Integrity +1",
    description: "Increase maximum lives by 1.",
  },
];

const shuffle = <T,>(items: T[]) => {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
};

export const pickUpgrades = (
  count: number,
  excluded: UpgradeId[] = []
) => {
  const available = upgradePool.filter((option) => !excluded.includes(option.id));
  return shuffle(available).slice(0, count);
};
