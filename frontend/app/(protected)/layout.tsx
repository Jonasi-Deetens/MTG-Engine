'use client';

// frontend/app/(protected)/layout.tsx

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { SidebarProvider } from '@/context/SidebarContext';
import { Sidebar } from '@/components/navigation/Sidebar';

function ProtectedLayoutContent({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-slate-900 overflow-x-hidden">
      {/* Sidebar - Fixed position, overlays content */}
      <Sidebar />

      {/* Main Content - Fixed margin for collapsed sidebar (expanded sidebar overlays) */}
      <main className="min-h-screen overflow-x-hidden md:ml-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-16 md:pt-8">
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
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <SidebarProvider>
      <ProtectedLayoutContent>{children}</ProtectedLayoutContent>
    </SidebarProvider>
  );
}

