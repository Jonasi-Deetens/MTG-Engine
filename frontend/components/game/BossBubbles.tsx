import React from "react";
import type { BossEntity } from "@/game/types";

type BossBubblesProps = {
  boss: BossEntity | null;
  bossDialogueIndex: number;
  bossBubbleVisibleMs: number;
  isAscended: boolean;
  bossPhaseMessage: string;
  bossPhaseMessageMs: number;
};

const bossLines = [
  "You do not belong here.",
  "Leave. Now.",
  "I will break you.",
];

const ascendedLines = [
  "You should have stayed down.",
  "I will erase you.",
  "You will not survive this.",
];

export function BossBubbles({
  boss,
  bossDialogueIndex,
  bossBubbleVisibleMs,
  isAscended,
  bossPhaseMessage,
  bossPhaseMessageMs,
}: BossBubblesProps) {
  const showPhase = bossPhaseMessageMs > 0 && bossPhaseMessage;
  if (!boss || (!showPhase && bossBubbleVisibleMs <= 0)) return null;
  const lines = isAscended ? ascendedLines : bossLines;
  const text = showPhase ? bossPhaseMessage : lines[bossDialogueIndex % lines.length];

  return (
    <div
      className="boss-bubble"
      style={{
        left: boss.position.x,
        top: boss.position.y - boss.radius * 1.6,
      }}
    >
      {text}
    </div>
  );
}
