'use client';

// frontend/components/navigation/NavDropdown.tsx

import { useState, useRef, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ChevronDown } from 'lucide-react';
import { NavGroup } from './navConfig';
import { useAuth } from '@/context/AuthContext';

interface NavDropdownProps {
  group: NavGroup;
  variant?: 'landing' | 'app';
  onItemClick?: () => void;
}

export function NavDropdown({ group, variant = 'app', onItemClick }: NavDropdownProps) {
  const pathname = usePathname();
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter items based on authentication
  const visibleItems = group.items.filter(item => !item.requiresAuth || isAuthenticated);

  // Check if any child item is active
  const isActive = visibleItems.some(
    item => pathname === item.href || pathname.startsWith(item.href + '/')
  );

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const variantStyles = {
    landing: {
      text: 'text-[color:var(--theme-text-primary)]',
      active: 'text-[color:var(--theme-nav-active)] font-semibold',
      hover: 'hover:text-[color:var(--theme-nav-active)] hover:font-semibold',
    },
    app: {
      text: 'text-[color:var(--theme-text-secondary)]',
      active: 'text-[color:var(--theme-nav-active)] font-semibold',
      hover: 'hover:text-[color:var(--theme-nav-active)] hover:font-semibold',
    },
  };

  const styles = variantStyles[variant];

  if (visibleItems.length === 0) {
    return null;
  }

  const Icon = group.icon;

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg transition-colors relative group
          ${isActive ? styles.active : `${styles.text} ${styles.hover}`}
          ${isActive ? 'rounded-b-none -mb-[2px]' : 'group-hover:border-b-2 group-hover:border-[color:var(--theme-nav-active-border)] group-hover:pb-2 group-hover:rounded-b-none group-hover:-mb-[2px] border-b-2 border-transparent'}
        `}
      >
        <span className="font-medium">{group.label}</span>
        <ChevronDown
          className={`
            w-4 h-4 transition-transform
            ${isOpen ? 'transform rotate-180' : ''}
          `}
        />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-2 w-56 bg-[color:var(--theme-card-bg)] rounded-lg shadow-xl border border-[color:var(--theme-card-border)] py-2 z-50">
            {visibleItems.map((item) => {
              const ItemIcon = item.icon;
              const itemIsActive = pathname === item.href || pathname.startsWith(item.href + '/');

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => {
                    setIsOpen(false);
                    onItemClick?.();
                  }}
                  className={`
                    flex items-center gap-2 px-4 py-2 text-sm transition-colors
                    ${itemIsActive 
                      ? 'bg-[color:var(--theme-card-hover)] text-[color:var(--theme-accent-primary)] font-medium' 
                      : 'text-[color:var(--theme-text-secondary)] hover:bg-[color:var(--theme-card-hover)] hover:text-[color:var(--theme-text-primary)]'
                    }
                  `}
                >
                  {ItemIcon && <ItemIcon className="w-4 h-4 flex-shrink-0" />}
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}



