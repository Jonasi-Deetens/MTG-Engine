'use client';

// frontend/components/dashboard/QuickActions.tsx

import Link from 'next/link';
import { cn } from '@/lib/utils';
import { ArchiveSectionHeader } from '@/components/ui/ArchiveSectionHeader';
import { Search, Plus, Code, Layers, Folder } from 'lucide-react';

interface QuickAction {
  href: string;
  icon: typeof Search;
  title: string;
  description: string;
  shortcuts?: string[];
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
    shortcuts: ['Ctrl+Space', 'Cmd+K'],
    color: 'amber',
  },
  {
    href: '/decks',
    icon: Layers,
    title: 'Decks',
    description: 'View and manage your decks',
    shortcuts: ['G D'],
    color: 'green',
  },
  {
    href: '/my-cards/collections',
    icon: Folder,
    title: 'Collections',
    description: 'Manage your card collections',
    shortcuts: ['G C'],
    color: 'pink',
  },
  {
    href: '/decks/builder',
    icon: Plus,
    title: 'Create Deck',
    description: 'Build a new deck from scratch',
    shortcuts: ['N D'],
    color: 'blue',
  },
  {
    href: '/builder',
    icon: Code,
    title: 'Ability Builder',
    description: 'Create ability graphs',
    shortcuts: ['G B'],
    color: 'purple',
  },
];

export function QuickActions({
  title = 'Quick Actions',
  actions = defaultActions,
}: QuickActionsProps) {
  return (
    <div>
      <ArchiveSectionHeader title={title} status="ACTION_QUEUE: READY" />
      <div className="space-y-2">
        {actions.map((action) => {
          const Icon = action.icon;
          const shortcutKeys = action.shortcuts?.length
            ? action.shortcuts.flatMap((shortcut) =>
                shortcut
                  .split(/[+\s]/)
                  .map((key) => key.trim())
                  .filter(Boolean)
              )
            : [];
          return (
            <Link
              key={action.href}
              href={action.href}
              className={cn(
                'group relative flex items-center gap-3 w-full p-3',
                'bg-[color:var(--theme-card-bg)] border border-[color:var(--theme-border-default)]',
                'transition-all duration-200',
                'hover:bg-[color:var(--theme-bg-secondary)] hover:border-[color:var(--theme-text-primary)]',
                'focus:outline-none focus:border-[color:var(--theme-text-primary)]'
              )}
            >
              <div className="absolute left-0 top-0 w-[2px] h-full bg-transparent group-hover:bg-[color:var(--theme-text-primary)] transition-colors" />

              <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-[color:var(--theme-text-primary)] opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[color:var(--theme-text-primary)] opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-[color:var(--theme-text-primary)] opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-[color:var(--theme-text-primary)] opacity-0 group-hover:opacity-100 transition-opacity" />

              <div
                className={cn(
                  'relative flex items-center justify-center w-8 h-8',
                  'border border-[color:var(--theme-border-default)] group-hover:border-[color:var(--theme-text-primary)] transition-colors'
                )}
              >
                <div className="absolute inset-0 overflow-hidden">
                  <div className="absolute inset-x-0 h-px bg-[color:var(--theme-text-primary)]/30 -translate-y-full group-hover:translate-y-[2rem] transition-transform duration-500" />
                </div>
                <Icon className="w-4 h-4 text-[color:var(--theme-text-muted)] group-hover:text-[color:var(--theme-text-primary)] transition-colors" />
              </div>

              <div className="flex-1 text-left">
                <span className="font-mono text-xs tracking-[0.15em] text-[color:var(--theme-text-primary)] uppercase block">
                  {action.title}
                </span>
                <span className="text-xs text-[color:var(--theme-text-muted)]">
                  {action.description}
                </span>
              </div>

              {shortcutKeys.length > 0 && (
                <div className="flex items-center gap-1">
                  {shortcutKeys.map((key, index) => (
                    <span
                      key={`${action.href}-shortcut-${index}`}
                      className="font-mono text-[10px] tracking-wider text-[color:var(--theme-text-muted)] px-1.5 py-0.5 border border-[color:var(--theme-border-default)] bg-[color:var(--theme-bg-primary)]"
                    >
                      {key}
                    </span>
                  ))}
                </div>
              )}

              <div className="w-0 group-hover:w-2 overflow-hidden transition-all duration-200">
                <span className="text-[color:var(--theme-text-primary)] font-mono text-xs">&gt;</span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}

