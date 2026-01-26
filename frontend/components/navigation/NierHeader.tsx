"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { navItems as appNavItems } from "@/components/navigation/navConfig";

interface NierHeaderProps {
  showSpacer?: boolean;
}

export function NierHeader({ showSpacer = true }: NierHeaderProps) {
  const pathname = usePathname();
  const { isAuthenticated, logout } = useAuth();
  const [time, setTime] = useState("00:00:00");
  const [date, setDate] = useState("0000.00.00");
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(now.toLocaleTimeString("en-US", { hour12: false }));
      setDate(
        `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, "0")}.${String(
          now.getDate()
        ).padStart(2, "0")}`
      );
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = useMemo(() => {
    return appNavItems.filter((item) => (item.requiresAuth ? isAuthenticated : true));
  }, [isAuthenticated]);

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 bg-[color:var(--theme-card-bg)]/70 backdrop-blur-md border-b border-[color:var(--theme-border-default)]/50">
        <div className="mx-auto max-w-[1600px] flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="group nier-frame p-3 transition-colors hover:bg-[color:var(--theme-button-primary-bg)]"
              onClick={() => setMobileOpen(false)}
            >
              <span className="font-mono text-sm tracking-[0.3em] text-[color:var(--theme-text-primary)] transition-colors group-hover:text-[color:var(--theme-button-primary-text)]">
                MTG
              </span>
            </Link>
            <div className="hidden sm:block h-8 w-px bg-[color:var(--theme-border-default)]/60" />
            <span className="hidden sm:block font-mono text-xs text-[color:var(--theme-text-muted)] tracking-wider">
              SIMULATOR
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-6 lg:gap-8">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group relative font-mono text-xs tracking-[0.2em] transition-colors ${
                    isActive
                      ? "text-[color:var(--theme-text-primary)]"
                      : "text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]"
                  }`}
                >
                  <span className="relative z-10">{item.label.toUpperCase()}</span>
                  <span className="absolute bottom-0 left-0 w-0 h-px bg-[color:var(--theme-border-default)] group-hover:w-full transition-all duration-300" />
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-6">
            <button
              type="button"
              onClick={() => setMobileOpen((prev) => !prev)}
              className="md:hidden font-mono text-xs tracking-[0.2em] text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] transition-colors"
              aria-expanded={mobileOpen}
              aria-label={mobileOpen ? "Close navigation menu" : "Open navigation menu"}
            >
              {mobileOpen ? "CLOSE" : "MENU"}
            </button>
            <div className="hidden lg:flex flex-col items-end font-mono text-xs text-[color:var(--theme-text-muted)]">
              <span>{date}</span>
              <span>{time}</span>
            </div>
            {isAuthenticated ? (
              <button
                type="button"
                onClick={logout}
                className="font-mono text-xs tracking-[0.2em] text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] transition-colors"
              >
                LOGOUT
              </button>
            ) : (
              <Link
                href="/login"
                className="font-mono text-xs tracking-[0.2em] text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)] transition-colors"
              >
                LOGIN
              </Link>
            )}
            <div className="nier-frame p-2">
              <div className="w-3 h-3 bg-[color:var(--theme-text-primary)] animate-pulse" />
            </div>
          </div>
        </div>
        <div
          className={`md:hidden border-t border-[color:var(--theme-border-default)]/50 bg-[color:var(--theme-card-bg)]/90 backdrop-blur-md ${
            mobileOpen ? "block" : "hidden"
          }`}
        >
          <div className="px-6 py-4 space-y-3">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center justify-between font-mono text-xs tracking-[0.2em] transition-colors ${
                    isActive
                      ? "text-[color:var(--theme-text-primary)]"
                      : "text-[color:var(--theme-text-secondary)] hover:text-[color:var(--theme-text-primary)]"
                  }`}
                >
                  <span>{item.label.toUpperCase()}</span>
                  <span className="text-[color:var(--theme-text-muted)]">→</span>
                </Link>
              );
            })}
          </div>
        </div>
      </header>

      {showSpacer && <div className="h-20" />}
    </>
  );
}
