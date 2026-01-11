'use client';

// frontend/components/navigation/TopNavbar.tsx

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { topLevelNavItems, navGroups, standaloneNavItems, NavItem } from './navConfig';
import { NavDropdown } from './NavDropdown';
import { ThemeSwitcher } from '@/components/ui/ThemeSwitcher';
import { BookOpen, Menu, X, ChevronDown } from 'lucide-react';

interface TopNavbarProps {
  variant?: 'landing' | 'app';
  showSpacer?: boolean;
}

export function TopNavbar({ variant = 'app', showSpacer = true }: TopNavbarProps) {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [openMobileGroup, setOpenMobileGroup] = useState<string | null>(null);

  // Filter nav items based on authentication
  const visibleTopLevelItems = topLevelNavItems.filter(item => !item.requiresAuth || isAuthenticated);
  const visibleNavGroups = navGroups.filter(group => 
    group.items.some(item => !item.requiresAuth || isAuthenticated)
  );
  const visibleStandaloneItems = standaloneNavItems.filter(item => !item.requiresAuth || isAuthenticated);

  // Variant styles - theme-aware with glassmorphism
  const variantStyles = {
    landing: {
      container: 'bg-[color:var(--theme-card-bg)]/70 backdrop-blur-md',
      text: 'text-[color:var(--theme-text-primary)]',
      hover: '',
      active: 'text-[color:var(--theme-nav-active)] font-semibold border-b-2 border-[color:var(--theme-nav-active-border)] pb-2',
      logo: 'text-[color:var(--theme-text-primary)]',
      mobileBorder: 'border-white/20',
    },
    app: {
      container: 'bg-[color:var(--theme-card-bg)]/70 backdrop-blur-md',
      text: 'text-[color:var(--theme-text-secondary)]',
      hover: '',
      active: 'text-[color:var(--theme-nav-active)] font-semibold border-b-2 border-[color:var(--theme-nav-active-border)] pb-2',
      logo: 'text-[color:var(--theme-text-primary)]',
      mobileBorder: 'border-white/20',
    },
  };

  const styles = variantStyles[variant];

  const NavLink = ({ item }: { item: NavItem }) => {
    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

    return (
      <Link
        href={item.href}
        className={`
          flex items-center px-4 py-2 rounded-lg transition-colors relative group
          ${isActive ? styles.active : `${styles.text} hover:text-[color:var(--theme-nav-active)] hover:font-semibold`}
          ${isActive ? 'rounded-b-none -mb-[2px]' : 'group-hover:border-b-2 group-hover:border-[color:var(--theme-nav-active-border)] group-hover:pb-2 group-hover:rounded-b-none group-hover:-mb-[2px] border-b-2 border-transparent'}
        `}
        onClick={() => setIsMobileOpen(false)}
      >
        <span className="font-medium">{item.label}</span>
      </Link>
    );
  };

  return (
    <>
      <nav
        className={`
          fixed top-4 left-4 right-4 z-50
          ${styles.container}
          rounded-2xl
          transition-all
        `}
        style={{
          boxShadow: `0 2px 8px -4px var(--theme-accent-primary)`,
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 flex-shrink-0">
              <BookOpen className={`w-6 h-6 ${styles.logo}`} />
              <span className={`font-heading text-xl font-bold ${styles.logo} hidden sm:inline`}>
                MTG Engine
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-2 flex-1 justify-center">
              {/* Top-level items */}
              {visibleTopLevelItems.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
              
              {/* Grouped items (dropdowns) */}
              {visibleNavGroups.map((group) => (
                <NavDropdown key={group.label} group={group} variant={variant} />
              ))}
              
              {/* Standalone items */}
              {visibleStandaloneItems.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
            </div>

            {/* User Section */}
            <div className="flex items-center gap-2">
              {isAuthenticated ? (
                <div className="relative">
                  <button
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg transition-all cursor-pointer
                      ${styles.text} ${styles.hover}
                    `}
                  >
                    <span className="hidden sm:inline">{user?.username}</span>
                    <ChevronDown className="w-4 h-4" />
                  </button>
                  
                  {isUserMenuOpen && (
                    <>
                      <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsUserMenuOpen(false)}
                      />
                      <div className="absolute right-0 mt-2 w-56 bg-[color:var(--theme-card-bg)] rounded-lg shadow-xl border border-[color:var(--theme-card-border)] py-2 z-50">
                        <div className="px-4 py-2 border-b border-[color:var(--theme-border-default)]">
                          <ThemeSwitcher />
                        </div>
                        <button
                          onClick={() => {
                            logout();
                            setIsUserMenuOpen(false);
                          }}
                          className="w-full flex items-center px-4 py-2 text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] transition-colors cursor-pointer"
                        >
                          <span>Logout</span>
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <Link
                  href="/login"
                  className={`
                    flex items-center px-4 py-2 rounded-lg transition-all
                    ${styles.text} ${styles.hover}
                  `}
                >
                  <span className="hidden sm:inline">Login</span>
                </Link>
              )}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setIsMobileOpen(!isMobileOpen)}
                className={`
                  md:hidden p-2 rounded-lg transition-all
                  ${styles.text} ${styles.hover}
                `}
                aria-label="Toggle menu"
              >
                {isMobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileOpen && (
          <div className={`md:hidden border-t ${styles.mobileBorder} py-4`}>
            <div className="max-w-7xl mx-auto px-4 space-y-2">
              {/* Top-level items */}
              {visibleTopLevelItems.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
              
              {/* Grouped items (expandable sections) */}
              {visibleNavGroups.map((group) => {
                const visibleGroupItems = group.items.filter(item => !item.requiresAuth || isAuthenticated);
                if (visibleGroupItems.length === 0) return null;
                
                const isGroupOpen = openMobileGroup === group.label;
                const GroupIcon = group.icon;
                
                return (
                  <div key={group.label} className="space-y-1">
                    <button
                      onClick={() => setOpenMobileGroup(isGroupOpen ? null : group.label)}
                      className={`
                        w-full flex items-center justify-between px-4 py-2 rounded-lg transition-all
                        ${styles.text} ${styles.hover}
                      `}
                    >
                      <div className="flex items-center gap-2">
                        {GroupIcon && <GroupIcon className="w-4 h-4" />}
                        <span className="font-medium">{group.label}</span>
                      </div>
                      <ChevronDown
                        className={`
                          w-4 h-4 transition-transform
                          ${isGroupOpen ? 'transform rotate-180' : ''}
                        `}
                      />
                    </button>
                    {isGroupOpen && (
                      <div className="pl-6 space-y-1">
                        {visibleGroupItems.map((item) => (
                          <NavLink key={item.href} item={item} />
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
              
              {/* Standalone items */}
              {visibleStandaloneItems.map((item) => (
                <NavLink key={item.href} item={item} />
              ))}
              
              {!isAuthenticated && (
                <Link
                  href="/register"
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-lg transition-all
                    ${styles.text} ${styles.hover}
                  `}
                  onClick={() => setIsMobileOpen(false)}
                >
                  <span>Register</span>
                </Link>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Spacer for fixed navbar (accounting for top margin and height) - not needed on landing page */}
      {showSpacer && <div className="h-20" />}
    </>
  );
}

