"use client";

import { useEffect, useRef } from "react";
import { createPortal } from "react-dom";
import { SearchInput } from "@/components/ui/SearchInput";
import { Button } from "@/components/ui/Button";
import { ArchiveSectionHeader } from "@/components/ui/ArchiveSectionHeader";

interface QuickSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  query: string;
  setQuery: (value: string) => void;
  onSubmit: () => void;
}

export function QuickSearchModal({
  isOpen,
  onClose,
  query,
  setQuery,
  onSubmit,
}: QuickSearchModalProps) {
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
      className="fixed inset-0 z-[9999] flex items-start justify-center bg-[color:var(--theme-overlay-strong)]/70 backdrop-blur-sm p-4 sm:p-8"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label="Quick search"
    >
      <div
        className="w-full max-w-2xl rounded-xl bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-card-border)] shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <form
          className="p-4 sm:p-5 space-y-3"
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit();
          }}
        >
          <div>
            <ArchiveSectionHeader
              title="Search cards"
              status="SEARCH_INDEX: READY"
              className="mb-2"
              titleClassName="text-lg sm:text-xl"
              action={
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={onClose}
                  aria-label="Close modal"
                >
                  Close
                </Button>
              }
            />
            <p className="text-xs sm:text-sm text-[color:var(--theme-text-secondary)]">
              Press <span className="font-mono">Enter</span> to open full
              search • <span className="font-mono">Esc</span> to close
            </p>
          </div>

          <div className="max-w-2xl">
            <SearchInput
              placeholder="Search for cards (e.g., Lightning Bolt, Jace, etc.)"
              value={query}
              onChange={setQuery}
              autoFocus
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setQuery("");
                onClose();
              }}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Search
            </Button>
          </div>
        </form>
      </div>
    </div>
  );

  return typeof window !== "undefined"
    ? createPortal(modalContent, document.body)
    : null;
}
