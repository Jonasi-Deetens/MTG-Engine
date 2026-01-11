'use client';

// frontend/components/dashboard/QuickActions.tsx

import { QuickActionCard } from './QuickActionCard';
import { Search, Plus, Code } from 'lucide-react';

interface QuickAction {
  href: string;
  icon: typeof Search;
  title: string;
  description: string;
  color?: 'amber' | 'blue' | 'purple' | 'green' | 'pink' | 'red';
}

interface QuickActionsProps {
  title?: string;
  actions?: QuickAction[];
}

const defaultActions: QuickAction[] = [
  {
    href: '/search',
    icon: Search,
    title: 'Search Cards',
    description: 'Search and browse all cards',
    color: 'amber',
  },
  {
    href: '/decks/builder',
    icon: Plus,
    title: 'Create Deck',
    description: 'Build a new deck from scratch',
    color: 'blue',
  },
  {
    href: '/builder',
    icon: Code,
    title: 'Ability Builder',
    description: 'Create ability graphs',
    color: 'purple',
  },
];

export function QuickActions({
  title = 'Quick Actions',
  actions = defaultActions,
}: QuickActionsProps) {
  return (
    <div>
      <h2 className="font-heading text-2xl font-bold text-[color:var(--theme-text-primary)] mb-4">{title}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {actions.map((action) => (
          <QuickActionCard
            key={action.href}
            href={action.href}
            icon={action.icon}
            title={action.title}
            description={action.description}
            color={action.color}
          />
        ))}
      </div>
    </div>
  );
}

