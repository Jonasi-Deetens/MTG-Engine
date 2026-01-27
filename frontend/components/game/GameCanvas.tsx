"use client";

import React, { useCallback, useEffect } from "react";
import { useGameLoop } from "@/hooks/useGameLoop";
import type {
  BossEntity,
  GameStatus,
  LaserEntity,
  OrbEntity,
  ProjectileEntity,
  Vector2,
} from "@/hooks/useGameState";

type ThemeColors = {
  background: string;
  primary: string;
  accent: string;
  border: string;
};

type GameCanvasProps = {
  bounds: { width: number; height: number };
  status: GameStatus;
  colors: ThemeColors;
  canvasRef: React.RefObject<HTMLCanvasElement>;
  playerRef: React.MutableRefObject<Vector2>;
  orbsRef: React.MutableRefObject<OrbEntity[]>;
  lasersRef: React.MutableRefObject<LaserEntity[]>;
  bossesRef: React.MutableRefObject<BossEntity[]>;
  projectilesRef: React.MutableRefObject<ProjectileEntity[]>;
  pointerRef: React.MutableRefObject<Vector2>;
  onFrame: (deltaMs: number) => void;
  onPointerMove: (position: Vector2) => void;
  onPointerDown: (position: Vector2) => void;
  onPointerUp: () => void;
};

const getPointerPosition = (
  event: React.PointerEvent<HTMLCanvasElement>,
  bounds: { width: number; height: number }
): Vector2 => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * bounds.width;
  const y = ((event.clientY - rect.top) / rect.height) * bounds.height;
  return { x, y };
};

const drawArrow = (
  ctx: CanvasRenderingContext2D,
  base: Vector2,
  target: Vector2,
  color: string
) => {
  const dx = target.x - base.x;
  const dy = target.y - base.y;
  const angle = Math.atan2(dy, dx);
  const length = 26;
  const width = 10;

  ctx.save();
  ctx.translate(base.x, base.y);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(-length, width * 0.6);
  ctx.lineTo(-length, -width * 0.6);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
  ctx.restore();
};

const drawOrbs = (
  ctx: CanvasRenderingContext2D,
  orbs: OrbEntity[],
  accent: string,
  border: string,
  primary: string
) => {
  orbs.forEach((orb) => {
    const alpha = orb.isPhasing ? 0.35 : 1;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(orb.position.x, orb.position.y, orb.radius, 0, Math.PI * 2);
    const fill =
      orb.type === "fast"
        ? primary
        : orb.type === "slow"
        ? "rgba(139, 64, 73, 0.7)"
        : orb.type === "splitting"
        ? "rgba(106, 138, 133, 0.9)"
        : accent;
    ctx.fillStyle = fill;
    ctx.fill();
    ctx.strokeStyle = border;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();
  });
};

const drawProjectiles = (
  ctx: CanvasRenderingContext2D,
  projectiles: ProjectileEntity[],
  color: string
) => {
  projectiles.forEach((projectile) => {
    ctx.beginPath();
    ctx.arc(
      projectile.position.x,
      projectile.position.y,
      projectile.radius,
      0,
      Math.PI * 2
    );
    ctx.fillStyle = color;
    ctx.fill();
  });
};

const drawLasers = (
  ctx: CanvasRenderingContext2D,
  lasers: LaserEntity[],
  bounds: { width: number; height: number },
  accent: string
) => {
  lasers.forEach((laser) => {
    ctx.save();
    if (laser.status === "warning") {
      ctx.strokeStyle = accent;
      ctx.globalAlpha = 0.35;
      ctx.setLineDash([6, 6]);
      ctx.lineWidth = 1;
    } else {
      ctx.strokeStyle = accent;
      ctx.globalAlpha = 0.85;
      ctx.setLineDash([]);
      ctx.lineWidth = 4;
    }
    ctx.beginPath();
    if (laser.axis === "horizontal") {
      ctx.moveTo(0, laser.position);
      ctx.lineTo(bounds.width, laser.position);
    } else {
      ctx.moveTo(laser.position, 0);
      ctx.lineTo(laser.position, bounds.height);
    }
    ctx.stroke();
    ctx.restore();
  });
};

const drawBosses = (
  ctx: CanvasRenderingContext2D,
  bosses: BossEntity[],
  border: string,
  primary: string
) => {
  bosses.forEach((boss) => {
    ctx.save();
    ctx.beginPath();
    ctx.arc(boss.position.x, boss.position.y, boss.radius, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(24, 22, 19, 0.85)";
    ctx.fill();
    ctx.strokeStyle = border;
    ctx.lineWidth = 2;
    ctx.stroke();

    const barWidth = boss.radius * 1.6;
    const barHeight = 6;
    const barX = boss.position.x - barWidth / 2;
    const barY = boss.position.y - boss.radius - 14;
    ctx.fillStyle = "rgba(0, 0, 0, 0.4)";
    ctx.fillRect(barX, barY, barWidth, barHeight);
    ctx.fillStyle = primary;
    ctx.fillRect(
      barX,
      barY,
      barWidth * (boss.hp / boss.maxHp),
      barHeight
    );
    ctx.restore();
  });
};

export function GameCanvas({
  bounds,
  status,
  colors,
  canvasRef,
  playerRef,
  orbsRef,
  lasersRef,
  bossesRef,
  projectilesRef,
  pointerRef,
  onFrame,
  onPointerMove,
  onPointerDown,
  onPointerUp,
}: GameCanvasProps) {
  const drawFrame = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const { width, height } = bounds;
    if (!width || !height) return;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = colors.background;
    ctx.fillRect(0, 0, width, height);

    drawLasers(ctx, lasersRef.current, bounds, colors.accent);
    drawOrbs(ctx, orbsRef.current, colors.accent, colors.border, colors.primary);
    drawBosses(ctx, bossesRef.current, colors.border, colors.primary);
    drawProjectiles(ctx, projectilesRef.current, colors.primary);

    const pointer = pointerRef.current;
    const player = playerRef.current;
    drawArrow(ctx, player, pointer, colors.primary);

    if (status !== "playing") {
      ctx.fillStyle = "rgba(0, 0, 0, 0.15)";
      ctx.fillRect(0, 0, width, height);
    }
  }, [
    bounds,
    canvasRef,
    colors,
    lasersRef,
    orbsRef,
    bossesRef,
    playerRef,
    pointerRef,
    projectilesRef,
    status,
  ]);

  const { start, stop } = useGameLoop((deltaMs) => {
    onFrame(deltaMs);
    drawFrame();
  });

  useEffect(() => {
    if (status === "playing") {
      start();
      return;
    }
    stop();
    drawFrame();
  }, [drawFrame, start, status, stop]);

  useEffect(() => {
    drawFrame();
  }, [drawFrame, bounds.width, bounds.height]);

  const handlePointerMove = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const position = getPointerPosition(event, bounds);
    onPointerMove(position);
    drawFrame();
  };

  const handlePointerDown = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const position = getPointerPosition(event, bounds);
    onPointerDown(position);
  };

  return (
    <canvas
      ref={canvasRef}
      width={bounds.width}
      height={bounds.height}
      className="h-full w-full cursor-crosshair"
      onPointerMove={handlePointerMove}
      onPointerDown={handlePointerDown}
      onPointerUp={onPointerUp}
      onPointerLeave={onPointerUp}
      role="img"
      aria-label="Arrow game canvas"
    />
  );
}
