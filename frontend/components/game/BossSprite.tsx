import React from "react";
import type { BossEntity } from "@/game/types";

type BossSpriteProps = {
  boss: BossEntity | null;
  bounds: { width: number; height: number };
};

const buildClassName = (boss: BossEntity) => {
  const classes = ["boss-container"];
  if (boss.phase === "phase2") classes.push("boss-phase-2");
  if (boss.phase === "phase3") classes.push("boss-phase-3");
  if (boss.phase === "transition" || boss.phase === "ascending") {
    classes.push("is-transitioning");
  }
  if (boss.phase === "dying") classes.push("is-dying");
  if (boss.isAscended) classes.push("boss-ascended");
  return classes.join(" ");
};

export function BossSprite({ boss, bounds }: BossSpriteProps) {
  if (!boss) return null;
  if (!bounds.width || !bounds.height) return null;

  const size = boss.radius * 2;
  const shouldShowSpikes = boss.phase === "phase2" || boss.phase === "phase3";

  return (
    <div
      className="boss-sprite"
      style={{
        width: size,
        height: size,
        left: boss.position.x,
        top: boss.position.y,
      }}
    >
      <div className={buildClassName(boss)} style={{ width: "100%", height: "100%" }}>
        {shouldShowSpikes ? <div className="spikes-overlay" /> : null}
        <div className="boss-core" />
      </div>
    </div>
  );
}
