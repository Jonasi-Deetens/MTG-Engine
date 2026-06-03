"use client";

import { useEffect, useMemo, useRef } from "react";
import { cn } from "@/lib/utils";

export function NierGridBackground({ className }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(var(--theme-text-primary) 1px, transparent 1px),
            linear-gradient(90deg, var(--theme-text-primary) 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
        }}
      />

      <div
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(var(--theme-text-primary) 1px, transparent 1px),
            linear-gradient(90deg, var(--theme-text-primary) 1px, transparent 1px)
          `,
          backgroundSize: "120px 120px",
        }}
      />

      <div className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-[color:var(--theme-text-primary)]/20 to-transparent animate-[scanVertical_8s_linear_infinite]" />
      <div className="absolute top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-[color:var(--theme-text-primary)]/20 to-transparent animate-[scanHorizontal_12s_linear_infinite]" />

      <style jsx>{`
        @keyframes scanVertical {
          0% {
            top: -1px;
          }
          100% {
            top: 100%;
          }
        }
        @keyframes scanHorizontal {
          0% {
            left: -1px;
          }
          100% {
            left: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export function NierGeometricBackground({ className }: { className?: string }) {
  const leftDiamonds = useMemo(
    () =>
      [...Array(6)].map((_, i) => ({
        key: i,
        size: 80 + i * 60,
        top: 10 + i * 12,
        left: 5 + i * 15,
      })),
    []
  );

  const rightDiamonds = useMemo(
    () =>
      [...Array(4)].map((_, i) => ({
        key: i,
        size: 60 + i * 40,
        top: 20 + i * 18,
        right: 8 + i * 10,
      })),
    []
  );

  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      {leftDiamonds.map((item) => (
        <div
          key={item.key}
          className="absolute border border-[color:var(--theme-text-primary)]/5 rotate-45"
          style={{
            width: `${item.size}px`,
            height: `${item.size}px`,
            top: `${item.top}%`,
            left: `${item.left}%`,
          }}
        />
      ))}

      {rightDiamonds.map((item) => (
        <div
          key={`r-${item.key}`}
          className="absolute border border-[color:var(--theme-text-primary)]/5 rotate-45"
          style={{
            width: `${item.size}px`,
            height: `${item.size}px`,
            top: `${item.top}%`,
            right: `${item.right}%`,
          }}
        />
      ))}

      <div className="absolute top-8 left-8 w-24 h-24">
        <div className="absolute top-0 left-0 w-8 h-px bg-[color:var(--theme-text-primary)]/10" />
        <div className="absolute top-0 left-0 w-px h-8 bg-[color:var(--theme-text-primary)]/10" />
      </div>

      <div className="absolute top-8 right-8 w-24 h-24">
        <div className="absolute top-0 right-0 w-8 h-px bg-[color:var(--theme-text-primary)]/10" />
        <div className="absolute top-0 right-0 w-px h-8 bg-[color:var(--theme-text-primary)]/10" />
      </div>

      <div className="absolute bottom-8 left-8 w-24 h-24">
        <div className="absolute bottom-0 left-0 w-8 h-px bg-[color:var(--theme-text-primary)]/10" />
        <div className="absolute bottom-0 left-0 w-px h-8 bg-[color:var(--theme-text-primary)]/10" />
      </div>

      <div className="absolute bottom-8 right-8 w-24 h-24">
        <div className="absolute bottom-0 right-0 w-8 h-px bg-[color:var(--theme-text-primary)]/10" />
        <div className="absolute bottom-0 right-0 w-px h-8 bg-[color:var(--theme-text-primary)]/10" />
      </div>
    </div>
  );
}

export function NierVignetteBackground({ className }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 pointer-events-none", className)}>
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 0%, transparent 50%, var(--theme-bg-primary) 100%)",
        }}
      />

      <div
        className="absolute inset-0 opacity-30"
        style={{
          background:
            "radial-gradient(ellipse at center, var(--theme-card-bg) 0%, transparent 60%)",
        }}
      />
    </div>
  );
}

