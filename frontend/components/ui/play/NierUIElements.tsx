'use client';

import type { PropsWithChildren } from 'react';
interface BaseProps {
  className?: string;
}

export function BracketHeader({ children, className }: PropsWithChildren<BaseProps>) {
  return (
    <div className="inline-flex flex-col gap-1">
      <div
        className={`nier-bracket-header font-semibold text-[color:var(--theme-text-primary)] ml-2 ${className ?? ''}`.trim()}
      >
        <span className="nier-bracket-header-text text-[color:var(--theme-text-primary)]">
          {children}
        </span>
      </div>
      <DataLine className="w-full" />
    </div>
  );
}

interface HudValueProps extends BaseProps {
  label?: string;
  value: string | number;
  tone?: 'primary' | 'muted';
}

export function HudValue({ label, value, tone = 'primary', className }: HudValueProps) {
  const toneClass = tone === 'muted' ? 'nier-hud-muted' : 'nier-hud-primary';
  return (
    <div className={`nier-hud-value ${toneClass} ${className ?? ''}`.trim()}>
      {label && <div className="nier-hud-label">{label}</div>}
      <div className="nier-hud-number">{value}</div>
    </div>
  );
}

export function GlowIndicator({ className }: BaseProps) {
  return <span className={`nier-glow-indicator ${className ?? ''}`.trim()} aria-hidden="true" />;
}

export function GeometricDivider({ className }: BaseProps) {
  return <div className={`nier-divider ${className ?? ''}`.trim()} role="presentation" />;
}

export function DataLine({ className }: BaseProps) {
  return <div className={`nier-data-line ${className ?? ''}`.trim()} role="presentation" />;
}

interface StatusIndicatorProps extends BaseProps {
  tone?: 'primary' | 'muted' | 'alert';
  pulse?: boolean;
}

export function StatusIndicator({ tone = 'primary', pulse = false, className }: StatusIndicatorProps) {
  const toneClass =
    tone === 'alert' ? 'nier-status-alert' : tone === 'muted' ? 'nier-status-muted' : '';
  const pulseClass = pulse ? 'nier-status-pulse' : '';
  return (
    <span
      className={`nier-status-dot ${toneClass} ${pulseClass} ${className ?? ''}`.trim()}
      aria-hidden="true"
    />
  );
}

export function ScanlineOverlay({ className }: BaseProps) {
  return <span className={`nier-scanline ${className ?? ''}`.trim()} aria-hidden="true" />;
}
