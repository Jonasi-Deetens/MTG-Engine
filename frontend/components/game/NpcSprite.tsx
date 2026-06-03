import React from "react";
import type { NpcEntity } from "@/game/types";

type NpcSpriteProps = {
  npcs: NpcEntity[];
  bounds: { width: number; height: number };
};

export function NpcSprite({ npcs, bounds }: NpcSpriteProps) {
  if (!bounds.width || !bounds.height) return null;
  if (!npcs.length) return null;

  return (
    <>
      {npcs.map((npc) => {
        if (!npc.isAlive) return null;
        const size = npc.radius * 2;
        const className = `npc-sprite ${npc.mood === "hostile" ? "npc-hostile" : "npc-beige"}`;
        return (
          <div
            key={npc.id}
            className={className}
            style={{
              width: size,
              height: size,
              left: npc.position.x,
              top: npc.position.y,
            }}
          />
        );
      })}
    </>
  );
}
