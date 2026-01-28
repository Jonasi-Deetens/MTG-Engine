"use client";

import React, { useCallback, useEffect } from "react";
import { useGameLoop } from "@/hooks/useGameLoop";
import type {
  BossEntity,
  EnemyProjectileEntity,
  GameStatus,
  LaserEntity,
  NpcProjectileEntity,
  OrbEntity,
  ProjectileEntity,
  RewardEntity,
  Vector2,
} from "@/game/types";
import { enemyProjectileColor, monsterColors } from "@/game/config";
import { bossBaseConfig, bossDeathConfig } from "@/game/boss/config";

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
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  elapsedMs: number;
  playerRef: React.MutableRefObject<Vector2>;
  orbsRef: React.MutableRefObject<OrbEntity[]>;
  lasersRef: React.MutableRefObject<LaserEntity[]>;
  bossesRef: React.MutableRefObject<BossEntity[]>;
  projectilesRef: React.MutableRefObject<ProjectileEntity[]>;
  enemyProjectilesRef: React.MutableRefObject<EnemyProjectileEntity[]>;
  npcProjectilesRef: React.MutableRefObject<NpcProjectileEntity[]>;
  rewardRef: React.MutableRefObject<RewardEntity | null>;
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
  color: string,
  border: string
) => {
  const dx = target.x - base.x;
  const dy = target.y - base.y;
  const angle = Math.atan2(dy, dx);
  const length = 24;
  const width = 14;

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
  ctx.strokeStyle = border;
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.restore();
};

const drawOrbs = (
  ctx: CanvasRenderingContext2D,
  orbs: OrbEntity[],
  accent: string,
  border: string
) => {
  orbs.forEach((orb) => {
    const alpha = orb.isPhasing ? 0.35 : 1;
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(orb.position.x, orb.position.y, orb.radius, 0, Math.PI * 2);
    ctx.fillStyle = "#0d0c0b";
    ctx.fill();
    ctx.shadowColor = "#c03a3a";
    ctx.shadowBlur = 8;
    ctx.strokeStyle = "#c03a3a";
    ctx.lineWidth = 1.5;
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
    ctx.save();
    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 10;
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
    ctx.restore();
  });
};

const drawEnemyProjectiles = (
  ctx: CanvasRenderingContext2D,
  projectiles: EnemyProjectileEntity[]
) => {
  projectiles.forEach((projectile) => {
    ctx.save();
    ctx.shadowColor = "#c03a3a";
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(
      projectile.position.x,
      projectile.position.y,
      projectile.radius,
      0,
      Math.PI * 2
    );
    ctx.fillStyle = "#c03a3a";
    ctx.fill();
    ctx.restore();
  });
};

