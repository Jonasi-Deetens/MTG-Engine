"use client";

import { Button } from "@/components/ui/Button";
import type { GameStatus } from "@/hooks/useGameState";

type GameHUDProps = {
  status: GameStatus;
  score: number;
  lives: number;
  elapsedMs: number;
  onStart: () => void;
  onResume: () => void;
  onReset: () => void;
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
  elapsedMs,
  onStart,
  onResume,
  onReset,
}: GameHUDProps) {
  const minutes = Math.floor(elapsedMs / 60000);
  const seconds = Math.floor((elapsedMs % 60000) / 1000);
  const millis = Math.floor(elapsedMs % 1000);
  const timeLabel = `${String(minutes).padStart(2, "0")}:${String(
    seconds
  ).padStart(2, "0")}.${String(millis).padStart(3, "0")}`;
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
              {lives}
            </span>
          </div>
        </div>
        <div className="text-right text-[10px] uppercase tracking-[0.3em] font-mono text-[color:var(--theme-accent-secondary)] space-y-1">
          <div>TIME: {timeLabel}</div>
          <div>ACTION_QUEUE: {statusLabel[status]}</div>
        </div>
      </div>

      {status !== "playing" && (
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
                  className="h-8"
                  onClick={onStart}
                >
                  Start
                </Button>
              )}
              {status === "paused" && (
                <Button
                  variant="primary"
                  size="sm"
                  className="h-8"
                  onClick={onResume}
                >
                  Resume
                </Button>
              )}
              {status === "gameover" && (
                <Button
                  variant="primary"
                  size="sm"
                  className="h-8"
                  onClick={onStart}
                >
                  Restart
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="h-8"
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
