"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { GameCanvas } from "@/components/game/GameCanvas";
import { GameHUD } from "@/components/game/GameHUD";
import { BossBubbles } from "@/components/game/BossBubbles";
import { BossSprite } from "@/components/game/BossSprite";
import { NpcBubbles } from "@/components/game/NpcBubbles";
import { NpcSprite } from "@/components/game/NpcSprite";
import { useGameState } from "@/hooks/useGameState";

type ThemeColors = {
  background: string;
  primary: string;
  accent: string;
  border: string;
};

const fallbackColors: ThemeColors = {
  background: "#1c1a16",
  primary: "#e7e0d0",
  accent: "#8b4049",
  border: "#8f8876",
};

export function ArrowGame() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [bounds, setBounds] = useState({ width: 0, height: 0 });
  const [colors, setColors] = useState<ThemeColors>(fallbackColors);
  const pointerPositionRef = useRef({ x: 0, y: 0 });
  const playerPositionRef = useRef({ x: 0, y: 0 });
  const moveRef = useRef({ up: false, down: false, left: false, right: false });
  const isFiringRef = useRef(false);
  const fireCooldownRef = useRef(0);

  const { state, refs, actions } = useGameState();

  const updateBounds = useCallback(() => {
    const element = containerRef.current;
    if (!element) return;
    const nextBounds = {
      width: element.clientWidth,
      height: element.clientHeight,
    };
    setBounds(nextBounds);
  }, []);

  useEffect(() => {
    updateBounds();
    const element = containerRef.current;
    if (!element) return;
    const observer = new ResizeObserver(() => updateBounds());
    observer.observe(element);
    return () => observer.disconnect();
  }, [updateBounds]);

  useEffect(() => {
    if (!bounds.width || !bounds.height) return;
    const initialPointer = { x: bounds.width * 0.5, y: bounds.height * 0.4 };
    actions.setPointer(initialPointer);
    pointerPositionRef.current = initialPointer;
    playerPositionRef.current = {
      x: bounds.width * 0.5,
      y: bounds.height * 0.82,
    };
  }, [actions, bounds.height, bounds.width]);

  useEffect(() => {
    const updateColors = () => {
      if (typeof document === "undefined") return;
      const style = getComputedStyle(document.documentElement);
      const read = (name: string, fallback: string) =>
        style.getPropertyValue(name).trim() || fallback;
      setColors({
        background: read("--theme-bg-primary", fallbackColors.background),
        primary: read("--theme-text-primary", fallbackColors.primary),
        accent: read("--theme-accent-primary", fallbackColors.accent),
        border: read("--theme-border-default", fallbackColors.border),
      });
    };

    updateColors();
    const observer = new MutationObserver(updateColors);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.repeat) return;
      switch (event.key.toLowerCase()) {
        case "w":
          moveRef.current.up = true;
          break;
        case "a":
          moveRef.current.left = true;
          break;
        case "s":
          moveRef.current.down = true;
          break;
        case "d":
          moveRef.current.right = true;
          break;
        default:
          break;
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      switch (event.key.toLowerCase()) {
        case "w":
          moveRef.current.up = false;
          break;
        case "a":
          moveRef.current.left = false;
          break;
        case "s":
          moveRef.current.down = false;
          break;
        case "d":
          moveRef.current.right = false;
          break;
        default:
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, []);

  const handleFrame = useCallback(
    (deltaMs: number) => {
      actions.update(deltaMs, bounds, playerPositionRef.current);
      if (bounds.width && bounds.height) {
        const speed = state.playerStats.moveSpeed;
        const deltaSec = deltaMs / 1000;
        const dx =
          (moveRef.current.right ? 1 : 0) - (moveRef.current.left ? 1 : 0);
        const dy =
          (moveRef.current.down ? 1 : 0) - (moveRef.current.up ? 1 : 0);

        if (dx || dy) {
          const length = Math.hypot(dx, dy) || 1;
          const nextX =
            playerPositionRef.current.x + (dx / length) * speed * deltaSec;
          const nextY =
            playerPositionRef.current.y + (dy / length) * speed * deltaSec;
          playerPositionRef.current = {
            x: Math.min(bounds.width, Math.max(0, nextX)),
            y: Math.min(bounds.height, Math.max(0, nextY)),
          };
        }
      }
      if (state.status !== "playing") return;
      if (!state.playerStats.fireOnHold || !isFiringRef.current) return;
      fireCooldownRef.current -= deltaMs;
      if (fireCooldownRef.current <= 0) {
        fireCooldownRef.current = state.playerStats.fireCooldownMs;
        actions.shoot(playerPositionRef.current, pointerPositionRef.current);
      }
    },
    [actions, bounds, state.status]
  );

  const handlePointerMove = useCallback(
    (position: { x: number; y: number }) => {
      actions.setPointer(position);
      pointerPositionRef.current = position;
    },
    [actions]
  );

  const handlePointerDown = useCallback(
    (position: { x: number; y: number }) => {
      actions.setPointer(position);
      pointerPositionRef.current = position;
      isFiringRef.current = true;
      fireCooldownRef.current = 0;
      if (state.status !== "playing") {
        actions.startGame();
        return;
      }
      actions.shoot(playerPositionRef.current, position);
    },
    [actions, state.status]
  );

  const handlePointerUp = useCallback(() => {
    isFiringRef.current = false;
    fireCooldownRef.current = 0;
  }, []);

  return (
    <div ref={containerRef} className="relative h-full w-full overflow-hidden">
      <GameCanvas
        bounds={bounds}
        status={state.status}
        colors={colors}
        canvasRef={canvasRef}
        elapsedMs={state.elapsedMs}
        playerRef={playerPositionRef}
        orbsRef={refs.orbsRef}
        lasersRef={refs.lasersRef}
        bossesRef={refs.bossesRef}
        projectilesRef={refs.projectilesRef}
        enemyProjectilesRef={refs.enemyProjectilesRef}
        npcProjectilesRef={refs.npcProjectilesRef}
        rewardRef={refs.rewardRef}
        pointerRef={refs.pointerRef}
        onFrame={handleFrame}
        onPointerMove={handlePointerMove}
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
      />
      <NpcSprite npcs={state.npcs} bounds={bounds} />
      <NpcBubbles
        npcs={state.npcs}
        storyPhase={state.storyPhase}
        npcDialogueIndex={state.npcDialogueIndex}
        npcBubbleVisibleMs={state.npcBubbleVisibleMs}
        bounds={bounds}
      />
      <BossBubbles
        boss={state.boss}
        bossDialogueIndex={state.bossDialogueIndex}
        bossBubbleVisibleMs={state.bossBubbleVisibleMs}
        isAscended={state.boss?.isAscended ?? false}
        bossPhaseMessage={state.bossPhaseMessage}
        bossPhaseMessageMs={state.bossPhaseMessageMs}
      />
      <BossSprite boss={state.boss} bounds={bounds} />
      <GameHUD
        status={state.status}
        score={state.score}
        lives={state.lives}
        maxLives={state.maxLives}
        elapsedMs={state.elapsedMs}
        upgradeOptions={state.upgradeOptions}
        boss={state.boss}
        missionComplete={state.missionComplete}
        onStart={actions.startGame}
        onResume={actions.resumeGame}
        onReset={actions.resetGame}
        onSelectUpgrade={actions.applyUpgrade}
      />
    </div>
  );
}
