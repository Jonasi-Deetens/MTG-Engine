'use client';

// frontend/app/(protected)/layout.tsx

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';

function ProtectedLayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isDeckBuilder = pathname === '/decks/builder';
  
  return (
    <main className="min-h-screen relative z-10">
      <div className={isDeckBuilder ? 'w-full px-4 sm:px-6 lg:px-8 py-8' : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'}>
        {children}
      </div>
    </main>
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

