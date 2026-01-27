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
    <div className={cn("flex items-center gap-4 mb-4", className)}>
      <div className="w-2 h-2 bg-[color:var(--theme-text-primary)] animate-pulse shrink-0" />
      <h2
        className={cn(
          "font-mono text-xl tracking-[0.2em] uppercase text-[color:var(--theme-text-primary)] min-w-0",
          titleClassName
        )}
      >
        {title}
      </h2>
      <div className="flex-1 h-px bg-[color:var(--theme-text-primary)]/30" />
      <div className="flex items-center gap-3 shrink-0">
        <div className="font-mono text-xs tracking-wider text-[color:var(--theme-accent-secondary)] uppercase">
          {status}
        </div>
        {action ? <div className="flex items-center gap-2">{action}</div> : null}
      </div>
    </div>
  );
}
