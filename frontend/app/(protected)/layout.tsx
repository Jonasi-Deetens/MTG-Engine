'use client';

// frontend/app/(protected)/layout.tsx

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useThemeImage } from '@/hooks/useThemeImage';

function ProtectedLayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isDeckBuilder = pathname === '/decks/builder';
  const isDashboard = pathname === '/dashboard';
  const isDecksPage = pathname?.startsWith('/decks') ?? false;
  const isMyCardsPage = pathname?.startsWith('/my-cards') ?? false;
  const dashboardBackgroundImage = useThemeImage('dashboard');
  const decksBackgroundImage = useThemeImage('decks');
  const collectionBackgroundImage = useThemeImage('collection');
  
  const getBackgroundStyle = () => {
    if (isDashboard) {
      return {
        backgroundImage: `url('${dashboardBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isDecksPage) {
      return {
        backgroundImage: `url('${decksBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    if (isMyCardsPage) {
      return {
        backgroundImage: `url('${collectionBackgroundImage}')`,
        backgroundSize: 'cover',
        backgroundPosition: 'top center',
        backgroundRepeat: 'no-repeat',
        backgroundAttachment: 'fixed',
      };
    }
    return {
      backgroundColor: 'var(--theme-bg-primary)',
    };
  };
  
  return (
    <div 
      className="min-h-screen overflow-x-hidden relative"
      style={getBackgroundStyle()}
    >
      {/* Main Content - Navbar is handled by NavbarWrapper in root layout */}
      <main className="min-h-screen relative z-10">
        <div className={isDeckBuilder ? 'w-full px-4 sm:px-6 lg:px-8 py-8' : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'}>
          {children}
        </div>
      </main>
    </div>
  );
}

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [loading, isAuthenticated, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[color:var(--theme-bg-primary)]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[color:var(--theme-accent-primary)]"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <ProtectedLayoutContent>{children}</ProtectedLayoutContent>;
}

