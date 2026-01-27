"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { QuickSearchModal } from "@/components/ui/QuickSearchModal";
import { ShortcutHelpModal } from "@/components/ui/ShortcutHelpModal";
import { GameModal } from "@/components/ui/GameModal";

type ShortcutContextValue = {
  openQuickSearch: () => void;
  closeQuickSearch: () => void;
  toggleQuickSearch: () => void;
  isQuickSearchOpen: boolean;
  openShortcutHelp: () => void;
  closeShortcutHelp: () => void;
  isShortcutHelpOpen: boolean;
};

const ShortcutContext = createContext<ShortcutContextValue | null>(null);

export function isEditableTarget(target: EventTarget | null) {
  const el = target as HTMLElement | null;
  if (!el) return false;

  const tag = el.tagName?.toLowerCase();
  if (tag === "input" || tag === "textarea" || tag === "select") return true;
  if (el.isContentEditable) return true;

  // common for custom editors
  if (el.getAttribute?.("role") === "textbox") return true;

  return false;
}

type ShortcutProviderProps = {
  children: ReactNode;
  enableCmdK?: boolean; // optional extra shortcut
};

export function ShortcutProvider({
  children,
  enableCmdK = true,
}: ShortcutProviderProps) {
  const router = useRouter();

  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isGameOpen, setIsGameOpen] = useState(false);

  const openQuickSearch = useCallback(() => setIsOpen(true), []);
  const closeQuickSearch = useCallback(() => {
    setIsOpen(false);
    setQuery("");
  }, []);
  const toggleQuickSearch = useCallback(() => setIsOpen((v) => !v), []);
  const openShortcutHelp = useCallback(() => setIsHelpOpen(true), []);
  const closeShortcutHelp = useCallback(() => setIsHelpOpen(false), []);
  const openGame = useCallback(() => setIsGameOpen(true), []);
  const closeGame = useCallback(() => setIsGameOpen(false), []);

  const submit = useCallback(() => {
    const q = query.trim();
    closeQuickSearch();
    router.push(q ? `/search?q=${encodeURIComponent(q)}` : "/search");
  }, [closeQuickSearch, query, router]);

  useEffect(() => {
    const sequenceWindowMs = 500;
    let pendingKey: { key: string; time: number } | null = null;

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.isComposing) return;
      if (isEditableTarget(e.target)) return;

      const ctrlSpace = e.ctrlKey && e.code === "Space";
      const cmdK =
        enableCmdK && (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k";

      if (ctrlSpace || cmdK) {
        e.preventDefault();
        e.stopPropagation();
        setIsOpen(true);
        return;
      }

      if (e.altKey && !e.ctrlKey && !e.metaKey) {
        const key = e.key.toLowerCase();
        if (key === "d") {
          e.preventDefault();
          e.stopPropagation();
          const lastDeckId =
            typeof window !== "undefined"
              ? window.localStorage.getItem("lastDeckId")
              : null;
          router.push(lastDeckId ? `/decks/builder?deck=${lastDeckId}` : "/decks");
        }
        return;
      }

      if (e.metaKey || e.ctrlKey) {
        return;
      }

      const key = e.key.toLowerCase();
      if (key === "?") {
        e.preventDefault();
        e.stopPropagation();
        setIsHelpOpen(true);
        return;
      }

      const now = Date.now();
      if (pendingKey && now - pendingKey.time <= sequenceWindowMs) {
        const sequence = `${pendingKey.key}${key}`;
        if (sequence === "gc") {
          e.preventDefault();
          e.stopPropagation();
          router.push("/my-cards/collections");
          pendingKey = null;
          return;
        }
        if (sequence === "gd") {
          e.preventDefault();
          e.stopPropagation();
          router.push("/decks");
          pendingKey = null;
          return;
        }
        if (sequence === "gb") {
          e.preventDefault();
          e.stopPropagation();
          router.push("/builder");
          pendingKey = null;
          return;
        }
        if (sequence === "gg") {
          e.preventDefault();
          e.stopPropagation();
          openGame();
          pendingKey = null;
          return;
        }
        if (sequence === "nd") {
          e.preventDefault();
          e.stopPropagation();
          router.push("/decks/builder");
          pendingKey = null;
          return;
        }
      }

      if (key === "g" || key === "n") {
        pendingKey = { key, time: now };
      } else {
        pendingKey = null;
      }
    };

    window.addEventListener("keydown", onKeyDown, { passive: false });
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [enableCmdK, openGame, router]);

  const value = useMemo<ShortcutContextValue>(
    () => ({
      openQuickSearch,
      closeQuickSearch,
      toggleQuickSearch,
      isQuickSearchOpen: isOpen,
      openShortcutHelp,
      closeShortcutHelp,
      isShortcutHelpOpen: isHelpOpen,
    }),
    [closeQuickSearch, openQuickSearch, toggleQuickSearch, isOpen, openShortcutHelp, closeShortcutHelp, isHelpOpen]
  );

  return (
    <ShortcutContext.Provider value={value}>
      {children}
      <QuickSearchModal
        isOpen={isOpen}
        onClose={closeQuickSearch}
        query={query}
        setQuery={setQuery}
        onSubmit={submit}
      />
      <button
        type="button"
        onClick={openShortcutHelp}
        className="fixed bottom-5 right-5 z-[10001] h-12 w-12 rounded-full bg-[color:var(--theme-button-primary-bg)] text-[color:var(--theme-button-primary-text)] shadow-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-[color:var(--theme-border-focus)] flex items-center justify-center"
        aria-label="Open shortcut help"
      >
        ?
      </button>
      <ShortcutHelpModal isOpen={isHelpOpen} onClose={closeShortcutHelp} />
      <GameModal isOpen={isGameOpen} onClose={closeGame} />
    </ShortcutContext.Provider>
  );
}

export function useShortcuts() {
  const ctx = useContext(ShortcutContext);
  if (!ctx)
    throw new Error("useShortcuts must be used within <ShortcutProvider />");
  return ctx;
}
