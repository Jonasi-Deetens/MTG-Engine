"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { Button } from "@/components/ui/Button";
import { ArchiveSectionHeader } from "@/components/ui/ArchiveSectionHeader";

interface ShortcutHelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const shortcuts = [
  {
    group: "Universal",
    items: [
      { keys: "Ctrl + Space / Cmd + K", label: "Quick search" },
      { keys: "G then C", label: "Go to Collection" },
      { keys: "G then D", label: "Go to Decks" },
      { keys: "G then B", label: "Go to Builder" },
      { keys: "Alt + D", label: "Last viewed deck" },
    ],
  },
  {
    group: "Deckbuilding",
    items: [
      { keys: "N then D", label: "New Deck" },
      { keys: "A", label: "Add focused card to deck" },
      { keys: "X", label: "Remove one copy" },
      { keys: "Shift + X", label: "Remove all copies" },
      { keys: "+ / -", label: "Increment / decrement quantity" },
    ],
  },
  {
    group: "Graph",
    items: [
      { keys: "G", label: "Open card graph (card detail)" },
      { keys: "Ctrl + R / Cmd + R", label: "Rebuild / validate graph" },
      { keys: "D", label: "Toggle debug overlay" },
    ],
  },
  {
    group: "Collections",
    items: [
      { keys: "O", label: "Toggle owned (collection)" },
      { keys: "+ / -", label: "Increment / decrement owned count" },
    ],
  },
  {
    group: "Help",
    items: [{ keys: "?", label: "Show shortcut help" }],
  },
];

export function ShortcutHelpModal({ isOpen, onClose }: ShortcutHelpModalProps) {
  const previouslyFocused = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen) return;

    previouslyFocused.current = document.activeElement as HTMLElement | null;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
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
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-[color:var(--theme-overlay-strong)]/70 backdrop-blur-sm p-4 sm:p-8"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Shortcut help"
    >
      <div
        className="ui-card w-full max-w-3xl bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-border-default)] shadow-xl"
        data-variant="default"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 sm:p-6 space-y-4">
          <div>
            <ArchiveSectionHeader
              title="Shortcuts"
              status="HELP_INDEX: LOADED"
              className="mb-2"
              titleClassName="text-lg sm:text-xl"
              action={
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  aria-label="Close shortcuts"
                >
                  Close
                </Button>
              }
            />
            <p className="text-xs sm:text-sm text-[color:var(--theme-text-secondary)]">
              Press <span className="font-mono">Esc</span> to close
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[70vh] overflow-y-auto pr-1">
            {shortcuts.map((section) => (
              <div
                key={section.group}
                className="space-y-2"
              >
                <div className="text-xs uppercase tracking-[0.2em] font-mono text-[color:var(--theme-text-secondary)]">
                  {section.group}
                </div>
                <div className="space-y-2">
                  {section.items.map((item) => (
                    <div
                      key={item.label}
                      className="flex items-center justify-between gap-4 border border-[color:var(--theme-border-default)] bg-[color:var(--theme-card-bg)] px-3 py-2"
                    >
                      <span className="text-sm text-[color:var(--theme-text-primary)]">
                        {item.label}
                      </span>
                      <span className="font-mono text-[10px] tracking-[0.12em] text-[color:var(--theme-text-secondary)] uppercase">
                        {item.keys}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  return typeof window !== "undefined"
    ? createPortal(modalContent, document.body)
    : null;
}
