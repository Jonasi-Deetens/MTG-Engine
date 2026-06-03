"use client";

import { Button } from "@/components/ui/Button";
import type { BossEntity, GameStatus, UpgradeOption } from "@/game/types";

type GameHUDProps = {
  status: GameStatus;
  score: number;
  lives: number;
  maxLives: number;
  elapsedMs: number;
  upgradeOptions: UpgradeOption[];
  boss: BossEntity | null;
  missionComplete: boolean;
  onStart: () => void;
  onResume: () => void;
  onReset: () => void;
  onSelectUpgrade: (upgradeId: UpgradeOption["id"]) => void;
};

const statusLabel: Record<GameStatus, string> = {
  idle: "READY",
  playing: "ACTIVE",
  paused: "PAUSED",
  gameover: "FAILED",
};

export function GameHUD({
  status,
  score,
  lives,
  maxLives,
  elapsedMs,
  upgradeOptions,
  boss,
  missionComplete,
  onStart,
  onResume,
  onReset,
  onSelectUpgrade,
}: GameHUDProps) {
  const minutes = Math.floor(elapsedMs / 60000);
  const seconds = Math.floor((elapsedMs % 60000) / 1000);
  const millis = Math.floor(elapsedMs % 1000);
  const timeLabel = `${String(minutes).padStart(2, "0")}:${String(
    seconds
  ).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
  const bossHpPercent = boss ? Math.max(0, Math.min(1, boss.hp / boss.maxHp)) : 0;
  const bossPhaseLabel =
    boss?.phase === "phase3"
      ? "PHASE 3"
      : boss?.phase === "phase2"
      ? "PHASE 2"
      : boss?.phase === "transition"
      ? "SHIFT"
      : "PHASE 1";

  return (
    <div className="absolute inset-0 flex flex-col pointer-events-none">
      <div className="flex items-start justify-between px-4 pt-4">
        <div className="space-y-1 text-[11px] uppercase tracking-[0.2em] font-mono text-[color:var(--theme-text-secondary)]">
          <div>
            Score{" "}
            <span className="text-[color:var(--theme-text-primary)]">
              {score}
            </span>
          </div>
          <div>
            Lives{" "}
            <span className="text-[color:var(--theme-accent-primary)]">
              {lives}/{maxLives}
            </span>
          </div>
        </div>
        <div className="text-right text-[10px] uppercase tracking-[0.3em] font-mono text-[color:var(--theme-accent-secondary)] space-y-1">
          <div>TIME: {timeLabel}</div>
          <div>ACTION_QUEUE: {statusLabel[status]}</div>
        </div>
      </div>

      {boss && (
        <div className="px-4 pt-3">
          <div className="ui-card nier-frame border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] px-4 py-3 text-[10px] uppercase tracking-[0.32em] font-mono text-[color:var(--theme-text-secondary)]">
            <div className="flex items-center justify-between">
              <span className="text-[color:var(--theme-text-primary)]">{boss.name}</span>
              <span className="text-[color:var(--theme-accent-primary)]">{bossPhaseLabel}</span>
              <span>{Math.round(bossHpPercent * 100)}%</span>
            </div>
            <div className="mt-2 h-[10px] w-full border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)]">
              <div
                className="h-full bg-[color:var(--theme-text-primary)] transition-[width] duration-150"
                style={{ width: `${bossHpPercent * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {upgradeOptions.length > 0 && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div
            className="ui-card nier-frame w-full max-w-xl border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] p-6 text-center space-y-4 pointer-events-auto"
            data-variant="default"
          >
            <div className="text-sm uppercase tracking-[0.3em] font-mono text-[color:var(--theme-text-primary)]">
              SYSTEM UPGRADE
            </div>
            <p className="text-xs text-[color:var(--theme-text-secondary)]">
              Select a module enhancement.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {upgradeOptions.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => onSelectUpgrade(option.id)}
                  className="border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] px-3 py-3 text-left text-xs uppercase tracking-[0.2em] font-mono text-[color:var(--theme-text-primary)] hover:bg-[color:var(--theme-button-primary-bg)] hover:text-[color:var(--theme-button-primary-text)] transition-colors"
                >
                  <div className="text-[10px] text-[color:var(--theme-text-secondary)]">
                    {option.title}
                  </div>
                  <div className="mt-2 text-[11px] tracking-[0.12em]">
                    {option.description}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {missionComplete && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div
            className="ui-card nier-frame w-full max-w-md border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] p-6 text-center space-y-4 pointer-events-auto"
            data-variant="default"
          >
            <div className="text-sm uppercase tracking-[0.3em] font-mono text-[color:var(--theme-text-primary)]">
              MISSION COMPLETE
            </div>
            <p className="text-xs text-[color:var(--theme-text-secondary)]">
              Ascended target neutralized. System integrity restored.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Button
                variant="primary"
                size="sm"
                onClick={onStart}
              >
                Restart
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onReset}
              >
                Reset
              </Button>
            </div>
          </div>
        </div>
      )}

      {upgradeOptions.length === 0 && status !== "playing" && !missionComplete && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div
            className="ui-card nier-frame w-full max-w-md border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] p-6 text-center space-y-4 pointer-events-auto"
            data-variant="default"
          >
            <div className="text-sm uppercase tracking-[0.3em] font-mono text-[color:var(--theme-text-primary)]">
              ORB NEUTRALIZATION
            </div>
            <p className="text-xs text-[color:var(--theme-text-secondary)]">
              Aim with the cursor. Click to fire. Keep the field clear.
            </p>
            <div className="flex items-center justify-center gap-3">
              {status === "idle" && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onStart}
                >
                  Start
                </Button>
              )}
              {status === "paused" && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onResume}
                >
                  Resume
                </Button>
              )}
              {status === "gameover" && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={onStart}
                >
                  Restart
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={onReset}
              >
                Reset
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
