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

export const navItems: NavItem[] = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', requiresAuth: true },
  { href: '/search', icon: Search, label: 'Search', requiresAuth: false },
  { href: '/browse', icon: Grid3x3, label: 'Browse', requiresAuth: false },
  { href: '/builder', icon: Code, label: 'Builder', requiresAuth: false },
  { href: '/decks', icon: BookOpen, label: 'Decks', requiresAuth: true },
  { href: '/templates', icon: Layers, label: 'Templates', requiresAuth: false },
  { href: '/my-cards', icon: Heart, label: 'My Cards', requiresAuth: true },
  { href: '/getting-started', icon: Rocket, label: 'Getting Started', requiresAuth: false },
];

