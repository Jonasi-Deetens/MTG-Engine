// frontend/components/navigation/navConfig.ts

import {
  LayoutDashboard,
  Search,
  Grid3x3,
  Layers,
  Code,
  BookOpen,
  Heart,
  Rocket,
} from 'lucide-react';

export interface NavItem {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  requiresAuth?: boolean;
}

export interface NavGroup {
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  items: NavItem[];
}

// Top-level navigation items (always visible)
export const topLevelNavItems: NavItem[] = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', requiresAuth: true },
  { href: '/search', icon: Search, label: 'Search', requiresAuth: false },
  { href: '/decks', icon: BookOpen, label: 'Decks', requiresAuth: true },
];

// Grouped navigation items
export const navGroups: NavGroup[] = [
  {
    label: 'Cards',
    icon: Grid3x3,
    items: [
      { href: '/my-cards', icon: Heart, label: 'My Cards', requiresAuth: true },
    ],
  },
  {
    label: 'Build',
    icon: Code,
    items: [
      { href: '/builder', icon: Code, label: 'Builder', requiresAuth: false },
      { href: '/templates', icon: Layers, label: 'Templates', requiresAuth: false },
    ],
  },
];

// Standalone items (not in groups)
export const standaloneNavItems: NavItem[] = [
  { href: '/getting-started', icon: Rocket, label: 'Getting Started', requiresAuth: false },
];

// Legacy: All items flattened (for backward compatibility if needed)
export const navItems: NavItem[] = [
  ...topLevelNavItems,
  ...navGroups.flatMap(group => group.items),
  ...standaloneNavItems,
];

