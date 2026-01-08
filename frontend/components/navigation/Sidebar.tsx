'use client';

// frontend/components/navigation/Sidebar.tsx

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { useSidebar } from '@/context/SidebarContext';
import { Button } from '@/components/ui/Button';
import {
  LayoutDashboard,
  Search,
  Grid3x3,
  Layers,
  Code,
  BookOpen,
  Heart,
  Rocket,
  LogOut,
  Menu,
  X,
} from 'lucide-react';

interface NavItem {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  section?: string;
}

const navItems: NavItem[] = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', section: 'main' },
  { href: '/search', icon: Search, label: 'Search', section: 'main' },
  { href: '/browse', icon: Grid3x3, label: 'Browse', section: 'main' },
  { href: '/builder', icon: Code, label: 'Builder', section: 'build' },
  { href: '/decks', icon: BookOpen, label: 'Decks', section: 'build' },
  { href: '/templates', icon: Layers, label: 'Templates', section: 'build' },
  { href: '/my-cards', icon: Heart, label: 'My Cards', section: 'collections' },
  { href: '/getting-started', icon: Rocket, label: 'Getting Started', section: 'help' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { isCollapsed } = useSidebar();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  // Always collapsed unless hovering
  const isExpanded = isHovering;
  const sidebarWidth = isExpanded ? 'w-64' : 'w-16';

  // Group nav items by section
  const groupedItems = navItems.reduce((acc, item) => {
    const section = item.section || 'main';
    if (!acc[section]) acc[section] = [];
    acc[section].push(item);
    return acc;
  }, {} as Record<string, NavItem[]>);

  const NavLink = ({ item }: { item: NavItem }) => {
    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
    const Icon = item.icon;

    return (
      <Link
        href={item.href}
        className={`
          group relative flex items-center gap-3 px-3 h-10 rounded-lg transition-all overflow-hidden
          ${isActive
            ? 'bg-amber-600/20 text-amber-400 border-l-2 border-amber-500'
            : 'text-slate-300 hover:bg-slate-700 hover:text-white'
          }
          ${isExpanded ? 'w-full' : 'justify-center'}
        `}
        onClick={() => setIsMobileOpen(false)}
        title={!isExpanded ? item.label : undefined}
      >
        <Icon className="flex-shrink-0 w-5 h-5" />
        {isExpanded && (
          <span className="font-medium whitespace-nowrap overflow-hidden text-ellipsis">{item.label}</span>
        )}
      </Link>
    );
  };

  const sidebarContent = (
    <div
      className={`
        h-screen bg-slate-800 border-r border-slate-700
        flex flex-col transition-all duration-300 flex-shrink-0
        ${sidebarWidth}
        relative
      `}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-700 relative z-10 h-16 overflow-hidden">
        {isExpanded ? (
          <Link href="/dashboard" className="flex items-center gap-2 h-full">
            <BookOpen className="w-5 h-5 text-amber-500 flex-shrink-0" />
            <span className="font-heading text-lg font-bold text-white whitespace-nowrap overflow-hidden text-ellipsis">MTG Engine</span>
          </Link>
        ) : (
          <Link href="/dashboard" className="flex items-center justify-center w-full h-full">
            <BookOpen className="w-5 h-5 text-amber-500 flex-shrink-0" />
          </Link>
        )}
        {/* Mobile close button */}
        <button
          onClick={() => setIsMobileOpen(false)}
          className="md:hidden flex items-center justify-center w-8 h-8 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors flex-shrink-0"
          aria-label="Close menu"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-4 px-2 space-y-6 relative z-10">
        {Object.entries(groupedItems).map(([section, items]) => (
          <div key={section} className="overflow-x-hidden">
            <div className="px-3 mb-2 h-5 flex items-center flex-shrink-0">
              <div className={`h-px bg-slate-600 flex-shrink-0 ${isExpanded ? 'w-full' : 'w-8 mx-auto'}`} aria-label={section} />
            </div>
            <div className="space-y-1">
              {items.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* User Section */}
      <div className="border-t border-slate-700 p-4 relative z-10 min-h-[88px] overflow-hidden">
        {isExpanded ? (
          <div className="space-y-2">
            <div className="px-3 py-2 text-sm text-slate-400 h-8 flex items-center overflow-hidden">
              <span className="whitespace-nowrap overflow-hidden text-ellipsis">{user?.username}</span>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => logout()}
              className="w-full flex items-center justify-center gap-2 h-10"
            >
              <LogOut className="w-5 h-5" />
              Logout
            </Button>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <button
              onClick={() => logout()}
              className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition-colors h-10"
              aria-label="Logout"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
        aria-label="Open menu"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar - Always fixed position */}
      <aside
        className={`
          fixed
          left-0 top-0 h-screen z-40
          overflow-visible
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0
          transition-transform duration-300
        `}
      >
        {sidebarContent}
      </aside>
    </>
  );
}

