'use client';

// frontend/app/(protected)/layout.tsx

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading, logout, isAuthenticated } = useAuth();
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
    <div className="min-h-screen bg-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="font-heading text-xl font-bold text-white">
                MTG Engine
              </Link>
              <Link
                href="/dashboard"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Dashboard
              </Link>
              <Link
                href="/search"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Search
              </Link>
              <Link
                href="/browse"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Browse
              </Link>
              <Link
                href="/templates"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Templates
              </Link>
              <Link
                href="/builder"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Builder
              </Link>
              <Link
                href="/decks"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Decks
              </Link>
              <Link
                href="/my-cards"
                className="text-slate-300 hover:text-white transition-colors"
              >
                My Cards
              </Link>
              <Link
                href="/getting-started"
                className="text-slate-300 hover:text-white transition-colors"
              >
                Getting Started
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-slate-300 text-sm">
                {user?.username}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => logout()}
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}

