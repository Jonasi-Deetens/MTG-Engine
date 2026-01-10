'use client';

// frontend/components/dashboard/QuickActionCard.tsx

import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { LucideIcon } from 'lucide-react';

interface QuickActionCardProps {
  href: string;
  icon: LucideIcon;
  title: string;
  description: string;
  color?: 'amber' | 'blue' | 'purple' | 'green' | 'pink' | 'red';
}

const colorClasses = {
  amber: {
    iconBg: 'bg-[color:var(--theme-accent-primary)]/10 border-[color:var(--theme-accent-primary)]/20 group-hover:bg-[color:var(--theme-accent-primary)]/20',
    iconColor: 'text-[color:var(--theme-accent-primary)]',
    hoverGradient: 'from-theme-accent-hover/10',
    hoverShadow: 'hover:shadow-theme-accent-primary/20',
    hoverBorder: 'hover:border-[color:var(--theme-border-hover)]',
  },
  blue: {
    iconBg: 'bg-blue-500/10 border-blue-500/20 group-hover:bg-blue-500/20',
    iconColor: 'text-blue-500',
    hoverGradient: 'from-blue-600/10',
    hoverShadow: 'hover:shadow-blue-900/20',
    hoverBorder: 'hover:border-blue-500/50',
  },
  purple: {
    iconBg: 'bg-purple-500/10 border-purple-500/20 group-hover:bg-purple-500/20',
    iconColor: 'text-purple-500',
    hoverGradient: 'from-purple-600/10',
    hoverShadow: 'hover:shadow-purple-900/20',
    hoverBorder: 'hover:border-purple-500/50',
  },
  green: {
    iconBg: 'bg-green-500/10 border-green-500/20 group-hover:bg-green-500/20',
    iconColor: 'text-green-500',
    hoverGradient: 'from-green-600/10',
    hoverShadow: 'hover:shadow-green-900/20',
    hoverBorder: 'hover:border-green-500/50',
  },
  pink: {
    iconBg: 'bg-pink-500/10 border-pink-500/20 group-hover:bg-pink-500/20',
    iconColor: 'text-pink-500',
    hoverGradient: 'from-pink-600/10',
    hoverShadow: 'hover:shadow-pink-900/20',
    hoverBorder: 'hover:border-pink-500/50',
  },
  red: {
    iconBg: 'bg-red-500/10 border-red-500/20 group-hover:bg-red-500/20',
    iconColor: 'text-red-500',
    hoverGradient: 'from-red-600/10',
    hoverShadow: 'hover:shadow-red-900/20',
    hoverBorder: 'hover:border-red-500/50',
  },
};

export function QuickActionCard({
  href,
  icon: Icon,
  title,
  description,
  color = 'amber',
}: QuickActionCardProps) {
  const colors = colorClasses[color];

  return (
    <Link href={href}>
      <Card
        variant="elevated"
        className={`
          relative overflow-visible p-6 
          hover:scale-105
          transition-all duration-200 cursor-pointer h-full group 
          border-0
        `}
      >
        {/* Theme-colored drop shadow on hover */}
        <div className="absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none" 
             style={{
               boxShadow: `0 4px 20px -4px var(--theme-accent-primary)`,
             }}
        />
        <div className="text-center relative z-10">
          <div
            className={`inline-flex p-3 rounded-xl ${colors.iconBg} mb-4 transition-colors`}
          >
            <Icon className={`w-8 h-8 ${colors.iconColor}`} />
          </div>
          <h3 className="font-semibold text-[color:var(--theme-text-primary)] mb-1">{title}</h3>
          <p className="text-sm text-[color:var(--theme-text-secondary)]">{description}</p>
        </div>
      </Card>
    </Link>
  );
}

