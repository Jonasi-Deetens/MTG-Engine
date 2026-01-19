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

type ShortcutContextValue = {
  openQuickSearch: () => void;
  closeQuickSearch: () => void;
  toggleQuickSearch: () => void;
  isQuickSearchOpen: boolean;
};

const ShortcutContext = createContext<ShortcutContextValue | null>(null);

function isEditableTarget(target: EventTarget | null) {
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

  const openQuickSearch = useCallback(() => setIsOpen(true), []);
  const closeQuickSearch = useCallback(() => {
    setIsOpen(false);
    setQuery("");
  }, []);
  const toggleQuickSearch = useCallback(() => setIsOpen((v) => !v), []);

  const submit = useCallback(() => {
    const q = query.trim();
    closeQuickSearch();
    router.push(q ? `/search?q=${encodeURIComponent(q)}` : "/search");
  }, [closeQuickSearch, query, router]);

  useEffect(() => {
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
      }
    };

    window.addEventListener("keydown", onKeyDown, { passive: false });
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [enableCmdK]);

  const value = useMemo<ShortcutContextValue>(
    () => ({
      openQuickSearch,
      closeQuickSearch,
      toggleQuickSearch,
      isQuickSearchOpen: isOpen,
    }),
    [closeQuickSearch, openQuickSearch, toggleQuickSearch, isOpen]
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
    </ShortcutContext.Provider>
  );
}

export function useShortcuts() {
  const ctx = useContext(ShortcutContext);
  if (!ctx)
    throw new Error("useShortcuts must be used within <ShortcutProvider />");
  return ctx;
}
