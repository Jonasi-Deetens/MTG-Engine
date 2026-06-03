// frontend/components/ui/HoverShadow.tsx

interface HoverShadowProps {
  className?: string;
  rounded?: string;
}

export function HoverShadow({ className = '', rounded = 'rounded-lg' }: HoverShadowProps) {
  return (
    <div 
      className={`absolute inset-0 ${rounded} opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-0 ${className}`}
      style={{
        boxShadow: `0 4px 20px -4px var(--theme-accent-primary)`,
      }}
    />
  );
}