export function NierCircuitBackground({ className }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      <svg
        className="absolute inset-0 w-full h-full opacity-[0.03]"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern id="circuit" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
            <line x1="0" y1="20" x2="30" y2="20" stroke="currentColor" strokeWidth="1" />
            <line x1="40" y1="20" x2="100" y2="20" stroke="currentColor" strokeWidth="1" />
            <line x1="0" y1="50" x2="60" y2="50" stroke="currentColor" strokeWidth="1" />
            <line x1="70" y1="50" x2="100" y2="50" stroke="currentColor" strokeWidth="1" />
            <line x1="0" y1="80" x2="20" y2="80" stroke="currentColor" strokeWidth="1" />
            <line x1="50" y1="80" x2="100" y2="80" stroke="currentColor" strokeWidth="1" />

            <line x1="30" y1="20" x2="30" y2="50" stroke="currentColor" strokeWidth="1" />
            <line x1="60" y1="50" x2="60" y2="80" stroke="currentColor" strokeWidth="1" />
            <line x1="20" y1="80" x2="20" y2="100" stroke="currentColor" strokeWidth="1" />

            <circle cx="30" cy="20" r="2" fill="currentColor" />
            <circle cx="40" cy="20" r="2" fill="currentColor" />
            <circle cx="60" cy="50" r="2" fill="currentColor" />
            <circle cx="70" cy="50" r="2" fill="currentColor" />
            <circle cx="20" cy="80" r="2" fill="currentColor" />
            <circle cx="50" cy="80" r="2" fill="currentColor" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#circuit)" />
      </svg>
    </div>
  );
}

export function NierParticleBackground({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    const particles: {
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      alpha: number;
    }[] = [];
    const particleCount = 50;

    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: Math.random() * 2 + 1,
        alpha: Math.random() * 0.3 + 0.1,
      });
    }

    let animationId: number;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const style = getComputedStyle(document.documentElement);
      const color = style.getPropertyValue("--theme-text-primary").trim() || "#454138";

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.globalAlpha = p.alpha;
        ctx.fill();
      });

      ctx.globalAlpha = 0.03;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return <canvas ref={canvasRef} className={cn("absolute inset-0 pointer-events-none", className)} />;
}

export function NierDataLinesBackground({ className }: { className?: string }) {
  const dataLines = useMemo(
    () =>
      [...Array(12)].map((_, i) => ({
        key: i,
        top: 8 + i * 8,
        maxWidth: 20 + Math.random() * 30,
        extraWidth: 5 + Math.random() * 15,
        extraLongWidth: 10 + Math.random() * 20,
      })),
    []
  );

  const rightLines = useMemo(
    () =>
      [...Array(8)].map((_, i) => ({
        key: i,
        top: 15 + i * 10,
        width: 10 + Math.random() * 25,
      })),
    []
  );

  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      {dataLines.map((line) => (
        <div
          key={line.key}
          className="absolute left-0 right-0 flex items-center gap-2"
          style={{ top: `${line.top}%` }}
        >
          <div
            className="h-px bg-[color:var(--theme-text-primary)]/5 flex-1"
            style={{ maxWidth: `${line.maxWidth}%` }}
          />
          <div className="w-1 h-1 bg-[color:var(--theme-text-primary)]/10" />
          <div
            className="h-px bg-[color:var(--theme-text-primary)]/5"
            style={{ width: `${line.extraWidth}%` }}
          />
          {line.key % 3 === 0 && (
            <>
              <div className="w-1.5 h-1.5 border border-[color:var(--theme-text-primary)]/10 rotate-45" />
              <div
                className="h-px bg-[color:var(--theme-text-primary)]/5"
                style={{ width: `${line.extraLongWidth}%` }}
              />
            </>
          )}
        </div>
      ))}

      {rightLines.map((line) => (
        <div
          key={`r-${line.key}`}
          className="absolute right-0 flex items-center justify-end gap-2"
          style={{ top: `${line.top}%` }}
        >
          <div className="h-px bg-[color:var(--theme-text-primary)]/5" style={{ width: `${line.width}%` }} />
          <div className="w-1 h-1 bg-[color:var(--theme-text-primary)]/10" />
        </div>
      ))}
    </div>
  );
}

export function NierPremiumBackground({ className }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 pointer-events-none", className)}>
      <NierGridBackground />
      <NierGeometricBackground />
      <NierVignetteBackground />
      <NierDataLinesBackground />
    </div>
  );
}
