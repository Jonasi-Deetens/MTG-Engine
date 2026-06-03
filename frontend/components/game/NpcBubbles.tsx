import React from "react";
import type { NpcEntity, StoryPhase } from "@/game/types";

type NpcBubblesProps = {
  npcs: NpcEntity[];
  storyPhase: StoryPhase;
  npcDialogueIndex: number;
  npcBubbleVisibleMs: number;
  bounds: { width: number; height: number };
};

const dialogueLines = [
  "Do you hear the wind?",
  "Play with us?",
  "Throw it gently.",
  "Will they join us?",
  "We are only shades.",
];

const hostileLines = [
  "You... you killed one of us.",
  "We were only playing.",
  "Why would you do that?",
  "We did not mean to hurt you.",
  "This is not a game anymore.",
];

export function NpcBubbles({
  npcs,
  storyPhase,
  npcDialogueIndex,
  npcBubbleVisibleMs,
  bounds,
}: NpcBubblesProps) {
  if (!bounds.width || !bounds.height) return null;
  if (!npcs.length) return null;
  if (npcBubbleVisibleMs <= 0) return null;
  const isFriendly =
    storyPhase === "intro_dialogue" || storyPhase === "harmless_throwing";
  const isHostile = storyPhase === "first_kill_triggered" || storyPhase === "escalation";
  if (!isFriendly && !isHostile) return null;

  const speakers = npcs.filter((npc) => npc.isAlive).slice(0, 4);
  if (!speakers.length) return null;

  return (
    <>
      {speakers.map((npc, index) => {
        const lines = isHostile ? hostileLines : dialogueLines;
        const text = lines[(npcDialogueIndex + index) % lines.length];
        return (
          <div
            key={`bubble-${npc.id}`}
            className={`npc-bubble${isHostile ? " npc-bubble--hostile" : ""}`}
            style={{
              left: npc.position.x,
              top: npc.position.y - npc.radius * 2.2,
            }}
          >
            {text}
          </div>
        );
      })}
    </>
  );
}
