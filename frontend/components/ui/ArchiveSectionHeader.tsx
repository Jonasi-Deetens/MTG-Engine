import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

interface ArchiveSectionHeaderProps {
  title: string;
  status: string;
  action?: ReactNode;
  className?: string;
  titleClassName?: string;
}

export function ArchiveSectionHeader({
  title,
  status,
  action,
  className,
  titleClassName,
}: ArchiveSectionHeaderProps) {
  return (
    <div className={cn("flex flex-col gap-3 mb-4 sm:flex-row sm:items-center sm:gap-4", className)}>
      <div className="flex items-center gap-3 min-w-0">
        <div className="w-2 h-2 bg-[color:var(--theme-text-primary)] animate-pulse shrink-0" />
        <h2
          className={cn(
            "font-mono text-lg sm:text-xl tracking-[0.2em] uppercase text-[color:var(--theme-text-primary)] min-w-0",
            titleClassName
          )}
        >
          {title}
        </h2>
      </div>
      <div className="hidden sm:block flex-1 h-px bg-[color:var(--theme-text-primary)]/30" />
      <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:flex-wrap sm:items-center sm:gap-3 sm:shrink-0">
        <div className="font-mono text-xs tracking-wider text-[color:var(--theme-accent-secondary)] uppercase">
          {status}
        </div>
        {action ? (
          <div className="flex w-full items-center gap-2 sm:ml-auto sm:w-auto [&_button]:w-full sm:[&_button]:w-auto [&_a]:w-full sm:[&_a]:w-auto">
            {action}
          </div>
        ) : null}
      </div>
    </div>
  );
}
