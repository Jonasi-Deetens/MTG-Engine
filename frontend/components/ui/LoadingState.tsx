import { cn } from "@/lib/utils";

interface LoadingStateProps {
  label?: string;
  className?: string;
  fullScreen?: boolean;
}

export function LoadingState({
  label = "SCANNING DATABASE...",
  className,
  fullScreen = true,
}: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center py-20",
        fullScreen && "min-h-screen",
        className
      )}
    >
      <div className="text-center">
        <div className="relative w-16 h-16 mx-auto mb-4">
          <div
            className="absolute inset-0 border border-foreground/30 animate-spin"
            style={{ animationDuration: "3s" }}
          />
          <div
            className="absolute inset-2 border border-foreground/50 animate-spin"
            style={{ animationDuration: "2s", animationDirection: "reverse" }}
          />
          <div
            className="absolute inset-4 border border-foreground animate-spin"
            style={{ animationDuration: "1s" }}
          />
        </div>
        <div className="font-mono text-sm tracking-[0.2em] text-muted-foreground">
          {label}
        </div>
      </div>
    </div>
  );
}
