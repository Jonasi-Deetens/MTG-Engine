"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { ArrowGame } from "@/components/game/ArrowGame";
import { Button } from "@/components/ui/Button";

type GameModalProps = {
  isOpen: boolean;
  onClose: () => void;
};

export function GameModal({ isOpen, onClose }: GameModalProps) {
  const previouslyFocused = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    previouslyFocused.current = document.activeElement as HTMLElement | null;

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleEscape);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "unset";
      requestAnimationFrame(() => previouslyFocused.current?.focus?.());
      previouslyFocused.current = null;
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const modalContent = (
    <div
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-[color:var(--theme-overlay-strong)]/70 backdrop-blur-sm p-2 sm:p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Arrow game"
    >
      <div
        className="ui-card relative w-full h-full max-w-[96vw] max-h-[92vh] border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] shadow-xl overflow-hidden"
        data-variant="default"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="absolute inset-0 nier-scanline" aria-hidden="true" />
        <div className="relative z-10 flex h-full flex-col">
          <div className="flex items-center justify-between border-b border-[color:var(--theme-border-default)] px-4 py-2 text-xs uppercase tracking-[0.3em] font-mono text-[color:var(--theme-text-secondary)]">
            <div>SIMULATED DRILL: ARROW PROTOCOL</div>
            <Button
              type="button"
              variant="frame"
              size="sm"
              onClick={onClose}
              className="w-10 p-0"
              aria-label="Close game modal"
            >
              <svg
                viewBox="0 0 20 20"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="square"
                strokeLinejoin="round"
                className="h-4 w-4"
                aria-hidden="true"
              >
                <path d="M5 5L15 15" />
                <path d="M15 5L5 15" />
              </svg>
            </Button>
          </div>
          <div className="flex-1">
            <ArrowGame />
          </div>
        </div>
      </div>
    </div>
  );

  return typeof window !== "undefined"
    ? createPortal(modalContent, document.body)
    : null;
}