const drawNpcProjectiles = (
  ctx: CanvasRenderingContext2D,
  projectiles: NpcProjectileEntity[]
) => {
  projectiles.forEach((projectile) => {
    ctx.save();
    ctx.shadowColor = "#ffffff";
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(
      projectile.position.x,
      projectile.position.y,
      projectile.radius,
      0,
      Math.PI * 2
    );
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    ctx.fill();
    ctx.restore();
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
    ctx.shadowColor = "#c03a3a";
    ctx.shadowBlur = 8;
    if (laser.status === "warning") {
      ctx.strokeStyle = "#c03a3a";
      ctx.globalAlpha = 0.35;
      ctx.setLineDash([6, 6]);
      ctx.lineWidth = 1;
    } else {
      ctx.strokeStyle = "#c03a3a";
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

const drawReward = (
  ctx: CanvasRenderingContext2D,
  reward: RewardEntity | null,
  accent: string
) => {
  if (!reward) return;
  const pulse = 0.9 + 0.12 * Math.sin(reward.pulseMs / 180);
  const radius = reward.radius * pulse;
  ctx.save();
  ctx.translate(reward.position.x, reward.position.y);
  ctx.shadowColor = accent;
  ctx.shadowBlur = 14;
  ctx.beginPath();
  ctx.arc(0, 0, radius, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(245, 210, 120, 0.95)";
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = accent;
  ctx.stroke();
  ctx.restore();
};

const drawBosses = (
  ctx: CanvasRenderingContext2D,
  bosses: BossEntity[],
  border: string,
  primary: string,
  accent: string,
  elapsedMs: number
) => {
  bosses.forEach((boss) => {
    if (boss.isAscended) return;
    const isPhaseTwo = boss.phase === "phase2";
    const isPhaseThree = boss.phase === "phase3";
    const isEvolved = isPhaseTwo || isPhaseThree;
    const isAscended = boss.isAscended;
    const isDying = boss.phase === "dying";
    const isAscending = boss.phase === "ascending";
    const ascendedAccent = "#e14b7a";
    const phaseGlow = isAscended ? ascendedAccent : isEvolved ? accent : primary;
    const pulse =
      boss.phase === "transition"
        ? 0.4 + 0.6 * Math.sin((boss.transitionMs / 1400) * Math.PI * 3)
        : 1;
    const baseRotation = Math.PI / (isEvolved ? 5 : 4);
    const rotation = boss.spinAngle ? baseRotation + boss.spinAngle : baseRotation;
    const deathProgress = isDying
      ? 1 - boss.deathTimerMs / bossDeathConfig.deathDurationMs
      : 0;
    const ascendProgress = isAscending
      ? 1 - boss.ascendTimerMs / bossDeathConfig.ascendDurationMs
      : 0;
    const scale = isDying ? 1 - deathProgress * 0.7 : isAscending ? 0.6 + ascendProgress * 0.4 : 1;
    const alpha = isDying ? 1 - deathProgress : isAscending ? ascendProgress : pulse;
    const time = elapsedMs / 1000;
    const glitchStrength = isAscended ? (isDying ? 6 : isAscending ? 5 : 3) : 0;
    const glitchX = glitchStrength
      ? Math.sin(time * 12 + boss.id) * glitchStrength * 0.6
      : 0;
    const glitchY = glitchStrength
      ? Math.cos(time * 9 + boss.id * 0.4) * glitchStrength * 0.6
      : 0;
    const flicker = isAscended ? 0.8 + 0.2 * Math.sin(time * 18 + boss.id) : 1;

    ctx.save();
    ctx.globalAlpha = alpha * flicker;
    ctx.translate(boss.position.x + glitchX, boss.position.y + glitchY);
    ctx.scale(scale, scale);
    ctx.rotate(rotation);

    ctx.beginPath();
    ctx.arc(0, 0, boss.radius, 0, Math.PI * 2);
    ctx.fillStyle = isPhaseThree
      ? "rgba(255, 255, 255, 0.98)"
      : isPhaseTwo
      ? "rgba(245, 242, 236, 0.95)"
      : "rgba(18, 16, 14, 0.9)";
    ctx.fill();
    ctx.strokeStyle = isAscended ? ascendedAccent : border;
    ctx.lineWidth = 3;
    ctx.stroke();

    if (isEvolved) {
      const spikeCount = 8;
      const spikeInner = boss.radius * 0.92;
      const spikeOuter = boss.radius * 1.35;
      const startAngle = Math.PI / 8;
      ctx.save();
      ctx.shadowColor = isAscended ? ascendedAccent : isPhaseThree ? "#ffffff" : accent;
      ctx.shadowBlur = isAscended ? 24 : isPhaseThree ? 20 : 14;
      ctx.strokeStyle = isAscended ? ascendedAccent : isPhaseThree ? "#ffffff" : accent;
      ctx.lineWidth = 2.5;
      ctx.setLineDash([10, 6]);
      ctx.beginPath();
      ctx.arc(0, 0, boss.radius * 1.05, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < spikeCount; i += 1) {
        const angle = startAngle + (Math.PI * 2 * i) / spikeCount;
        const innerX = Math.cos(angle) * spikeInner;
        const innerY = Math.sin(angle) * spikeInner;
        const outerX = Math.cos(angle) * spikeOuter;
        const outerY = Math.sin(angle) * spikeOuter;
        ctx.moveTo(innerX, innerY);
        ctx.lineTo(outerX, outerY);
      }
      ctx.stroke();
      ctx.restore();
    }

    ctx.beginPath();
    ctx.arc(0, 0, boss.radius * 0.62, 0, Math.PI * 2);
    ctx.strokeStyle = phaseGlow;
    ctx.lineWidth = isEvolved ? 2 : 1.5;
    ctx.setLineDash(isEvolved ? [4, 2] : [6, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = isPhaseThree
      ? "rgba(220, 220, 220, 0.85)"
      : isPhaseTwo
      ? "rgba(120, 48, 68, 0.75)"
      : "rgba(60, 56, 48, 0.7)";
    ctx.fillRect(
      -boss.radius * 0.32,
      -boss.radius * 0.32,
      boss.radius * 0.64,
      boss.radius * 0.64
    );

    ctx.strokeStyle = phaseGlow;
    ctx.lineWidth = isEvolved ? 2 : 1.5;
    ctx.beginPath();
    ctx.moveTo(-boss.radius * 0.9, 0);
    ctx.lineTo(boss.radius * 0.9, 0);
    ctx.moveTo(0, -boss.radius * 0.9);
    ctx.lineTo(0, boss.radius * 0.9);
    ctx.stroke();

    if (isAscended) {
      ctx.save();
      ctx.globalAlpha = 0.35 + 0.15 * Math.sin(time * 8 + boss.id);
      ctx.strokeStyle = ascendedAccent;
      ctx.lineWidth = 1;
      const scanOffset = Math.sin(time * 6) * 3;
      for (let y = -boss.radius + scanOffset; y <= boss.radius; y += 6) {
        ctx.beginPath();
        ctx.moveTo(-boss.radius, y);
        ctx.lineTo(boss.radius, y);
        ctx.stroke();
      }
      ctx.restore();
    }

    ctx.restore();

    if (boss.phase === "transition") {
      const progress = 1 - boss.transitionMs / bossBaseConfig.transitionMs;
      const ringRadius = boss.radius * (1.1 + progress * 0.5);
      ctx.save();
      ctx.globalAlpha = 0.55 - progress * 0.35;
      ctx.strokeStyle = accent;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(boss.position.x, boss.position.y, ringRadius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  });
};

export function GameCanvas({
  bounds,
  status,
  colors,
  canvasRef,
  elapsedMs,
  playerRef,
  orbsRef,
  lasersRef,
  bossesRef,
  projectilesRef,
  enemyProjectilesRef,
  npcProjectilesRef,
  rewardRef,
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
    drawOrbs(ctx, orbsRef.current, colors.accent, colors.border);
    if (!bossesRef.current.length) {
      drawBosses(ctx, bossesRef.current, colors.border, colors.primary, colors.accent, elapsedMs);
    }
    drawReward(ctx, rewardRef.current, colors.accent);
    drawNpcProjectiles(ctx, npcProjectilesRef.current);
    drawProjectiles(ctx, projectilesRef.current, "rgba(255, 255, 255, 0.9)");
    drawEnemyProjectiles(ctx, enemyProjectilesRef.current);

    const pointer = pointerRef.current;
    const player = playerRef.current;
    drawArrow(ctx, player, pointer, "#ffffff", colors.border);

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
    npcProjectilesRef,
    elapsedMs,
    rewardRef,
    playerRef,
    pointerRef,
    projectilesRef,
    enemyProjectilesRef,
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
