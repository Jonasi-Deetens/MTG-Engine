'use client';

// frontend/components/dashboard/QuickActionCard.tsx

import Link from 'next/link';
import { Card } from '@/components/ui/Card';
import { HoverShadow } from '@/components/ui/HoverShadow';
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
  },
  blue: {
    iconBg: 'bg-[color:var(--theme-status-info)]/10 border-[color:var(--theme-status-info)]/20 group-hover:bg-[color:var(--theme-status-info)]/20',
    iconColor: 'text-[color:var(--theme-status-info)]',
  },
  purple: {
    iconBg: 'bg-[color:var(--theme-accent-secondary)]/10 border-[color:var(--theme-accent-secondary)]/20 group-hover:bg-[color:var(--theme-accent-secondary)]/20',
    iconColor: 'text-[color:var(--theme-accent-secondary)]',
  },
  green: {
    iconBg: 'bg-[color:var(--theme-status-success)]/10 border-[color:var(--theme-status-success)]/20 group-hover:bg-[color:var(--theme-status-success)]/20',
    iconColor: 'text-[color:var(--theme-status-success)]',
  },
  pink: {
    iconBg: 'bg-[color:var(--theme-accent-secondary)]/10 border-[color:var(--theme-accent-secondary)]/20 group-hover:bg-[color:var(--theme-accent-secondary)]/20',
    iconColor: 'text-[color:var(--theme-accent-secondary)]',
  },
  red: {
    iconBg: 'bg-[color:var(--theme-status-error)]/10 border-[color:var(--theme-status-error)]/20 group-hover:bg-[color:var(--theme-status-error)]/20',
    iconColor: 'text-[color:var(--theme-status-error)]',
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
        <HoverShadow />
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

